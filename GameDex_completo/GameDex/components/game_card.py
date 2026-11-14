# ==========================================
# GAMEDEX
# Archivo: components/game_card.py
# Componente reutilizable: tarjeta de videojuego
# ==========================================

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Ruta RELATIVA al proyecto (funciona en cualquier equipo)
RUTA_ICONO = (
    Path(__file__).resolve().parent.parent
    / "resources" / "icons" / "gamepad.png"
)


class GameCard(QWidget):
    """Tarjeta que muestra un videojuego con botones Editar / Eliminar."""

    ANCHO = 220
    ALTO = 225

    # Señales para comunicar las acciones a la ventana principal
    editar_solicitado = Signal(int)
    eliminar_solicitado = Signal(int)

    def __init__(self, id_juego, titulo, genero, plataforma, anio, puntuacion):
        super().__init__()
        self.id_juego = id_juego

        # Necesario para que el fondo/borde del stylesheet se pinte
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("GameCard")
        self.setFixedSize(self.ANCHO, self.ALTO)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Valores seguros ante datos vacíos en la base de datos
        titulo = str(titulo or "Sin título")
        genero = genero or "—"
        plataforma = plataforma or "—"
        anio = anio if anio is not None else "—"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---- Cabecera: icono + título ----
        cabecera = QHBoxLayout()
        cabecera.setSpacing(8)

        self.lbl_icono = QLabel()
        self.lbl_icono.setFixedSize(32, 32)
        self.lbl_icono.setStyleSheet("background: transparent;")
        if RUTA_ICONO.exists():
            pix = QPixmap(str(RUTA_ICONO)).scaled(
                32, 32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.lbl_icono.setPixmap(pix)
        cabecera.addWidget(self.lbl_icono)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_titulo.setWordWrap(True)
        self.lbl_titulo.setStyleSheet(
            "background: transparent; color: #FFFFFF;"
            "font-size: 15px; font-weight: bold;"
        )
        cabecera.addWidget(self.lbl_titulo, 1)
        layout.addLayout(cabecera)

        # ---- Datos ----
        estilo_dato = "background: transparent; color: #C9CBE0; font-size: 12px;"

        self.lbl_genero = QLabel(f"Género: {genero}")
        self.lbl_genero.setStyleSheet(estilo_dato)
        layout.addWidget(self.lbl_genero)

        self.lbl_plataforma = QLabel(f"Plataforma: {plataforma}")
        self.lbl_plataforma.setStyleSheet(estilo_dato)
        layout.addWidget(self.lbl_plataforma)

        self.lbl_anio = QLabel(f"Año: {anio}")
        self.lbl_anio.setStyleSheet(estilo_dato)
        layout.addWidget(self.lbl_anio)

        # ---- Puntuación (estrellas + número: no solo color) ----
        try:
            valor = int(round(float(puntuacion)))
        except (TypeError, ValueError):
            valor = 0
        valor = max(0, min(5, valor))

        self.lbl_puntuacion = QLabel(
            "★" * valor + "☆" * (5 - valor) + f"  {valor}/5"
        )
        self.lbl_puntuacion.setStyleSheet(
            "background: transparent; color: #F39C12; font-size: 13px;"
        )
        self.lbl_puntuacion.setAccessibleName(f"Puntuación {valor} de 5")
        layout.addWidget(self.lbl_puntuacion)

        layout.addStretch(1)

        # ---- Botones ----
        botones = QHBoxLayout()
        botones.setSpacing(8)

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setAccessibleName(f"Editar {titulo}")
        self.btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #292B40; color: #FFFFFF;
                border-radius: 4px; padding: 5px; font-size: 12px;
            }
            QPushButton:hover, QPushButton:focus { background-color: #7C3AED; }
        """)
        self.btn_editar.clicked.connect(
            lambda: self.editar_solicitado.emit(self.id_juego)
        )
        botones.addWidget(self.btn_editar)

        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setAccessibleName(f"Eliminar {titulo}")
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #292B40; color: #FF8080;
                border-radius: 4px; padding: 5px; font-size: 12px;
            }
            QPushButton:hover, QPushButton:focus {
                background-color: #DC2626; color: #FFFFFF;
            }
        """)
        self.btn_eliminar.clicked.connect(
            lambda: self.eliminar_solicitado.emit(self.id_juego)
        )
        botones.addWidget(self.btn_eliminar)

        layout.addLayout(botones)

        self.setStyleSheet("""
            QWidget#GameCard {
                background-color: #171827;
                border: 1px solid #292B40;
                border-radius: 12px;
            }
        """)
