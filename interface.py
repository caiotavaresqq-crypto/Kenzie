import os
import json
import math
import random
import threading
from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QThread,
    QObject,
    Signal,
    QTimer,
    QPointF,
    QRectF,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QFont,
    QLinearGradient,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QMessageBox,
)


# ============================================================
# CORES / CONSTANTES VISUAIS
# ============================================================

FUNDO = "#020006"
FUNDO_CARD = "#06000f"
FUNDO_CARD_2 = "#080014"
MAGENTA = "#ff00ff"
ROXO = "#8b2cff"
ROXO_CLARO = "#b85cff"
BRANCO = "#f5edff"
CINZA = "#aaa0bd"
LINHA = "#35105a"


# ============================================================
# UTILITÁRIOS
# ============================================================

def carregar_json(nome, padrao):
    try:
        if os.path.exists(nome):
            with open(nome, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
    except Exception:
        pass

    return padrao


def salvar_json(nome, dados):
    try:
        with open(nome, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    except Exception:
        pass


# ============================================================
# WORKER DA CONVERSA
# ============================================================

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

        except Exception as erro:
            self.erro.emit(str(erro))


# ============================================================
# NÚCLEO CENTRAL
# ============================================================

class BlackHoleWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.estado = "completo"
        self.pulsacao = 0.0
        self.rotacao = 0.0
        self.zoom = 1.0
        self.mouse_anterior = None

        self.particulas = []

        random.seed(42)

        for _ in range(150):
            self.particulas.append({
                "angulo": random.uniform(0, math.tau),
                "raio": random.uniform(110, 310),
                "velocidade": random.uniform(0.001, 0.006),
                "tamanho": random.uniform(1, 3),
                "brilho": random.uniform(0.3, 1.0),
            })

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animar)
        self.timer.start(16)

        self.setMinimumSize(420, 420)

    def mudar_estado(self, estado):
        self.estado = estado.lower()
        self.update()

    def animar(self):
        self.pulsacao += 0.045
        self.rotacao += 0.003

        for particula in self.particulas:
            particula["angulo"] += particula["velocidade"]

        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        if delta > 0:
            self.zoom = min(1.18, self.zoom + 0.03)
        else:
            self.zoom = max(0.88, self.zoom - 0.03)

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_anterior = event.position()

    def mouseMoveEvent(self, event):
        if self.mouse_anterior is not None:
            deslocamento = event.position() - self.mouse_anterior
            self.rotacao += deslocamento.x() * 0.003
            self.mouse_anterior = event.position()
            self.update()

    def mouseReleaseEvent(self, event):
        self.mouse_anterior = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        centro = QPointF(w / 2, h / 2 - 5)

        # Fundo transparente
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Campo estelar
        for particula in self.particulas:
            angulo = particula["angulo"] + self.rotacao
            raio = particula["raio"] * self.zoom

            x = centro.x() + math.cos(angulo) * raio
            y = centro.y() + math.sin(angulo) * raio * 0.55

            if x < -10 or x > w + 10 or y < -10 or y > h + 10:
                continue

            alpha = int(100 + 120 * particula["brilho"])

            painter.setPen(
                QPen(QColor(255, 0, 255, alpha),
                     max(1, int(particula["tamanho"])))
            )
            painter.drawPoint(QPointF(x, y))

        # Órbitas
        for i, escala in enumerate((1.0, 1.22, 1.48)):
            rect = QRectF(
                centro.x() - 210 * escala * self.zoom,
                centro.y() - 92 * escala * self.zoom,
                420 * escala * self.zoom,
                184 * escala * self.zoom,
            )

            pen = QPen(QColor(155, 25, 255, 75 - i * 15), 1.2)
            painter.setPen(pen)
            painter.drawEllipse(rect)

        # Brilho externo
        brilho = QRadialGradient(centro, 180 * self.zoom)
        brilho.setColorAt(0.0, QColor(255, 0, 255, 70))
        brilho.setColorAt(0.35, QColor(155, 0, 255, 35))
        brilho.setColorAt(0.72, QColor(80, 0, 150, 15))
        brilho.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(brilho))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            QRectF(
                centro.x() - 180 * self.zoom,
                centro.y() - 180 * self.zoom,
                360 * self.zoom,
                360 * self.zoom,
            )
        )

        # Anel luminoso
        raio = 115 * self.zoom + math.sin(self.pulsacao) * 3

        painter.setBrush(Qt.NoBrush)

        for espessura, alpha in ((12, 18), (7, 45), (3, 220)):
            painter.setPen(
                QPen(
                    QColor(255, 0, 255, alpha),
                    espessura,
                )
            )
            painter.drawEllipse(
                QRectF(
                    centro.x() - raio,
                    centro.y() - raio * 0.42,
                    raio * 2,
                    raio * 0.84,
                )
            )

        # Disco central
        disco = QRadialGradient(centro, raio * 0.9)
        disco.setColorAt(0.0, QColor(0, 0, 0, 255))
        disco.setColorAt(0.65, QColor(0, 0, 0, 255))
        disco.setColorAt(0.85, QColor(18, 0, 25, 255))
        disco.setColorAt(1.0, QColor(125, 0, 150, 180))

        painter.setBrush(QBrush(disco))
        painter.setPen(QPen(QColor(255, 0, 255, 150), 2))

        painter.drawEllipse(
            QRectF(
                centro.x() - raio * 0.63,
                centro.y() - raio * 0.63,
                raio * 1.26,
                raio * 1.26,
            )
        )


# ============================================================
# WIDGETS VISUAIS
# ============================================================

class Card(QFrame):

    def __init__(
        self,
        titulo,
        conteudo="",
        botao=None,
        parent=None,
        largura=None,
        altura=None,
    ):
        super().__init__(parent)

        self.setObjectName("Card")

        if largura:
            self.setMinimumWidth(largura)

        if altura:
            self.setMinimumHeight(altura)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)

        self.titulo = QLabel(titulo)
        self.titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 15px;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.titulo)

        linha = QFrame()
        linha.setFixedHeight(1)
        linha.setStyleSheet("background-color: #35105a;")
        layout.addWidget(linha)

        self.conteudo = QLabel(conteudo)
        self.conteudo.setWordWrap(True)
        self.conteudo.setStyleSheet("""
            QLabel {
                color: #eee6f5;
                font-size: 13px;
            }
        """)

        layout.addWidget(self.conteudo)

        if botao:
            self.botao = QPushButton(botao)
            self.botao.setMinimumHeight(34)
            layout.addWidget(self.botao)

        self.setStyleSheet("""
            QFrame#Card {
                background-color: rgba(6, 0, 15, 235);
                border: 1px solid #4d0870;
                border-radius: 18px;
            }

            QFrame#Card:hover {
                border: 1px solid #ff00ff;
            }

            QPushButton {
                color: #eee6ff;
                background-color: #080019;
                border: 1px solid #3e1461;
                border-radius: 14px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                border: 1px solid #ff00ff;
            }
        """)


class ProgressBar(QWidget):

    def __init__(self, valor=0.5, parent=None):
        super().__init__(parent)

        self.valor = valor
        self.setFixedHeight(9)

    def setValue(self, valor):
        self.valor = max(0.0, min(1.0, valor))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(0, 1, self.width(), 7)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#150d2b"))
        painter.drawRoundedRect(rect, 4, 4)

        preenchido = QRectF(
            0,
            1,
            self.width() * self.valor,
            7,
        )

        gradiente = QLinearGradient(
            0, 0,
            self.width(), 0
        )

        gradiente.setColorAt(0, QColor("#6d22ff"))
        gradiente.setColorAt(1, QColor("#ff00ff"))

        painter.setBrush(QBrush(gradiente))
        painter.drawRoundedRect(preenchido, 4, 4)


class StatCard(QFrame):

    def __init__(self, titulo, texto, parent=None):
        super().__init__(parent)

        self.setObjectName("StatCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 11, 14, 11)
        layout.setSpacing(4)

        titulo_widget = QLabel(titulo)
        titulo_widget.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        texto_widget = QLabel(texto)
        texto_widget.setWordWrap(True)
        texto_widget.setStyleSheet("""
            QLabel {
                color: #e8dff0;
                font-size: 12px;
            }
        """)

        layout.addWidget(titulo_widget)
        layout.addWidget(texto_widget)

        self.setStyleSheet("""
            QFrame#StatCard {
                background-color: #06000f;
                border: 1px solid #4d0870;
                border-radius: 14px;
            }
        """)


# ============================================================
# KENZIE INTERFACE
# ============================================================

class KenzieInterface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kenzie")
        self.resize(1500, 920)
        self.setMinimumSize(1200, 760)

        self.projetos = carregar_json(
            "kenzie_projetos.json",
            {}
        )

        self.treinos = carregar_json(
            "kenzie_treinos.json",
            {}
        )

        self.financas = carregar_json(
            "kenzie_financas.json",
            {}
        )

        self.paginas = QStackedPages(self)

        self.estado_atual = "COMPLETO"

        self.setStyleSheet("""
            QMainWindow {
                background-color: #020006;
            }

            QWidget {
                color: #f5edff;
                font-family: "Segoe UI";
            }

            QScrollBar:vertical {
                background: #030008;
                width: 8px;
            }

            QScrollBar::handle:vertical {
                background: #35105a;
                border-radius: 4px;
            }

            QLineEdit, QTextEdit {
                color: white;
                background-color: #06000f;
                border: 1px solid #4d0870;
                border-radius: 14px;
                padding: 9px 12px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #ff00ff;
            }

            QPushButton {
                color: #f5edff;
                background-color: #070012;
                border: 1px solid #46105f;
                border-radius: 12px;
                padding: 8px 14px;
            }

            QPushButton:hover {
                border: 1px solid #ff00ff;
            }
        """)

        self.criar_interface()

    # ========================================================
    # ESTRUTURA PRINCIPAL
    # ========================================================

    def criar_interface(self):

        raiz = QWidget()
        self.setCentralWidget(raiz)

        layout_principal = QVBoxLayout(raiz)
        layout_principal.setContentsMargins(10, 10, 10, 10)
        layout_principal.setSpacing(8)

        area_superior = QHBoxLayout()
        area_superior.setSpacing(12)

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        sidebar = self.criar_sidebar()
        area_superior.addWidget(sidebar, 0)

        # ----------------------------------------------------
        # CENTRO
        # ----------------------------------------------------

        centro = QWidget()
        layout_centro = QVBoxLayout(centro)
        layout_centro.setContentsMargins(10, 0, 0, 0)
        layout_centro.setSpacing(8)

        topo = self.criar_topo()
        layout_centro.addWidget(topo, 0)

        self.paginas = QStackedPages(self)

        self.pagina_nucleo = self.criar_pagina_nucleo()
        self.pagina_conversa = self.criar_pagina_conversa()
        self.pagina_codigo = self.criar_pagina_codigo()
        self.pagina_estudos = self.criar_pagina_generica(
            "ESTUDOS",
            "Área de aprendizado e acompanhamento."
        )
        self.pagina_projetos = self.criar_pagina_projetos()
        self.pagina_treinos = self.criar_pagina_treinos()
        self.pagina_financas = self.criar_pagina_financas()
        self.pagina_saude = self.criar_pagina_generica(
            "SAÚDE",
            "Acompanhamento pessoal e bem-estar."
        )
        self.pagina_configuracoes = self.criar_pagina_configuracoes()

        self.paginas.addWidget(self.pagina_nucleo)
        self.paginas.addWidget(self.pagina_conversa)
        self.paginas.addWidget(self.pagina_codigo)
        self.paginas.addWidget(self.pagina_estudos)
        self.paginas.addWidget(self.pagina_projetos)
        self.paginas.addWidget(self.pagina_treinos)
        self.paginas.addWidget(self.pagina_financas)
        self.paginas.addWidget(self.pagina_saude)
        self.paginas.addWidget(self.pagina_configuracoes)

        layout_centro.addWidget(self.paginas, 1)

        area_superior.addWidget(centro, 1)

        # ----------------------------------------------------
        # PAINEL DIREITO
        # ----------------------------------------------------

        painel_direito = self.criar_painel_direito()
        area_superior.addWidget(painel_direito, 0)

        layout_principal.addLayout(area_superior, 1)

        # ----------------------------------------------------
        # BARRA DE CONVERSA INFERIOR
        # ----------------------------------------------------

        barra_conversa = self.criar_barra_conversa()
        layout_principal.addWidget(barra_conversa, 0)

    # ========================================================
    # SIDEBAR
    # ========================================================

    def criar_sidebar(self):

        frame = QFrame()
        frame.setFixedWidth(255)
        frame.setObjectName("Sidebar")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 20, 15, 18)
        layout.setSpacing(7)

        logo = QLabel("KENZIE")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 25px;
                font-weight: bold;
                letter-spacing: 2px;
                padding: 8px;
            }
        """)

        subtitulo = QLabel("AI ASSISTANT")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("""
            QLabel {
                color: #aaa0bd;
                font-size: 10px;
                letter-spacing: 3px;
            }
        """)

        layout.addWidget(logo)
        layout.addWidget(subtitulo)
        layout.addSpacing(20)

        itens = [
            ("⌂", "NÚCLEO", 0),
            ("⌁", "CONVERSA", 1),
            ("</>", "CÓDIGO", 2),
            ("▣", "ESTUDOS", 3),
            ("□", "PROJETOS", 4),
            ("♢", "TREINOS", 5),
            ("$", "FINANÇAS", 6),
            ("♡", "SAÚDE", 7),
            ("⚙", "CONFIGURAÇÕES", 8),
        ]

        self.botoes_menu = []

        for icone, texto, indice in itens:

            botao = QPushButton()

            botao.setText(f"{icone}   {texto}")
            botao.setMinimumHeight(46)
            botao.setCursor(Qt.PointingHandCursor)

            botao.setStyleSheet("""
                QPushButton {
                    color: #eee6f5;
                    background-color: transparent;
                    border: none;
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 12px;
                    font-size: 12px;
                }

                QPushButton:hover {
                    color: #ff00ff;
                    background-color: #0c0018;
                }
            """)

            botao.clicked.connect(
                lambda checked=False, i=indice:
                self.ir_para_pagina(i)
            )

            layout.addWidget(botao)
            self.botoes_menu.append(botao)

        layout.addStretch()

        estado = QFrame()
        estado.setObjectName("EstadoSistema")

        estado_layout = QVBoxLayout(estado)
        estado_layout.setContentsMargins(16, 15, 16, 15)
        estado_layout.setSpacing(9)

        titulo = QLabel("ESTADO DO SISTEMA")
        titulo.setStyleSheet("""
            QLabel {
                color: #aaa0bd;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        self.desempenho = QLabel("82%")
        self.desempenho.setStyleSheet("""
            QLabel {
                color: #f5edff;
                font-size: 29px;
                font-weight: bold;
            }
        """)

        sincronizado = QLabel("●  SINCRONIZADO")
        sincronizado.setStyleSheet("""
            QLabel {
                color: #00ffb3;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        descricao = QLabel(
            "Todos os sistemas operacionais\n"
            "online."
        )

        descricao.setStyleSheet("""
            QLabel {
                color: #aaa0bd;
                font-size: 10px;
            }
        """)

        estado_layout.addWidget(titulo)
        estado_layout.addSpacing(5)
        estado_layout.addWidget(self.desempenho)
        estado_layout.addWidget(sincronizado)
        estado_layout.addWidget(descricao)

        frame_estado = QFrame()
        frame_estado.setLayout(estado_layout)

        layout.addWidget(frame_estado)

        frame.setStyleSheet("""
            QFrame#Sidebar {
                background-color: #030008;
                border: 1px solid #4d0870;
                border-radius: 20px;
            }

            QFrame#EstadoSistema {
                background-color: #05000c;
                border: 1px solid #35105a;
                border-radius: 18px;
            }
        """)

        return frame

    # ========================================================
    # TOPO
    # ========================================================

    def criar_topo(self):

        frame = QWidget()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 2, 8, 2)

        saudacao = QLabel(
            "Olá, <span style='color:#ff00ff;'>Caio.</span>"
        )

        saudacao.setTextFormat(Qt.RichText)

        saudacao.setStyleSheet("""
            QLabel {
                color: #f5edff;
                font-size: 24px;
                font-weight: 500;
            }
        """)

        saudacao.setTextFormat(Qt.RichText)
        saudacao.setStyleSheet("""
            QLabel {
                color: #f5edff;
                font-size: 24px;
                font-weight: 500;
            }
        """)

        layout.addWidget(saudacao)

        layout.addStretch()

        data = datetime.now()

        data_label = QLabel(
            f"<b>{data.strftime('%H:%M')}</b><br>"
            f"<span style='font-size:11px;'>"
            f"{data.strftime('%d %b %Y').upper()}<br>"
            f"{data.strftime('%A').upper()}"
            f"</span>"
        )

        data_label.setTextFormat(Qt.RichText)
        data_label.setAlignment(Qt.AlignCenter)
        data_label.setStyleSheet("""
            QLabel {
                color: #eee6f5;
                font-size: 22px;
            }
        """)

        layout.addWidget(data_label)

        layout.addStretch()

        energia = QFrame()
        energia.setObjectName("Energia")

        energia_layout = QVBoxLayout(energia)
        energia_layout.setContentsMargins(14, 7, 14, 7)

        texto_energia = QLabel("⚡  ENERGIA   78%")
        texto_energia.setStyleSheet("""
            QLabel {
                color: #eee6f5;
                font-size: 10px;
            }
        """)

        barra = ProgressBar(0.78)

        energia_layout.addWidget(texto_energia)
        energia_layout.addWidget(barra)

        energia.setStyleSheet("""
            QFrame#Energia {
                background-color: #05000c;
                border: 1px solid #35105a;
                border-radius: 14px;
            }
        """)

        layout.addWidget(energia)

        sino = QLabel("●")
        sino.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 20px;
                padding: 10px;
            }
        """)

        layout.addWidget(sino)

        return frame

    # ========================================================
    # PÁGINA DO NÚCLEO
    # ========================================================

    def criar_pagina_nucleo(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        titulo = QLabel("NÚCLEO CENTRAL")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 22px;
                font-weight: bold;
                padding-left: 3px;
            }
        """)

        layout.addWidget(titulo)

        area = QWidget()
        area_layout = QGridLayout(area)
        area_layout.setContentsMargins(0, 0, 0, 0)
        area_layout.setSpacing(8)

        # Card Código
        codigo = Card(
            "⌁  CÓDIGO",
            "Python • Java • HTML\n\n"
            "Projetos ativos                         2\n"
            "Linhas de código                  4.215",
            "ABRIR",
        )
        codigo.botao.clicked.connect(
    lambda: self.ir_para_pagina(2)
)

        # Card Estudos
        estudos = Card(
            "▣  ESTUDOS",
            "Química • História • SO\n\n"
            "Próxima prova\n"
            "Mitose e Meiose                 01 DIA",
            "VER PLANO",
        )
        estudos.botao.clicked.connect(
    lambda: self.ir_para_pagina(3)
)

        # Card Treinos
        treinos = Card(
            "♢  TREINOS",
            "Vôlei • Praia\n\n"
            "Próximo treino\n"
            "Amanhã • 18:20",
            "VER PLANO",
        )
        treinos.botao.clicked.connect(
    lambda: self.ir_para_pagina(5)
)

        # Card Projetos
        projetos = Card(
            "□  PROJETOS",
            "Kenzie.py\n\n"
            "Status\n"
            "Em desenvolvimento",
            "CONTINUAR",
        )
        projetos.botao.clicked.connect(
    lambda: self.ir_para_pagina(4)
)

        # Card Finanças
        financas = Card(
            "$  FINANÇAS",
            "Meta mensal\n"
            "R$200 / R$200\n",
            "VER DETALHES",
        )
        financas.botao.clicked.connect(
    lambda: self.ir_para_pagina(6)
)

        barra_financas = ProgressBar(1.0)
        financas.layout().insertWidget(
            financas.layout().count() - 1,
            barra_financas
        )

        # Card Saúde
        saude = Card(
            "♡  SAÚDE",
            "Sono                                  7h 10m\n\n"
            "Hidratação                         1,6 L / 3,0 L",
            "VER MAIS",
        )
        saude.botao.clicked.connect(
    lambda: self.ir_para_pagina(7)
)

        # Núcleo
        self.nucleo_central = BlackHoleWidget()

        self.estado_nucleo = QLabel(
            "Estado: COMPLETO"
        )

        self.estado_nucleo.setAlignment(Qt.AlignCenter)
        self.estado_nucleo.setStyleSheet("""
            QLabel {
                color: #eee6f5;
                font-size: 11px;
                background-color: #05000c;
                border: 1px solid #35105a;
                border-radius: 12px;
                padding: 7px 12px;
            }
        """)

        self.atividade_nucleo = QLabel(
            "Atividade: AGUARDANDO"
        )

        self.atividade_nucleo.setAlignment(Qt.AlignCenter)
        self.atividade_nucleo.setStyleSheet("""
            QLabel {
                color: #aaa0bd;
                font-size: 11px;
            }
        """)

        centro_nucleo = QVBoxLayout()
        centro_nucleo.setContentsMargins(0, 0, 0, 0)
        centro_nucleo.addWidget(
            self.nucleo_central,
            1
        )
        centro_nucleo.addWidget(
            self.estado_nucleo,
            0,
            Qt.AlignCenter
        )
        centro_nucleo.addWidget(
            self.atividade_nucleo,
            0,
            Qt.AlignCenter
        )

        centro_widget = QWidget()
        centro_widget.setLayout(centro_nucleo)

        area_layout.addWidget(codigo, 0, 0)
        area_layout.addWidget(estudos, 0, 2)

        area_layout.addWidget(treinos, 1, 0)
        area_layout.addWidget(projetos, 1, 2)

        area_layout.addWidget(financas, 2, 0)
        area_layout.addWidget(saude, 2, 2)

        # O núcleo ocupa as três linhas centrais.
        # Isso mantém o buraco negro realmente centralizado
        # entre os cards superiores e inferiores.
        area_layout.addWidget(
            centro_widget,
            0, 1, 3, 1
        )

        area_layout.setColumnStretch(0, 1)
        area_layout.setColumnStretch(1, 2)
        area_layout.setColumnStretch(2, 1)

        area_layout.setRowStretch(0, 1)
        area_layout.setRowStretch(1, 1)
        area_layout.setRowStretch(2, 1)

        layout.addWidget(area, 1)

        frase = QLabel(
            "FOCO   •   DISCIPLINA   •   EVOLUÇÃO"
        )

        frase.setAlignment(Qt.AlignCenter)
        frase.setStyleSheet("""
            QLabel {
                color: #9c6aff;
                font-size: 10px;
                letter-spacing: 2px;
                padding: 4px;
            }
        """)

        layout.addWidget(frase)

        diagnostico = QPushButton(
            "EXECUTAR DIAGNÓSTICO"
        )

        diagnostico.clicked.connect(
            self.executar_diagnostico
        )

        diagnostico.setMinimumHeight(35)

        layout.addWidget(diagnostico)

        return pagina

    # ========================================================
    # PAINEL DIREITO
    # ========================================================

    def criar_painel_direito(self):

        painel = QFrame()
        painel.setFixedWidth(305)
        painel.setObjectName("PainelDireito")

        layout = QVBoxLayout(painel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        titulo = QLabel("AGENDA")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 17px;
                font-weight: bold;
            }
        """)

        agenda = Card(
            "AGENDA",
            "10:40     IFPA - Aula\n\n"
            "18:20     Treino de Vôlei\n\n"
            "20:30     Estudos / Projetos\n\n"
            "22:30     Revisão do dia",
            "VER AGENDA COMPLETA",
        )

        tarefas = Card(
            "TAREFAS DO DIA",
            "●  Estudar Mitose e Meiose\n\n"
            "●  Projeto Kenzie.py\n\n"
            "●  Treino de Vôlei\n\n"
            "○  Revisar Química\n\n"
            "3 / 4 concluídas",
        )

        barra_tarefas = ProgressBar(0.75)

        tarefas.layout().addWidget(
            barra_tarefas
        )

        anotacoes = Card(
            "ANOTAÇÕES RÁPIDAS",
            "Tenha paciência no processo.\n"
            "O difícil hoje é o fácil amanhã.\n"
            "Confia no núcleo.",
            "NOVA ANOTAÇÃO",
        )

        foco = QFrame()
        foco.setObjectName("Foco")

        foco_layout = QHBoxLayout(foco)
        foco_layout.setContentsMargins(14, 10, 14, 10)

        foco_texto = QLabel(
            "◉  MODO FOCO\n"
            "<span style='color:#aaa0bd;'>ATIVADO</span>"
        )

        foco_texto.setTextFormat(Qt.RichText)

        foco_layout.addWidget(foco_texto)
        foco_layout.addStretch()

        toggle = QLabel("●")
        toggle.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 20px;
            }
        """)

        foco_layout.addWidget(toggle)

        foco.setStyleSheet("""
            QFrame#Foco {
                background-color: #05000c;
                border: 1px solid #35105a;
                border-radius: 15px;
            }
        """)

        layout.addWidget(agenda)
        layout.addWidget(tarefas)
        layout.addWidget(anotacoes)
        layout.addStretch()
        layout.addWidget(foco)

        painel.setStyleSheet("""
            QFrame#PainelDireito {
                background-color: transparent;
                border: none;
            }
        """)

        return painel

    # ========================================================
    # BARRA DE CONVERSA
    # ========================================================

    def criar_barra_conversa(self):

        frame = QFrame()
        frame.setObjectName("BarraConversa")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 9, 14, 9)
        layout.setSpacing(8)

        icone = QLabel("✦")
        icone.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 23px;
            }
        """)

        layout.addWidget(icone)

        self.entrada_chat = QLineEdit()
        self.entrada_chat.setPlaceholderText(
            "Como posso te ajudar hoje, Caio?"
        )

        self.entrada_chat.returnPressed.connect(
            self.enviar_mensagem
        )

        self.entrada_chat.setMinimumHeight(42)

        layout.addWidget(
            self.entrada_chat,
            1
        )

        enviar = QPushButton("➤")
        enviar.setFixedSize(44, 42)

        enviar.clicked.connect(
            self.enviar_mensagem
        )

        layout.addWidget(enviar)

        frame.setStyleSheet("""
            QFrame#BarraConversa {
                background-color: #04000a;
                border: 1px solid #4d0870;
                border-radius: 24px;
            }
        """)

        return frame

    # ========================================================
    # CONVERSA
    # ========================================================

    def criar_pagina_conversa(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)

        titulo = QLabel("CONVERSA")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout.addWidget(titulo)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.chat.clear()

        layout.addWidget(
            self.chat,
            1
        )

        return pagina

    # ========================================================
    # PÁGINAS GENÉRICAS
    # ========================================================
    
    
    def criar_pagina_generica(self, titulo, descricao):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        titulo_widget = QLabel(titulo)
        titulo_widget.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        descricao_widget = QLabel(descricao)
        descricao_widget.setWordWrap(True)
        descricao_widget.setStyleSheet("""
            QLabel {
                color: #aaa0bd;
                font-size: 13px;
            }
        """)

        layout.addWidget(titulo_widget)
        layout.addWidget(descricao_widget)
        layout.addStretch()

        return pagina

    # ========================================================
    # PÁGINA DE CÓDIGO
    # ========================================================

    def criar_pagina_codigo(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        titulo = QLabel("CÓDIGO")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        subtitulo = QLabel(
            "Ambiente de desenvolvimento • Python • Java • HTML"
        )

        subtitulo.setStyleSheet("""
            QLabel {
                color: #aaa0bd;
                font-size: 13px;
            }
        """)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        editor = QTextEdit()
        editor.setPlaceholderText(
            "Escreva seu código aqui..."
        )

        editor.setStyleSheet("""
            QTextEdit {
                color: #f5edff;
                background-color: #030008;
                border: 1px solid #4d0870;
                border-radius: 14px;
                padding: 12px;
                font-family: Consolas;
                font-size: 13px;
            }

            QTextEdit:focus {
                border: 1px solid #ff00ff;
            }
        """)

        layout.addWidget(editor, 1)

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

        novo = QPushButton("NOVO")
        abrir = QPushButton("ABRIR")
        salvar = QPushButton("SALVAR")
        executar = QPushButton("▶  EXECUTAR")

        def novo_codigo():
            editor.clear()

        novo.clicked.connect(novo_codigo)

        botoes.addWidget(novo)
        botoes.addWidget(abrir)
        botoes.addWidget(salvar)
        botoes.addStretch()
        botoes.addWidget(executar)

        layout.addLayout(botoes)

        return pagina
    # ========================================================
    # PROJETOS
    # ========================================================

    def criar_pagina_projetos(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)

        titulo = QLabel("PROJETOS")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout.addWidget(titulo)

        nome = QLineEdit()
        nome.setPlaceholderText(
            "Nome do projeto..."
        )

        descricao = QTextEdit()
        descricao.setPlaceholderText(
            "Descrição do projeto..."
        )

        salvar = QPushButton(
            "SALVAR PROJETO"
        )

        salvar.clicked.connect(
            lambda: self.salvar_projeto(
                nome,
                descricao
            )
        )

        layout.addWidget(nome)
        layout.addWidget(descricao)
        layout.addWidget(salvar)

        layout.addStretch()

        return pagina

    def salvar_projeto(self, nome, descricao):

        nome_projeto = nome.text().strip()

        if not nome_projeto:
            return

        self.projetos[nome_projeto] = {
            "descricao": descricao.toPlainText(),
            "criado_em": datetime.now().isoformat()
        }

        salvar_json(
            "kenzie_projetos.json",
            self.projetos
        )

        nome.clear()
        descricao.clear()

        QMessageBox.information(
            self,
            "Kenzie",
            "Projeto salvo."
        )

    # ========================================================
    # TREINOS
    # ========================================================

    def criar_pagina_treinos(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)

        titulo = QLabel("TREINOS")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        nome = QLineEdit()
        nome.setPlaceholderText(
            "Nome do treino..."
        )

        descricao = QTextEdit()
        descricao.setPlaceholderText(
            "Descrição do treino..."
        )

        salvar = QPushButton(
            "SALVAR TREINO"
        )

        salvar.clicked.connect(
            lambda: self.salvar_treino(
                nome,
                descricao
            )
        )

        layout.addWidget(titulo)
        layout.addWidget(nome)
        layout.addWidget(descricao)
        layout.addWidget(salvar)

        layout.addStretch()

        return pagina

    def salvar_treino(self, nome, descricao):

        nome_treino = nome.text().strip()

        if not nome_treino:
            return

        self.treinos[nome_treino] = {
            "descricao": descricao.toPlainText(),
            "criado_em": datetime.now().isoformat()
        }

        salvar_json(
            "kenzie_treinos.json",
            self.treinos
        )

        nome.clear()
        descricao.clear()

        QMessageBox.information(
            self,
            "Kenzie",
            "Treino salvo."
        )

    # ========================================================
    # FINANÇAS
    # ========================================================

    def criar_pagina_financas(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)

        titulo = QLabel("FINANÇAS")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout.addWidget(titulo)

        cards = QGridLayout()

        categorias = [
            "RENDA",
            "DESPESAS FIXAS",
            "DESPESAS VARIÁVEIS",
            "GASTOS / LAZER",
            "RESERVA DE EMERGÊNCIA",
            "METAS E OBJETIVOS",
        ]

        for i, categoria in enumerate(categorias):

            card = StatCard(
                categoria,
                "Controle financeiro disponível."
            )

            cards.addWidget(
                card,
                i // 2,
                i % 2
            )

        layout.addLayout(cards)
        layout.addStretch()

        return pagina

    # ========================================================
    # CONFIGURAÇÕES
    # ========================================================

    def criar_pagina_configuracoes(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)

        titulo = QLabel("CONFIGURAÇÕES")
        titulo.setStyleSheet("""
            QLabel {
                color: #ff00ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout.addWidget(titulo)

        info = Card(
            "KENZIE",
            "Versão: 0.3\n"
            "Linguagem: Python\n"
            "Interface: PySide6\n"
            "Memória: Ativa\n"
            "Modo: Online / Offline"
        )

        sistema = Card(
            "SISTEMA",
            "Assistente pessoal desenvolvido "
            "para Windows.\n\n"
            "Sistema de memória, interface gráfica, "
            "comandos do sistema e interação por voz."
        )

        layout.addWidget(info)
        layout.addWidget(sistema)
        layout.addStretch()

        return pagina

    # ========================================================
    # NAVEGAÇÃO
    # ========================================================

    def ir_para_pagina(self, indice):

        self.paginas.setCurrentIndex(indice)

    # ========================================================
    # ENVIO DE MENSAGEM
    # ========================================================

    def enviar_mensagem(self):

        mensagem = self.entrada_chat.text().strip()

        if not mensagem:
            return

        # Se a página de conversa ainda não estiver selecionada,
        # a mensagem continua sendo enviada normalmente.
        self.entrada_chat.clear()

        try:
            from __main__ import detectar_ativacao

            estado = detectar_ativacao(mensagem)

        except Exception:
            estado = None

        if estado == "LEVE":

            self.estado_atual = "LEVE"
            self.nucleo_central.mudar_estado("leve")
            self.estado_nucleo.setText(
                "Estado: LEVE"
            )

            self.adicionar_mensagem(
                "Kenzie",
                "Estou acordada."
            )

            return

        if estado == "COMPLETO":

            self.estado_atual = "COMPLETO"
            self.nucleo_central.mudar_estado("completo")
            self.estado_nucleo.setText(
                "Estado: COMPLETO"
            )

            self.adicionar_mensagem(
                "Kenzie",
                "Vamos trabalhar."
            )

            return

        if estado == "STANDBY":

            self.estado_atual = "STANDBY"
            self.nucleo_central.mudar_estado("standby")
            self.estado_nucleo.setText(
                "Estado: STANDBY"
            )

            self.adicionar_mensagem(
                "Kenzie",
                "Entrando em espera."
            )

            return

        # Mensagem do usuário
        self.adicionar_mensagem(
            "Você",
            mensagem
        )

        self.entrada_chat.setEnabled(False)

        self.atividade_nucleo.setText(
            "Atividade: PROCESSANDO"
        )

        self.thread_processamento = QThread()
        self.worker_processamento = (
            ProcessarMensagemWorker(mensagem)
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

    def adicionar_mensagem(self, autor, texto):

        if not hasattr(self, "chat"):
            self.chat = QTextEdit()
            self.chat.setReadOnly(True)

        cor = "#ff00ff" if autor == "Kenzie" else "#ffffff"

        self.chat.insertHtml(
            '<br>'
            f'<span style="color:{cor};">'
            f'<b>{autor}:</b></span> '
            f'{texto}'
            '<br>'
        )

        self.paginas.setCurrentIndex(1)

    def finalizar_processamento(self, resposta):

        self.adicionar_mensagem(
            "Kenzie",
            str(resposta)
        )

        self.atividade_nucleo.setText(
            "Atividade: AGUARDANDO"
        )

        self.entrada_chat.setEnabled(True)
        self.entrada_chat.setFocus()

    def finalizar_erro(self, erro):

        self.adicionar_mensagem(
            "Erro",
            str(erro)
        )

        self.atividade_nucleo.setText(
            "Atividade: AGUARDANDO"
        )

        self.entrada_chat.setEnabled(True)
        self.entrada_chat.setFocus()

    # ========================================================
    # DIAGNÓSTICO
    # ========================================================

    def executar_diagnostico(self):

        resultados = []

        resultados.append("✓ Interface: OK")

        arquivos = [
            ("Memória", "kenzie_memory.json"),
            ("Projetos", "kenzie_projetos.json"),
            ("Treinos", "kenzie_treinos.json"),
            ("Finanças", "kenzie_financas.json"),
        ]

        for nome, arquivo in arquivos:

            if os.path.exists(arquivo):
                resultados.append(
                    f"✓ {nome}: OK"
                )
            else:
                resultados.append(
                    f"✗ {nome}: ARQUIVO NÃO ENCONTRADO"
                )

        modulos = [
            "PySide6",
            "dotenv",
            "openai",
            "pyttsx3",
            "tools",
        ]

        for modulo in modulos:

            try:
                __import__(modulo)

                resultados.append(
                    f"✓ Módulo {modulo}: OK"
                )

            except Exception:
                resultados.append(
                    f"✗ Módulo {modulo}: ERRO"
                )

        QMessageBox.information(
            self,
            "Diagnóstico da Kenzie",
            "\n".join(resultados)
        )


# ============================================================
# STACKED PAGES
# ============================================================

from PySide6.QtWidgets import QStackedWidget


class QStackedPages(QStackedWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QStackedWidget {
                background-color: #020006;
                border: none;
            }
        """)


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    janela = KenzieInterface()
    janela.show()

    app.exec()
