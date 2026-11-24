"""Motor de voz da Kenzie: Piper neural offline, com fallback para pyttsx3."""
import os
import queue
import tempfile
import threading
from pathlib import Path


class VoiceManager:
    def __init__(self, rate=175, volume=0.95, base_dir=None, profile="TARS"):
        self.rate = int(rate)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.base_dir = Path(base_dir or Path(__file__).resolve().parent)
        self.model_path = self.base_dir / "voices" / "pt_BR-cadu-medium.onnx"
        self.enabled = True
        self.profile = str(profile or "TARS").upper()
        self._queue = queue.Queue()
        self._engine = None
        self._engine_lock = threading.RLock()
        self._generation = 0
        self._backend = None
        self._piper_voice = None
        self._thread = threading.Thread(target=self._run, daemon=True, name="KenzieVoice")
        self._thread.start()

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        if not self.enabled:
            self.stop()

    def set_profile(self, profile):
        profile = str(profile or "TARS").upper()
        if profile not in ("TARS", "CASE"):
            profile = "TARS"
        self.profile = profile

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, float(volume)))

    def speak(self, text):
        text = str(text or "").strip()
        if self.enabled and text:
            self._queue.put((text, self._generation))

    def stop(self):
        with self._engine_lock:
            self._generation += 1
            try:
                while True:
                    self._queue.get_nowait()
                    self._queue.task_done()
            except queue.Empty:
                pass
            if self._engine is not None:
                try:
                    self._engine.stop()
                except Exception:
                    pass
            if os.name == "nt":
                try:
                    import winsound
                    winsound.PlaySound(None, winsound.SND_PURGE)
                except Exception:
                    pass

    def _load_piper(self):
        if self._piper_voice is not None:
            return self._piper_voice
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"Modelo Piper não encontrado: {self.model_path}. Execute INSTALAR_VOZ_PIPER.bat."
            )
        from piper import PiperVoice
        self._piper_voice = PiperVoice.load(str(self.model_path))
        self._backend = "piper"
        print("[VOZ] Motor Piper carregado (pt-BR Cadu).")
        return self._piper_voice

    def _profile_config(self):
        # Os perfis alteram ritmo e textura da síntese, sem fingir uma troca de ator/voz.
        if self.profile == "CASE":
            return {"length_scale": 1.02, "noise_scale": 0.48, "noise_w_scale": 0.55}
        return {"length_scale": 0.96, "noise_scale": 0.58, "noise_w_scale": 0.68}

    def _speak_piper(self, text, generation):
        import wave
        import winsound
        from piper import SynthesisConfig

        voice = self._load_piper()
        config = SynthesisConfig(**self._profile_config(), volume=self.volume)
        fd, wav_path = tempfile.mkstemp(prefix="kenzie_voice_", suffix=".wav")
        os.close(fd)
        try:
            with wave.open(wav_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file, syn_config=config)
            with self._engine_lock:
                if generation != self._generation or not self.enabled:
                    return
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        finally:
            try:
                os.remove(wav_path)
            except OSError:
                pass

    def _init_fallback(self):
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", self.volume)
        try:
            for voice in engine.getProperty("voices") or []:
                description = " ".join((str(getattr(voice, "id", "")), str(getattr(voice, "name", "")), str(getattr(voice, "languages", "")))).lower()
                if any(code in description for code in ("pt-br", "pt_br", "portuguese", "brazil")):
                    engine.setProperty("voice", voice.id)
                    break
        except Exception:
            pass
        self._engine = engine
        self._backend = "pyttsx3"
        print("[VOZ] Piper indisponível; usando pyttsx3 como alternativa.")

    def _run(self):
        while True:
            item = self._queue.get()
            try:
                text, generation = item
                if not self.enabled:
                    continue
                try:
                    if os.name != "nt":
                        raise RuntimeError("A reprodução WAV desta versão está configurada para Windows.")
                    self._speak_piper(text, generation)
                except Exception as piper_error:
                    print(f"[VOZ] Piper não pôde falar: {piper_error}")
                    try:
                        if self._engine is None or self._backend != "pyttsx3":
                            self._init_fallback()
                        with self._engine_lock:
                            if generation != self._generation or not self.enabled:
                                continue
                            self._engine.say(text)
                            self._engine.runAndWait()
                    except Exception as fallback_error:
                        print(f"[VOZ] Falha também no pyttsx3: {fallback_error}")
            finally:
                self._queue.task_done()
