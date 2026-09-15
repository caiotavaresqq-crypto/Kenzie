import sys
import random
import math

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QComboBox,
)
from PySide6.QtGui import (
    QPainter,
    QRadialGradient,
    QPen,
    QBrush,
    QColor,
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread

class ProcessarMensagemWorker(QObject):
    concluido = Signal(str)
    erro = Signal(str)

    def __init__(self, mensagem):
        super().__init__()
        self.mensagem = mensagem

    def executar(self):
        try:
            from __main__ import process_command

            resposta = process_command(self.mensagem)

            self.concluido.emit(str(resposta))

        except Exception as error:
            self.erro.emit(str(error))


# ============================================================
# FUNDO ESPACIAL
# ============================================================

class SpaceBackgroundWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.estrelas = []

        for _ in range(110):

            self.estrelas.append({
                "x": random.random(),
                "y": random.random(),
                "tamanho": random.uniform(0.5, 1.8),
                "brilho": random.uniform(0.2, 0.9),
                "velocidade": random.uniform(0.003, 0.015)
            })

        self.timer = QTimer(self)
        self.timer.timeout.connect(
            self.animar_estrelas
        )
        self.timer.start(40)

    def animar_estrelas(self):

        for estrela in self.estrelas:

            estrela["brilho"] += (
                estrela["velocidade"]
            )

            if estrela["brilho"] >= 1.0:

                estrela["brilho"] = random.uniform(
                    0.2,
                    0.5
                )

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.fillRect(
            self.rect(),
            QColor("#030008")
        )

        painter.setPen(
            Qt.NoPen
        )

        for estrela in self.estrelas:

            x = (
                estrela["x"]
                * self.width()
            )

            y = (
                estrela["y"]
                * self.height()
            )

            tamanho = estrela["tamanho"]
            brilho = estrela["brilho"]

            painter.setOpacity(
                brilho
            )

            painter.setBrush(
                QColor(
                    255,
                    255,
                    255
                )
            )

            painter.drawEllipse(
                x,
                y,
                tamanho,
                tamanho
            )

        painter.setOpacity(
            1.0
        )

        painter.end()


# ============================================================
# NÚCLEO / BURACO NEGRO
# ============================================================

class BlackHoleWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(
            400,
            400
        )

        self.particulas = []

        for _ in range(120):

            angulo = random.uniform(
                0,
                2 * math.pi
            )

            raio = random.uniform(
                90,
                190
            )

            tamanho = random.uniform(
                1,
                4
            )

            self.particulas.append({
                "angulo": angulo,
                "raio": raio,
                "tamanho": tamanho,
                "brilho": random.uniform(
                    0.4,
                    1.0
                ),
                "velocidade": random.uniform(
                    0.002,
                    0.008
                ),
                "variacao_velocidade": random.uniform(
                    0.85,
                    1.15
                )
            })

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.animar
        )

        self.timer.start(16)

        self.pulsacao = 0
        self.estado = "standby"
        self.rotacao_manual = 0
        self.inclinacao = 0
        self.mouse_anterior = None
        self.zoom = 1.0
        self.velocidade_rotacao = 0
        self.intensidade_estado = 0.7

    def mudar_estado(
        self,
        estado
    ):

        self.estado = estado

    def animar(self):

        if self.estado == "standby":

            velocidade_estado = 0.5

        elif self.estado == "leve":

            velocidade_estado = 0.8

        else:

            velocidade_estado = 1.0

        if self.estado == "standby":

            intensidade_estado = 0.7

        elif self.estado == "leve":

            intensidade_estado = 0.85

        else:

            intensidade_estado = 1.0

        self.intensidade_estado = (
            intensidade_estado
        )

        for particula in self.particulas:

            particula["angulo"] += (
                particula["velocidade"]
                * particula["variacao_velocidade"]
                * velocidade_estado
                * (
                    220
                    / particula["raio"]
                )
            )

            particula[
                "variacao_velocidade"
            ] = max(
                0.8,
                min(
                    1.2,
                    particula[
                        "variacao_velocidade"
                    ]
                    + math.sin(
                        self.pulsacao * 0.3
                        + particula["angulo"]
                    ) * 0.0005
                )
            )

            particula["raio"] += (
                math.sin(
                    self.pulsacao * 0.8
                    + particula["angulo"]
                ) * 0.12
            )

            particula["tamanho"] = max(
                1,
                min(
                    4,
                    particula["tamanho"]
                    + math.sin(
                        self.pulsacao
                        + particula["angulo"]
                    ) * 0.03
                )
            )

            particula["brilho"] = (
                0.6
                + math.sin(
                    particula["angulo"] * 2
                    + self.pulsacao
                ) * 0.4
            ) * intensidade_estado

        self.update()

        self.pulsacao += (
            0.05
            * velocidade_estado
        )

        self.pulsacao += (
            0.02
            * velocidade_estado
        )

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.LeftButton:

            self.mouse_anterior = (
                event.position()
            )

    def mouseMoveEvent(
        self,
        event
    ):

        if self.mouse_anterior is not None:

            movimento_x = (
                event.position().x()
                - self.mouse_anterior.x()
            )

            movimento_y = (
                event.position().y()
                - self.mouse_anterior.y()
            )

            self.inclinacao += (
                movimento_y * 0.3
            )

            self.inclinacao = max(
                -30,
                min(
                    30,
                    self.inclinacao
                )
            )

            self.rotacao_manual += (
                movimento_x * 0.2
            )

            self.mouse_anterior = (
                event.position()
            )

            self.update()

    def mouseReleaseEvent(
        self,
        event
    ):

        if event.button() == Qt.LeftButton:

            self.mouse_anterior = None

    def wheelEvent(
        self,
        event
    ):

        movimento = (
            event.angleDelta().y()
        )

        if movimento > 0:

            self.zoom += 0.1

        else:

            self.zoom -= 0.1

        self.zoom = max(
            0.7,
            min(
                1.5,
                self.zoom
            )
        )

        self.update()

    def resetar_nucleo(self):

        self.rotacao_manual = 0
        self.inclinacao = 0
        self.zoom = 1.0

        self.update()

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setCompositionMode(
            QPainter.CompositionMode_SourceOver
        )

        painter.fillRect(
            self.rect(),
            QColor("#030008")
        )

        painter.setCompositionMode(
            QPainter.CompositionMode_Screen
        )

        centro_x = (
            self.width()
            / 2
        )

        centro_y = (
            self.height()
            / 2
        )

        escala = (
            min(
                self.width(),
                self.height()
            )
            / 500
        )

        painter.translate(
            centro_x,
            centro_y
        )

        painter.scale(
            self.zoom,
            self.zoom
        )

        painter.translate(
            -centro_x,
            -centro_y
        )

        # ----------------------------------------------------
        # AURA
        # ----------------------------------------------------

        raio_aura = (
            min(
                self.width(),
                self.height()
            ) * 0.32
            + math.sin(
                self.pulsacao
            ) * 18 * escala
        )

        gradiente = QRadialGradient(
            centro_x,
            centro_y,
            raio_aura
        )

        gradiente.setColorAt(
            0.0,
            Qt.white
        )

        gradiente.setColorAt(
            0.2,
            QColor(
                255,
                0,
                255,
                int(
                    255
                    * self.intensidade_estado
                )
            )
        )

        gradiente.setColorAt(
            0.5,
            Qt.transparent
        )

        gradiente.setColorAt(
            1.0,
            Qt.transparent
        )

        painter.setBrush(
            gradiente
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawEllipse(
            centro_x - 180 * escala,
            centro_y - 180 * escala,
            360 * escala,
            360 * escala
        )

        # ----------------------------------------------------
        # PARTÍCULAS
        # ----------------------------------------------------

        painter.setBrush(
            QBrush(Qt.magenta)
        )

        painter.setPen(
            Qt.NoPen
        )

        for particula in self.particulas:

            angulo = (
                particula["angulo"]
                + math.radians(
                    self.rotacao_manual
                )
            )

            raio = (
                particula["raio"]
            )

            raio_visual = (
                raio
                + math.sin(
                    angulo * 3
                    + self.pulsacao
                ) * 2
            )

            tamanho = (
                particula["tamanho"]
            )

            brilho = (
                particula["brilho"]
            )

            painter.setOpacity(
                brilho
            )

            x = (
                centro_x
                + math.cos(angulo)
                * raio_visual
            )

            y = (
                centro_y
                + math.sin(angulo)
                * raio
                * (
                    0.35
                    + math.sin(
                        self.pulsacao
                    ) * 0.04
                )
            )

            painter.setPen(
                QPen(
                    Qt.magenta,
                    1,
                    Qt.SolidLine
                )
            )

            painter.setOpacity(
                brilho * 0.15
            )

            painter.drawEllipse(
                x - tamanho
                * (1 + brilho),
                y - tamanho
                * (1 + brilho),
                tamanho
                * (2 + brilho * 2),
                tamanho
                * (2 + brilho * 2)
            )

            painter.drawLine(
                x,
                y,
                x
                + math.sin(angulo) * 6,
                y
                - math.cos(angulo) * 6
            )

            painter.setOpacity(
                brilho
            )

            painter.drawEllipse(
                x - tamanho / 2,
                y - tamanho / 2,
                tamanho,
                tamanho
            )

            painter.setOpacity(
                1.0
            )

        # ----------------------------------------------------
        # LINHAS ORBITAIS
        # ----------------------------------------------------

        painter.save()

        painter.translate(
            centro_x,
            centro_y
        )

        painter.rotate(
            self.pulsacao * 2
            + self.rotacao_manual
        )

        painter.scale(
            1,
            1
            - abs(
                self.inclinacao
            ) / 100
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.setPen(
            QPen(
                Qt.magenta,
                1
            )
        )

        painter.drawEllipse(
            -165 * escala,
            -62 * escala,
            330 * escala,
            124 * escala
        )

        painter.rotate(
            -self.pulsacao * 4
        )

        painter.setPen(
            QPen(
                Qt.darkMagenta,
                1
            )
        )

        painter.drawEllipse(
            -175 * escala,
            -68 * escala,
            350 * escala,
            136 * escala
        )

        painter.restore()

        # ----------------------------------------------------
        # DISCO DE ACREÇÃO
        # ----------------------------------------------------

        espessura = (
            6
            + math.sin(
                self.pulsacao * 1.5
            ) * 2.5
        )

        painter.save()

        painter.translate(
            centro_x,
            centro_y
        )

        painter.rotate(
            self.pulsacao * 0.5
            + self.rotacao_manual
        )

        painter.scale(
            1,
            1
            - abs(
                self.inclinacao
            ) / 100
        )

        painter.setPen(
            QPen(
                Qt.magenta,
                espessura
            )
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawEllipse(
            -150 * escala,
            -55 * escala,
            300 * escala,
            110 * escala
        )

        painter.restore()

        painter.save()

        painter.translate(
            centro_x,
            centro_y
        )

        painter.rotate(
            -self.pulsacao * 0.8
            + self.rotacao_manual
        )

        painter.scale(
            1,
            1
            - abs(
                self.inclinacao
            ) / 100
        )

        painter.setPen(
            QPen(
                Qt.magenta,
                3
            )
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawEllipse(
            -135 * escala,
            -42 * escala,
            270 * escala,
            84 * escala
        )

        painter.restore()

        # ----------------------------------------------------
        # BRILHO DO HORIZONTE
        # ----------------------------------------------------

        brilho = QRadialGradient(
            centro_x,
            centro_y,
            95 * escala
        )

        brilho.setColorAt(
            0.0,
            Qt.transparent
        )

        brilho.setColorAt(
            0.7,
            QColor(
                255,
                0,
                255,
                int(
                    100
                    + math.sin(
                        self.pulsacao
                    ) * 40
                )
            )
        )

        brilho.setColorAt(
            1.0,
            Qt.transparent
        )

        painter.setBrush(
            brilho
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawEllipse(
            centro_x - 95 * escala,
            centro_y - 95 * escala,
            190 * escala,
            190 * escala
        )

        painter.setCompositionMode(
            QPainter.CompositionMode_SourceOver
        )

        # ----------------------------------------------------
        # BURACO NEGRO
        # ----------------------------------------------------

        painter.setBrush(
            Qt.darkMagenta
        )

        painter.drawEllipse(
            centro_x - 78 * escala,
            centro_y - 78 * escala,
            156 * escala,
            156 * escala
        )

        painter.setBrush(
            Qt.black
        )

        painter.drawEllipse(
            centro_x - 70 * escala,
            centro_y - 70 * escala,
            140 * escala,
            140 * escala
        )

        painter.end()


# ============================================================
# INTERFACE
# ============================================================

class KenzieInterface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Kenzie"
        )

        self.resize(
            1200,
            700
        )

        self.criar_interface()

    # ========================================================
    # CHAT
    # ========================================================

    def adicionar_mensagem(
        self,
        mensagem
    ):

        self.chat.append(
            mensagem
        )

    def enviar_mensagem(self, entrada):

        mensagem = entrada.text().strip()

        if not mensagem:
            return

        self.entrada_chat = entrada

        self.chat.append(
            '<span style="color: white;">'
            '<b>Você:</b></span> '
            + mensagem
            + '<br>'
        )

        entrada.clear()

        from __main__ import detectar_ativacao

        estado = detectar_ativacao(mensagem)

        if estado == "LEVE":

            resposta = "Estou acordada."

            self.nucleo_central.mudar_estado(
                "leve"
            )

            self.estado_nucleo.setText(
                "Estado: LEVE"
            )

            self.chat.append(
                '<span style="color: magenta;">'
                '<b>Kenzie:</b></span> '
                + resposta
                + '<br>'
            )

            return

        elif estado == "COMPLETO":

            resposta = "Vamos trabalhar."

            self.nucleo_central.mudar_estado(
                "completo"
            )

            self.estado_nucleo.setText(
                "Estado: COMPLETO"
            )

            self.chat.append(
                '<span style="color: magenta;">'
                '<b>Kenzie:</b></span> '
                + resposta
                + '<br>'
            )

            return

        elif estado == "STANDBY":

            resposta = "Entrando em espera."

            self.nucleo_central.mudar_estado(
                "standby"
            )

            self.estado_nucleo.setText(
                "Estado: STANDBY"
            )

            self.chat.append(
                '<span style="color: magenta;">'
                '<b>Kenzie:</b></span> '
                + resposta
                + '<br>'
            )

            return

        # ----------------------------------------------------
        # PROCESSAMENTO EM SEGUNDO PLANO
        # ----------------------------------------------------

        entrada.setEnabled(False)

        self.thread_processamento = QThread()

        self.worker_processamento = (
            ProcessarMensagemWorker(
                mensagem
            )
        )

        self.worker_processamento.moveToThread(
            self.thread_processamento
        )

        self.thread_processamento.started.connect(
            self.worker_processamento.executar
        )

        self.worker_processamento.concluido.connect(
            self.finalizar_processamento
        )

        self.worker_processamento.erro.connect(
            self.finalizar_erro
        )

        self.worker_processamento.concluido.connect(
            self.thread_processamento.quit
        )

        self.worker_processamento.erro.connect(
            self.thread_processamento.quit
        )

        self.thread_processamento.finished.connect(
            self.worker_processamento.deleteLater
        )

        self.thread_processamento.finished.connect(
            self.thread_processamento.deleteLater
        )

        self.thread_processamento.start()

    def finalizar_processamento(self, resposta):

        self.chat.append(
            '<span style="color: magenta;">'
            '<b>Kenzie:</b></span> '
            + resposta
            + '<br>'
        )

        self.entrada_chat.setEnabled(True)
        self.entrada_chat.setFocus()

    def finalizar_erro(self, erro):

        self.chat.append(
            '<span style="color: magenta;">'
            '<b>Kenzie:</b></span> '
            'Ocorreu um erro: '
            + erro
            + '<br>'
        )

        self.entrada_chat.setEnabled(True)
        self.entrada_chat.setFocus()

    # ========================================================
    # STANDBY
    # ========================================================

    def ativar_standby(self):

        from __main__ import (
            detectar_ativacao
        )

        detectar_ativacao(
            "Kenzie, pode dormir"
        )

        self.nucleo_central.mudar_estado(
            "standby"
        )

        self.chat.append(
            '<span style="color: magenta;">'
            '<b>Kenzie:</b></span> '
            'Entrando em espera.<br>'
        )

    # ========================================================
    # BOTÕES DE AÇÃO
    # ========================================================

    def executar_acao(
        self,
        nome_ferramenta
    ):

        try:

            import __main__

            if not hasattr(
                __main__,
                "use_tool"
            ):

                self.adicionar_mensagem(
                    '<span style="color: magenta;">'
                    '<b>Kenzie:</b></span> '
                    'O sistema de ferramentas '
                    'não está disponível.<br>'
                )

                return

            use_tool = (
                __main__.use_tool
            )

            resposta = use_tool(
                nome_ferramenta
            )

            self.adicionar_mensagem(
                '<span style="color: magenta;">'
                '<b>Kenzie:</b></span> '
                + str(resposta)
                + '<br>'
            )

        except Exception as error:

            self.adicionar_mensagem(
                '<span style="color: magenta;">'
                '<b>Kenzie:</b></span> '
                'Erro ao executar ação: '
                + str(error)
                + '<br>'
            )

    def criar_botao_acao(
        self,
        texto,
        ferramenta
    ):

        botao = QPushButton(
            texto
        )

        botao.setStyleSheet("""
            QPushButton {
                color: magenta;
                background-color: #080010;
                border: 1px solid magenta;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #25002f;
            }

            QPushButton:pressed {
                background-color: #350040;
            }
        """)

        botao.clicked.connect(
            lambda: self.executar_acao(
                ferramenta
            )
        )

        return botao

    # ========================================================
    # CÓDIGO
    # ========================================================

    def limpar_codigo(self):

        self.editor_codigo.clear()

        self.status_codigo.setText(
            "Editor limpo."
        )

    def mudar_linguagem(
        self,
        linguagem
    ):

        self.status_codigo.setText(
            "Linguagem selecionada: "
            + linguagem
        )

    # ========================================================
    # ESTUDOS
    # ========================================================

    def limpar_estudos(self):

        self.tarefas_estudos.clear()

        self.status_estudos.setText(
            "Área de tarefas limpa."
        )

    def salvar_estudos(self):

        self.status_estudos.setText(
            "Anotações mantidas na sessão atual."
        )

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        central = SpaceBackgroundWidget()

        self.setCentralWidget(
            central
        )

        layout_principal = QHBoxLayout()

        central.setLayout(
            layout_principal
        )

        # ====================================================
        # MENU LATERAL
        # ====================================================

        menu = QVBoxLayout()

        menu.setSpacing(
            10
        )

        titulo = QLabel(
            "KENZIE"
        )

        titulo.setMinimumHeight(
            40
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setStyleSheet("""
            QLabel {
                color: magenta;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        botao_standby = QPushButton(
            "STANDBY"
        )

        botao_reset = QPushButton(
            "RESET NÚCLEO"
        )

        nucleo = QPushButton(
            "NÚCLEO"
        )

        conversa = QPushButton(
            "CONVERSA"
        )

        botoes_menu = [
            botao_standby,
            botao_reset,
            conversa,
        ]

        for botao in botoes_menu:

            botao.setStyleSheet("""
                QPushButton {
                    color: magenta;
                    background-color: #080010;
                    border: 1px solid magenta;
                    border-radius: 8px;
                    padding: 8px;
                }

                QPushButton:hover {
                    background-color: #25002f;
                }

                QPushButton:pressed {
                    background-color: #350040;
                }
            """)

        nucleo.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #120018;
                border: 1px solid magenta;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #25002f;
            }

            QPushButton:pressed {
                background-color: #350040;
            }
        """)

        codigo = QPushButton(
            "CÓDIGO"
        )

        estudos = QPushButton(
            "ESTUDOS"
        )

        projetos = QPushButton(
            "PROJETOS"
        )

        treinos = QPushButton(
            "TREINOS"
        )

        financas = QPushButton(
            "FINANÇAS"
        )

        configuracoes = QPushButton(
            "CONFIGURAÇÕES"
        )

        botoes_secundarios = [
            codigo,
            estudos,
            projetos,
            treinos,
            financas,
            configuracoes,
        ]

        for botao in botoes_secundarios:

            botao.setStyleSheet("""
                QPushButton {
                    color: magenta;
                    background-color: transparent;
                    border: 1px solid #5a005a;
                    border-radius: 8px;
                    padding: 8px;
                    text-align: left;
                }

                QPushButton:hover {
                    background-color: #120018;
                    border: 1px solid magenta;
                }

                QPushButton:pressed {
                    background-color: #25002f;
                }
            """)

        menu.addWidget(
            titulo
        )

        menu.addWidget(
            botao_standby
        )

        menu.addWidget(
            botao_reset
        )

        menu.addWidget(
            nucleo
        )

        menu.addWidget(
            conversa
        )

        menu.addSpacing(
            10
        )

        menu.addWidget(
            codigo
        )

        menu.addWidget(
            estudos
        )

        menu.addWidget(
            projetos
        )

        menu.addWidget(
            treinos
        )

        menu.addWidget(
            financas
        )

        menu.addWidget(
            configuracoes
        )

        menu.addStretch()

        # ====================================================
        # NÚCLEO CENTRAL
        # ====================================================

        self.nucleo_central = (
            BlackHoleWidget()
        )

        self.nucleo_central.mudar_estado(
            "completo"
        )

        botao_standby.clicked.connect(
            self.ativar_standby
        )

        botao_reset.clicked.connect(
            self.nucleo_central.resetar_nucleo
        )

        # ====================================================
        # PÁGINAS
        # ====================================================

        self.paginas = QStackedWidget()
        
        pagina_projetos = QWidget()
        layout_projetos = QVBoxLayout()
        pagina_projetos.setLayout(layout_projetos)

        titulo_projetos = QLabel("PROJETOS")
        titulo_projetos.setAlignment(Qt.AlignCenter)
        titulo_projetos.setStyleSheet("""
    QLabel {
        color: magenta;
        font-size: 24px;
        font-weight: bold;
    }
""")

        layout_projetos.addWidget(titulo_projetos)

        nome_projeto = QLineEdit()
        nome_projeto.setPlaceholderText("Nome do projeto...")

        layout_projetos.addWidget(nome_projeto)

        botao_criar_projeto = QPushButton("CRIAR PROJETO")
        layout_projetos.addWidget(botao_criar_projeto)
        
        lista_projetos = QVBoxLayout()
        layout_projetos.addLayout(lista_projetos)
        def abrir_projeto(nome):

            pagina = QWidget()
            layout = QVBoxLayout()
            pagina.setLayout(layout)

            titulo = QLabel(nome)
            titulo.setAlignment(Qt.AlignCenter)

            titulo.setStyleSheet("""
                QLabel {
                    color: magenta;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)

            layout.addWidget(titulo)
            descricao = QTextEdit()
            descricao.setPlaceholderText("Descrição do projeto...")
            layout.addWidget(descricao)
            
            botao_voltar = QPushButton("VOLTAR")
            layout.addWidget(botao_voltar)
            botao_voltar.clicked.connect(
    lambda: self.paginas.setCurrentWidget(pagina_projetos)
)

            self.paginas.addWidget(pagina)
            self.paginas.setCurrentWidget(pagina)

        def criar_projeto():

            nome = nome_projeto.text().strip()

            if nome:

                projeto = QPushButton(nome)

                projeto.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #080010;
                        border: 1px solid magenta;
                        border-radius: 8px;
                        padding: 8px;
                        text-align: left;
                    }

                    QPushButton:hover {
                        background-color: #180025;
    }
""")

                lista_projetos.addWidget(projeto)
                projeto.clicked.connect(
    lambda: abrir_projeto(nome)
)

                nome_projeto.clear()

        botao_criar_projeto.clicked.connect(
            criar_projeto
        )

        self.paginas.addWidget(
            pagina_projetos
        )

        # ====================================================
        # PÁGINA DO NÚCLEO
        # ====================================================

        pagina_nucleo = QWidget()

        layout_nucleo = QVBoxLayout()

        pagina_nucleo.setLayout(
            layout_nucleo
        )

        titulo_nucleo = QLabel(
            "NÚCLEO DA KENZIE"
        )

        titulo_nucleo.setStyleSheet("""
            QLabel {
                color: magenta;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        self.estado_nucleo = QLabel(
            "Estado: COMPLETO"
        )

        self.estado_nucleo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                padding: 5px;
            }
        """)

        layout_nucleo.addWidget(
            titulo_nucleo
        )

        layout_nucleo.addWidget(
            self.estado_nucleo
        )

        layout_nucleo.addStretch()

        self.paginas.addWidget(
            pagina_nucleo
        )

        # ====================================================
        # PÁGINA DO CHAT
        # ====================================================

        pagina_chat = QWidget()

        layout_chat = QVBoxLayout()

        pagina_chat.setLayout(
            layout_chat
        )

        self.chat = QTextEdit()

        self.chat.setReadOnly(
            True
        )

        self.chat.setPlaceholderText(
            "Conversa com a Kenzie..."
        )

        self.chat.setStyleSheet("""
            QTextEdit {
                background-color: #080010;
                color: magenta;
                border: 1px solid magenta;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        layout_chat.addWidget(
            self.chat
        )

        self.chat.append(
            '<span style="color: magenta;">'
            '<b>Kenzie:</b></span> '
            'Sistema online.<br>'
        )

        entrada = QLineEdit()

        entrada.setPlaceholderText(
    "Fale com a Kenzie..."
)

        entrada.setStyleSheet("""
    QLineEdit {
        background-color: #080010;
        color: magenta;
        border: 1px solid magenta;
        border-radius: 12px;
        padding: 10px;
    }
""")

        botao_enviar = QPushButton(
        "ENVIAR"
)

        botao_enviar.setStyleSheet("""
    QPushButton {
        color: magenta;
        background-color: #080010;
        border: 1px solid magenta;
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #25002f;
    }

    QPushButton:pressed {
        background-color: #350040;
    }
""")

        linha_entrada = QHBoxLayout()

        linha_entrada.addWidget(
        entrada
)

        linha_entrada.addWidget(
        botao_enviar
)

        layout_chat.addLayout(
        linha_entrada
)

        entrada.returnPressed.connect(
    lambda: self.enviar_mensagem(
        entrada
    )
)

        botao_enviar.clicked.connect(
    lambda: self.enviar_mensagem(
        entrada
    )
)

        # ====================================================
        # BOTÕES DE AÇÃO
        # ====================================================

        titulo_acoes = QLabel(
            "AÇÕES RÁPIDAS"
        )

        titulo_acoes.setStyleSheet("""
            QLabel {
                color: magenta;
                font-size: 16px;
                font-weight: bold;
                padding-top: 8px;
            }
        """)

        layout_chat.addWidget(
            titulo_acoes
        )

        linha_acoes_1 = QHBoxLayout()

        linha_acoes_1.addWidget(
            self.criar_botao_acao(
                "CALCULADORA",
                "calculadora"
            )
        )

        linha_acoes_1.addWidget(
            self.criar_botao_acao(
                "PAINT",
                "paint"
            )
        )

        linha_acoes_1.addWidget(
            self.criar_botao_acao(
                "NOTAS",
                "bloco_de_notas"
            )
        )

        layout_chat.addLayout(
            linha_acoes_1
        )

        linha_acoes_2 = QHBoxLayout()

        linha_acoes_2.addWidget(
            self.criar_botao_acao(
                "EXPLORADOR",
                "explorador"
            )
        )

        linha_acoes_2.addWidget(
            self.criar_botao_acao(
                "GOOGLE",
                "google"
            )
        )

        linha_acoes_2.addWidget(
            self.criar_botao_acao(
                "YOUTUBE",
                "youtube"
            )
        )

        layout_chat.addLayout(
            linha_acoes_2
        )

        # ====================================================
        # OUTRAS ÁREAS
        # ====================================================

        agenda = QLabel(
            "AGENDA"
        )

        tarefas = QLabel(
            "TAREFAS DO DIA"
        )

        anotacoes = QLabel(
            "ANOTAÇÕES RÁPIDAS"
        )

        for label in [
            agenda,
            tarefas,
            anotacoes,
        ]:

            label.setStyleSheet("""
                QLabel {
                    color: white;
                    padding: 5px;
                }
            """)

        layout_chat.addWidget(
            agenda
        )

        layout_chat.addWidget(
            tarefas
        )

        layout_chat.addWidget(
            anotacoes
        )

        self.paginas.insertWidget(
            0,
            pagina_chat
        )

        self.paginas.setCurrentWidget(
            pagina_chat
        )

        # ====================================================
        # PÁGINA DE CÓDIGO
        # ====================================================

        pagina_codigo = QWidget()

        layout_codigo = QVBoxLayout()

        pagina_codigo.setLayout(
            layout_codigo
        )

        titulo_codigo = QLabel(
            "AMBIENTE DE CÓDIGO"
        )

        titulo_codigo.setStyleSheet("""
            QLabel {
                color: magenta;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout_codigo.addWidget(
            titulo_codigo
        )

        barra_codigo = QHBoxLayout()

        label_linguagem = QLabel(
            "LINGUAGEM:"
        )

        label_linguagem.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)

        self.seletor_linguagem = QComboBox()

        self.seletor_linguagem.addItems([
            "Python",
            "Java",
            "HTML"
        ])

        self.seletor_linguagem.setStyleSheet("""
            QComboBox {
                color: magenta;
                background-color: #080010;
                border: 1px solid magenta;
                border-radius: 8px;
                padding: 6px;
            }

            QComboBox QAbstractItemView {
                color: magenta;
                background-color: #080010;
                selection-background-color: #25002f;
            }
        """)

        botao_limpar_codigo = QPushButton(
            "LIMPAR"
        )

        botao_limpar_codigo.setStyleSheet("""
            QPushButton {
                color: magenta;
                background-color: #080010;
                border: 1px solid magenta;
                border-radius: 8px;
                padding: 7px 14px;
            }

            QPushButton:hover {
                background-color: #25002f;
            }

            QPushButton:pressed {
                background-color: #350040;
            }
        """)

        barra_codigo.addWidget(
            label_linguagem
        )

        barra_codigo.addWidget(
            self.seletor_linguagem
        )

        barra_codigo.addStretch()

        barra_codigo.addWidget(
            botao_limpar_codigo
        )

        layout_codigo.addLayout(
            barra_codigo
        )

        self.editor_codigo = QTextEdit()

        self.editor_codigo.setPlaceholderText(
            "Escreva seu código aqui..."
        )

        self.editor_codigo.setStyleSheet("""
            QTextEdit {
                background-color: #050008;
                color: #eeeeee;
                border: 1px solid magenta;
                border-radius: 10px;
                padding: 12px;
                font-family: Consolas;
                font-size: 14px;
            }
        """)

        layout_codigo.addWidget(
            self.editor_codigo
        )

        self.status_codigo = QLabel(
            "Editor pronto."
        )

        self.status_codigo.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                padding: 4px;
            }
        """)

        layout_codigo.addWidget(
            self.status_codigo
        )

        botao_limpar_codigo.clicked.connect(
            self.limpar_codigo
        )

        self.seletor_linguagem.currentTextChanged.connect(
            self.mudar_linguagem
        )

        self.paginas.addWidget(
            pagina_codigo
        )

        # ====================================================
        # PÁGINA DE ESTUDOS
        # ====================================================

        pagina_estudos = QWidget()

        layout_estudos = QVBoxLayout()

        pagina_estudos.setLayout(
            layout_estudos
        )

        titulo_estudos = QLabel(
            "CENTRO DE ESTUDOS"
        )

        titulo_estudos.setStyleSheet("""
            QLabel {
                color: magenta;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout_estudos.addWidget(
            titulo_estudos
        )

        descricao_estudos = QLabel(
            "Organização acadêmica da Kenzie"
        )

        descricao_estudos.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 14px;
                padding-bottom: 10px;
            }
        """)

        layout_estudos.addWidget(
            descricao_estudos
        )

        # ----------------------------------------------------
        # MATÉRIAS
        # ----------------------------------------------------

        titulo_materias = QLabel(
            "MATÉRIAS"
        )

        titulo_materias.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 17px;
                font-weight: bold;
            }
        """)

        layout_estudos.addWidget(
            titulo_materias
        )

        materias = [
            "Programação",
            "Química",
            "História",
            "Filosofia",
            "Sistemas Operacionais",
        ]

        for materia in materias:

            item = QLabel(
                "• " + materia
            )

            item.setStyleSheet("""
                QLabel {
                    color: #dddddd;
                    background-color: #080010;
                    border: 1px solid #350035;
                    border-radius: 6px;
                    padding: 8px;
                }
            """)

            layout_estudos.addWidget(
                item
            )

        # ----------------------------------------------------
        # TAREFAS
        # ----------------------------------------------------

        titulo_tarefas_estudos = QLabel(
            "PRÓXIMAS TAREFAS"
        )

        titulo_tarefas_estudos.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 17px;
                font-weight: bold;
                padding-top: 12px;
            }
        """)

        layout_estudos.addWidget(
            titulo_tarefas_estudos
        )

        self.tarefas_estudos = QTextEdit()

        self.tarefas_estudos.setPlaceholderText(
            "Digite aqui suas tarefas, trabalhos "
            "ou conteúdos para estudar..."
        )

        self.tarefas_estudos.setStyleSheet("""
            QTextEdit {
                background-color: #080010;
                color: white;
                border: 1px solid magenta;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout_estudos.addWidget(
            self.tarefas_estudos
        )

        # ----------------------------------------------------
        # BOTÕES DE ESTUDOS
        # ----------------------------------------------------

        linha_estudos = QHBoxLayout()

        botao_salvar_estudos = QPushButton(
            "SALVAR"
        )

        botao_limpar_estudos = QPushButton(
            "LIMPAR"
        )

        for botao in [
            botao_salvar_estudos,
            botao_limpar_estudos,
        ]:

            botao.setStyleSheet("""
                QPushButton {
                    color: magenta;
                    background-color: #080010;
                    border: 1px solid magenta;
                    border-radius: 8px;
                    padding: 8px 15px;
                }

                QPushButton:hover {
                    background-color: #25002f;
                }

                QPushButton:pressed {
                    background-color: #350040;
                }
            """)

        linha_estudos.addWidget(
            botao_salvar_estudos
        )

        linha_estudos.addWidget(
            botao_limpar_estudos
        )

        layout_estudos.addLayout(
            linha_estudos
        )

        self.status_estudos = QLabel(
            "Sistema de estudos pronto."
        )

        self.status_estudos.setStyleSheet("""
            QLabel {
                color: #888888;
                padding-top: 5px;
            }
        """)

        layout_estudos.addWidget(
            self.status_estudos
        )

        botao_limpar_estudos.clicked.connect(
            self.limpar_estudos
        )

        botao_salvar_estudos.clicked.connect(
            self.salvar_estudos
        )

        self.paginas.addWidget(
            pagina_estudos
        )

        # ====================================================
        # NAVEGAÇÃO
        # ====================================================

        nucleo.clicked.connect(
            lambda: self.paginas.setCurrentWidget(
                pagina_nucleo
            )
        )

        conversa.clicked.connect(
            lambda: self.paginas.setCurrentWidget(
                pagina_chat
            )
        )

        codigo.clicked.connect(
            lambda: self.paginas.setCurrentWidget(
                pagina_codigo
            )
        )

        estudos.clicked.connect(
            lambda: self.paginas.setCurrentWidget(
                pagina_estudos
            )
        )
        projetos.clicked.connect(
            lambda: self.paginas.setCurrentWidget(
                pagina_projetos
            )
        )

        # ====================================================
        # LAYOUT FINAL
        # ====================================================

        layout_principal.addLayout(
            menu,
            1
        )

        layout_principal.addWidget(
            self.nucleo_central,
            3
        )

        layout_principal.addWidget(
            self.paginas,
            2
        )


# ============================================================
# INICIAR
# ============================================================

def iniciar_interface():

    app = QApplication(
        sys.argv
    )

    janela = KenzieInterface()

    janela.show()

    app.exec()


if __name__ == "__main__":
    iniciar_interface()