import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtGui import QPainter, QRadialGradient, QPen, QBrush, QColor
import random
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QRadialGradient

class BlackHoleWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 400)

        self.particulas = []

        for _ in range(120):
            angulo = random.uniform(0, 2 * math.pi)
            raio = random.uniform(90, 190)
            tamanho = random.uniform(1, 4)

            self.particulas.append({
            "angulo": angulo,
            "raio": raio,
            "tamanho": tamanho,
            "brilho": random.uniform(0.4, 1.0),
            "velocidade": random.uniform(0.002, 0.008),
            "variacao_velocidade": random.uniform(0.85, 1.15)
})
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animar)
        self.timer.start(16)
        self.pulsacao = 0
        self.estado = "standby"
    def mudar_estado(self, estado):
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

        self.intensidade_estado = intensidade_estado

        for particula in self.particulas:
            particula["angulo"] += particula["velocidade"] * particula["variacao_velocidade"] * velocidade_estado * (220 / particula["raio"])
            particula["variacao_velocidade"] = max(
            0.8,
            min(1.2, particula["variacao_velocidade"] + math.sin(self.pulsacao * 0.3 + particula["angulo"]) * 0.0005)
)
            particula["raio"] += math.sin(self.pulsacao * 0.8 + particula["angulo"]) * 0.12
            particula["tamanho"] = max(1, min(4, particula["tamanho"] + math.sin(self.pulsacao + particula["angulo"]) * 0.03))
            particula["brilho"] = (0.6 + math.sin(particula["angulo"] * 2 + self.pulsacao) * 0.4) * intensidade_estado

        self.update()
        self.pulsacao += 0.05 * velocidade_estado
        self.pulsacao += 0.02 * velocidade_estado

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.fillRect(self.rect(), QColor("#030008"))

        painter.setCompositionMode(QPainter.CompositionMode_Screen)

        centro_x = self.width() / 2
        centro_y = self.height() / 2
        escala = min(self.width(), self.height()) / 500

        # Aura

        raio_aura = min(self.width(), self.height()) * 0.32 + math.sin(self.pulsacao) * 18 * escala

        gradiente = QRadialGradient(
        centro_x,
        centro_y,
        raio_aura
)

        gradiente.setColorAt(0.0, Qt.white)
        gradiente.setColorAt(0.2,QColor(255, 0, 255, int(255 * self.intensidade_estado))
)
        gradiente.setColorAt(0.5, Qt.transparent)
        gradiente.setColorAt(1.0, Qt.transparent)

        painter.setBrush(gradiente)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(
            centro_x - 180 * escala,
            centro_y - 180 * escala,
            360 * escala,
            360 * escala
)
        # Partículas

        painter.setBrush(QBrush(Qt.magenta))
        painter.setPen(Qt.NoPen)

        for particula in self.particulas:

            angulo = particula["angulo"]
            raio = particula["raio"]
            raio_visual = raio + math.sin(angulo * 3 + self.pulsacao) * 2
            tamanho = particula["tamanho"]
            brilho = particula["brilho"]
            painter.setOpacity(brilho)

            x = centro_x + math.cos(angulo) * raio_visual
            y = centro_y + math.sin(angulo) * raio * (0.35 + math.sin(self.pulsacao) * 0.04)
            painter.setPen(QPen(Qt.magenta, 1, Qt.SolidLine))
            painter.setOpacity(brilho * 0.35)
            painter.setOpacity(brilho * 0.15)

            painter.drawEllipse(
            x - tamanho * (1 + brilho),
            y - tamanho * (1 + brilho),
            tamanho * (2 + brilho * 2),
            tamanho * (2 + brilho * 2)
)

            painter.drawLine(
            x,
            y,
            x + math.sin(angulo) * 6,
            y - math.cos(angulo) * 6
        )
            painter.setOpacity(brilho)
            painter.drawEllipse(
                x - tamanho / 2,
                y - tamanho / 2,
                tamanho,
                tamanho
            )
            painter.setOpacity(1.0)
    # Linhas orbitais

        painter.save()

        painter.translate(centro_x, centro_y)

        painter.rotate(self.pulsacao * 2)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(Qt.magenta, 1))

        painter.drawEllipse(
        -165 * escala,
        -62 * escala,
        330 * escala,
        124 * escala
)

        painter.rotate(-self.pulsacao * 4)

        painter.setPen(QPen(Qt.darkMagenta, 1))

        painter.drawEllipse(
        -175 * escala,
        -68 * escala,
        350 * escala,
        136 * escala
)

        painter.restore()

        # Disco de acreção

        espessura = 6 + math.sin(self.pulsacao * 1.5) * 2.5
        painter.save()
        painter.translate(centro_x, centro_y)
        painter.rotate(self.pulsacao * 0.5)
        painter.setPen(QPen(Qt.magenta, espessura))
        painter.setBrush(Qt.NoBrush)

        painter.drawEllipse(
        -150 * escala,
        -55 * escala,
        300 * escala,
        110 * escala
)
        painter.restore()
        painter.save()

        painter.translate(centro_x, centro_y)
        painter.rotate(-self.pulsacao * 0.8)

        painter.setPen(QPen(Qt.magenta, 3))
        painter.setBrush(Qt.NoBrush)

        painter.drawEllipse(
        -135 * escala,
        -42 * escala,
        270 * escala,
        84 * escala
)

        painter.restore()
                # Brilho do horizonte

        brilho = QRadialGradient(
        centro_x,
        centro_y,
        95 * escala
)

        brilho.setColorAt(0.0, Qt.transparent)
        brilho.setColorAt(
        0.7,
        QColor(255, 0, 255, int(100 + math.sin(self.pulsacao) * 40))
)
        brilho.setColorAt(1.0, Qt.transparent)

        painter.setBrush(brilho)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(
        centro_x - 95 * escala,
        centro_y - 95 * escala,
        190 * escala,
        190 * escala
)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Buraco negro
        painter.setBrush(Qt.darkMagenta)

        painter.drawEllipse(
        centro_x - 78 * escala,
        centro_y - 78 * escala,
        156 * escala,
        156 * escala
)

        painter.setBrush(Qt.black)

        painter.drawEllipse(
        centro_x - 70 * escala,
        centro_y - 70 * escala,
        140 * escala,
        140 * escala
)
        painter.end()
class KenzieInterface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kenzie")
        self.resize(1200, 700)

        self.criar_interface()

    def criar_interface(self):

        # Área principal
        central = QWidget()
        central.setStyleSheet("background-color: #030008;")
        self.setCentralWidget(central)

        # Layout principal
        layout_principal = QHBoxLayout()
        central.setLayout(layout_principal)

        # Menu lateral
        menu = QVBoxLayout()

        titulo = QLabel("KENZIE")
        titulo.setAlignment(Qt.AlignCenter)
        botao_standby = QPushButton("STANDBY")
        botao_standby.setStyleSheet("color: magenta;")
        
        nucleo = QLabel("NÚCLEO")
        codigo = QLabel("CÓDIGO")
        estudos = QLabel("ESTUDOS")
        projetos = QLabel("PROJETOS")
        treinos = QLabel("TREINOS")
        financas = QLabel("FINANÇAS")
        configuracoes = QLabel("CONFIGURAÇÕES")

        menu.addWidget(titulo)
        menu.addWidget(botao_standby)
        menu.addWidget(nucleo)
        menu.addWidget(codigo)
        menu.addWidget(estudos)
        menu.addWidget(projetos)
        menu.addWidget(treinos)
        menu.addWidget(financas)
        menu.addWidget(configuracoes)

        # Núcleo central
        self.nucleo_central = BlackHoleWidget()
        botao_standby.clicked.connect(lambda: self.nucleo_central.mudar_estado("standby"))
        self.nucleo_central.mudar_estado("completo")

        # Painel direito
        painel = QVBoxLayout()

        agenda = QLabel("AGENDA")
        tarefas = QLabel("TAREFAS DO DIA")
        anotacoes = QLabel("ANOTAÇÕES RÁPIDAS")

        painel.addWidget(agenda)
        painel.addWidget(tarefas)
        painel.addWidget(anotacoes)

        # Montando a interface
        layout_principal.addLayout(menu, 1)
        layout_principal.addWidget(self.nucleo_central, 3)
        layout_principal.addLayout(painel, 2)


def iniciar_interface():

    app = QApplication(sys.argv)

    janela = KenzieInterface()
    janela.show()

    app.exec()


if __name__ == "__main__":
    iniciar_interface()