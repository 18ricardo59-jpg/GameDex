# ==========================================
# GAMEDEX
# Archivo: components/game_card.py
# Componente reutilizable: tarjeta de videojuego
# El aspecto (colores, fuentes, bordes) esta en
# resources/styles/gamedex.qss
# ==========================================

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Color de la "etiqueta de cartucho" segun la plataforma.
# El nombre de la plataforma tambien se escribe en la etiqueta,
# asi que el color nunca es la unica fuente de informacion.
COLORES_PLATAFORMA = {
    "pc": "#5B5FC7",
    "playstation 5": "#1F6FEB",
    "nintendo switch": "#D6322C",
    "xbox series x": "#1E8449",
    "xbox series x/s": "#1E8449",
}
COLOR_DEFECTO = "#6B7280"


class GameCard(QWidget):
    """Tarjeta que muestra un videojuego con botones Editar / Eliminar."""

    ANCHO = 230
    ALTO = 240

    # Señales para comunicar las acciones a la ventana principal
    editar_solicitado = Signal(int)
    eliminar_solicitado = Signal(int)

    def __init__(self, id_juego, titulo, genero, plataforma, anio, puntuacion):
        super().__init__()
        self.id_juego = id_juego

        # Necesario para que fondo y borde del QSS se pinten en un QWidget
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("GameCard")
        self.setFixedSize(self.ANCHO, self.ALTO)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Valores seguros ante datos vacíos en la base de datos
        titulo = str(titulo or "Sin título").strip() or "Sin título"
        genero = genero or "Sin género"
        plataforma = plataforma or "Sin plataforma"
        anio_texto = str(anio) if anio is not None else "Año sin indicar"

        self.setToolTip(titulo)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(1, 1, 1, 1)   # deja ver el borde de la tarjeta
        raiz.setSpacing(0)

        # ---------- Etiqueta superior (color de plataforma) ----------
        color = COLORES_PLATAFORMA.get(plataforma.strip().lower(), COLOR_DEFECTO)

        banner = QWidget()
        banner.setObjectName("cardBanner")
        banner.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        banner.setFixedHeight(70)
        banner.setStyleSheet(
            f"QWidget#cardBanner {{ background-color: {color};"
            " border-top-left-radius: 11px; border-top-right-radius: 11px; }"
        )

        fila_banner = QHBoxLayout(banner)
        fila_banner.setContentsMargins(16, 6, 14, 6)

        inicial = titulo[:1].upper() or "?"
        self.lbl_inicial = QLabel(inicial)
        self.lbl_inicial.setObjectName("cardInicial")
        self.lbl_inicial.setTextFormat(Qt.TextFormat.PlainText)
        fila_banner.addWidget(self.lbl_inicial)

        fila_banner.addStretch(1)

        self.lbl_plataforma = QLabel(plataforma)
        self.lbl_plataforma.setObjectName("cardPlataforma")
        self.lbl_plataforma.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_plataforma.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        fila_banner.addWidget(self.lbl_plataforma)

        raiz.addWidget(banner)

        # ---------- Cuerpo ----------
        cuerpo = QVBoxLayout()
        cuerpo.setContentsMargins(14, 12, 14, 12)
        cuerpo.setSpacing(7)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("cardTitulo")
        self.lbl_titulo.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_titulo.setWordWrap(True)
        self.lbl_titulo.setMaximumHeight(44)
        cuerpo.addWidget(self.lbl_titulo)

        fila_datos = QHBoxLayout()
        fila_datos.setSpacing(8)

        self.lbl_genero = QLabel(genero)
        self.lbl_genero.setObjectName("cardChip")
        self.lbl_genero.setTextFormat(Qt.TextFormat.PlainText)
        fila_datos.addWidget(self.lbl_genero)

        fila_datos.addStretch(1)

        self.lbl_anio = QLabel(anio_texto)
        self.lbl_anio.setObjectName("cardAnio")
        fila_datos.addWidget(self.lbl_anio)

        cuerpo.addLayout(fila_datos)

        # Puntuación: estrellas + número (no depende solo del color)
        try:
            valor = int(round(float(puntuacion)))
        except (TypeError, ValueError):
            valor = 0
        valor = max(0, min(5, valor))

        self.lbl_puntuacion = QLabel(
            "★" * valor + "☆" * (5 - valor) + f"   {valor}/5"
        )
        self.lbl_puntuacion.setObjectName("cardEstrellas")
        self.lbl_puntuacion.setAccessibleName(f"Puntuación {valor} de 5")
        cuerpo.addWidget(self.lbl_puntuacion)

        cuerpo.addStretch(1)

        # ---------- Botones ----------
        botones = QHBoxLayout()
        botones.setSpacing(8)

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setObjectName("btnEditarCard")
        self.btn_editar.setAccessibleName(f"Editar {titulo}")
        self.btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar.clicked.connect(
            lambda: self.editar_solicitado.emit(self.id_juego)
        )
        botones.addWidget(self.btn_editar)

        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setObjectName("btnEliminarCard")
        self.btn_eliminar.setAccessibleName(f"Eliminar {titulo}")
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.clicked.connect(
            lambda: self.eliminar_solicitado.emit(self.id_juego)
        )
        botones.addWidget(self.btn_eliminar)

        cuerpo.addLayout(botones)
        raiz.addLayout(cuerpo)
