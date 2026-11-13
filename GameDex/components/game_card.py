from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

class GameCard(QWidget):
    def __init__(self, titulo, genero, plataforma, anio, puntuacion):
        super().__init__()

        # Tamaño de tarjeta en formato cuadrado / compacto
        self.setFixedSize(220, 170)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed, 
            QSizePolicy.Policy.Fixed
        )

        # Diseño interior de la tarjeta
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(6)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título del juego
        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
            }
        """)
        # Permitir que el título se ajuste si es largo pero sin romper el cuadro
        self.lbl_titulo.setWordWrap(True)
        layout_principal.addWidget(self.lbl_titulo)

        # Género
        self.lbl_genero = QLabel(f"Género: {genero}")
        self.lbl_genero.setStyleSheet("QLabel { color: #A5A7BD; font-size: 12px; }")
        layout_principal.addWidget(self.lbl_genero)

        # Plataforma
        self.lbl_plataforma = QLabel(f"Plataforma: {plataforma}")
        self.lbl_plataforma.setStyleSheet("QLabel { color: #A5A7BD; font-size: 12px; }")
        layout_principal.addWidget(self.lbl_plataforma)

        # Año
        self.lbl_anio = QLabel(f"Año: {anio}")
        self.lbl_anio.setStyleSheet("QLabel { color: #A5A7BD; font-size: 12px; }")
        layout_principal.addWidget(self.lbl_anio)

        # Puntuación (Estrellas)
        estrellas = "★" * puntuacion + "☆" * (5 - puntuacion)
        self.lbl_puntuacion = QLabel(estrellas)
        self.lbl_puntuacion.setStyleSheet("QLabel { color: #F39C12; font-size: 13px; }")
        layout_principal.addWidget(self.lbl_puntuacion)

        # Estilo visual del cuadro de la tarjeta
        self.setStyleSheet("""
            GameCard {
                background-color: #171827;
                border: 1px solid #292B40;
                border-radius: 12px;
            }
        """)