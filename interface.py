import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtGui import QPainter, QRadialGradient, QPen, QBrush
import random
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QRadialGradient

class BlackHoleWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 400)

        self.particulas = []

        for _ in range(80):
            angulo = random.uniform(0, 2 * math.pi)
            raio = random.uniform(90, 190)
            tamanho = random.uniform(1, 4)

            self.particulas.append({
                "angulo": angulo,
                "raio": raio,
                "tamanho": tamanho,
                "velocidade": random.uniform(0.002, 0.008)
            })  
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animar)
        self.timer.start(16)
        self.pulsacao = 0
    def animar(self):

        for particula in self.particulas:
            particula["angulo"] += particula["velocidade"]

        self.update()
        self.pulsacao += 0.05

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        centro_x = self.width() / 2
        centro_y = self.height() / 2

        # Aura

        raio_aura = 180 + math.sin(self.pulsacao) * 10

        gradiente = QRadialGradient(
        centro_x,
        centro_y,
        raio_aura
)

        gradiente.setColorAt(0.0, Qt.white)
        gradiente.setColorAt(0.2, Qt.magenta)
        gradiente.setColorAt(0.5, Qt.transparent)
        gradiente.setColorAt(1.0, Qt.transparent)

        painter.setBrush(gradiente)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(
            centro_x - 180,
            centro_y - 180,
            360,
            360
        )

        # Partículas

        painter.setBrush(QBrush(Qt.magenta))
        painter.setPen(Qt.NoPen)

        for particula in self.particulas:

            angulo = particula["angulo"]
            raio = particula["raio"]
            tamanho = particula["tamanho"]

            x = centro_x + math.cos(angulo) * raio
            y = centro_y + math.sin(angulo) * raio * 0.35

            painter.drawEllipse(
                x - tamanho / 2,
                y - tamanho / 2,
                tamanho,
                tamanho
            )

        # Disco de acreção

        espessura = 6 + math.sin(self.pulsacao) * 2

        painter.setPen(QPen(Qt.magenta, espessura))
        painter.setBrush(Qt.NoBrush)

        painter.drawEllipse(
            centro_x - 150,
            centro_y - 55,
            300,
            110
        )

        # Buraco negro
        painter.setBrush(Qt.darkMagenta)

        painter.drawEllipse(
            centro_x - 78,
        centro_y - 78,
        156,
        156
)

        painter.setBrush(Qt.black)

        painter.drawEllipse(
            centro_x - 70,
            centro_y - 70,
            140,
            140
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

        nucleo = QLabel("NÚCLEO")
        codigo = QLabel("CÓDIGO")
        estudos = QLabel("ESTUDOS")
        projetos = QLabel("PROJETOS")
        treinos = QLabel("TREINOS")
        financas = QLabel("FINANÇAS")
        configuracoes = QLabel("CONFIGURAÇÕES")

        menu.addWidget(titulo)
        menu.addWidget(nucleo)
        menu.addWidget(codigo)
        menu.addWidget(estudos)
        menu.addWidget(projetos)
        menu.addWidget(treinos)
        menu.addWidget(financas)
        menu.addWidget(configuracoes)

        # Núcleo central
        nucleo_central = BlackHoleWidget()

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
        layout_principal.addWidget(nucleo_central, 3)
        layout_principal.addLayout(painel, 2)


def iniciar_interface():

    app = QApplication(sys.argv)

    janela = KenzieInterface()
    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    iniciar_interface()