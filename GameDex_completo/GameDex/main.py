# ==========================================
# GAMEDEX
# Archivo: main.py
# Punto de entrada: python main.py
# ==========================================

import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import QDate, QEvent, QFile, QIODevice, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import database as db
from components.game_card import GameCard

# Carpeta del proyecto (todas las rutas son relativas a ella)
RUTA_PROYECTO = Path(__file__).resolve().parent
RUTA_ICONO_APP = RUTA_PROYECTO / "resources" / "icons" / "gamedex.png"

TODOS_GENEROS = "Todos los géneros"
TODAS_PLATAFORMAS = "Todas las plataformas"

# Opciones base de los filtros (las mismas que el formulario)
GENEROS_BASE = ["Acción", "RPG", "Aventura", "Estrategia", "Deportes"]
PLATAFORMAS_BASE = ["PC", "PlayStation 5", "Nintendo Switch", "Xbox Series X"]

ESTILO_FORMULARIO = """
    QDialog { background-color: #171827; color: #FFFFFF; }
    QLabel { color: #FFFFFF; font-size: 13px; }
    QLineEdit, QSpinBox, QComboBox {
        background-color: #1F2235; color: #FFFFFF;
        border: 1px solid #4B4F73; border-radius: 6px; padding: 6px;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 2px solid #A78BFA;
    }
    QComboBox::drop-down { border: 0px; }
    QComboBox QAbstractItemView {
        background-color: #1F2235; color: #FFFFFF;
        selection-background-color: #7C3AED; border: 1px solid #292B40;
    }
    QPushButton {
        background-color: #7C3AED; color: #FFFFFF;
        border-radius: 6px; padding: 8px; font-weight: bold;
    }
    QPushButton:hover { background-color: #6D28D9; }
    QPushButton:focus { border: 2px solid #FFFFFF; }
    QPushButton#btnCancelar { background-color: #374151; }
    QPushButton#btnCancelar:hover { background-color: #4B5563; }
"""


# =============================================================
# UTILIDAD: cargar un archivo .ui creado con Qt Designer
# =============================================================

def cargar_ui(nombre_archivo, padre=None):
    """Carga ui/<nombre_archivo> y devuelve el widget raíz."""

    ruta = RUTA_PROYECTO / "ui" / nombre_archivo
    archivo = QFile(str(ruta))

    if not archivo.open(QIODevice.OpenModeFlag.ReadOnly):
        raise FileNotFoundError(f"No se pudo abrir {ruta}")

    try:
        widget = QUiLoader().load(archivo, padre)
    finally:
        archivo.close()

    if widget is None:
        raise RuntimeError(f"No se pudo cargar la interfaz {nombre_archivo}")

    return widget


# =============================================================
# VENTANA PRINCIPAL
# =============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # RF09: crea la BD y la tabla si no existen
        db.inicializar_bd()

        self.tarjetas = []
        self.lbl_vacio = None
        self._columnas_actuales = 0

        self._cargar_interfaz()
        self._configurar_catalogo()
        self._configurar_menus()
        self._configurar_navegacion()
        self._configurar_filtros()

        # RF10: cargar los datos al iniciar
        self.actualizar_catalogo()

    # ---------------------------------------------------------
    # Interfaz
    # ---------------------------------------------------------

    def _cargar_interfaz(self):
        """Carga main_window.ui y usa su contenido como central."""

        # Guardamos la referencia para que Qt no destruya los hijos
        self._ventana_ui = cargar_ui("main_window.ui")

        central = self._ventana_ui.centralWidget()
        self.setCentralWidget(central)

        self.setWindowTitle("GameDex")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        if RUTA_ICONO_APP.exists():
            self.setWindowIcon(QIcon(str(RUTA_ICONO_APP)))

        # El panel principal debe adaptarse a la ventana
        # (en el .ui estaba con posición y tamaño fijos)
        principal = self.findChild(QWidget, "contenedorPrincipal")

        if principal is not None and central.layout() is None:
            layout = QVBoxLayout(central)
            layout.setContentsMargins(9, 9, 9, 9)
            layout.addWidget(principal)

        self.stack = self.findChild(QStackedWidget, "contenidoPrincipal")
        self.pagina_inicio = self.findChild(QWidget, "pageInicio")
        self.pagina_biblioteca = self.findChild(QWidget, "pageBiblioteca")

    def _configurar_catalogo(self):
        """Sustituye el contenedor fijo del .ui por uno con layout."""

        self.scroll_area = self.findChild(QScrollArea, "scrollArea")

        if self.scroll_area is None:
            raise RuntimeError("No se encuentra 'scrollArea' en main_window.ui")

        self.contenedor_tarjetas = QWidget()
        self.contenedor_tarjetas.setObjectName("contenedorTarjetas")
        self.contenedor_tarjetas.setStyleSheet(
            "QWidget#contenedorTarjetas { background: transparent; }"
        )

        self.layout_tarjetas = QGridLayout(self.contenedor_tarjetas)
        self.layout_tarjetas.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.layout_tarjetas.setContentsMargins(15, 15, 15, 15)
        self.layout_tarjetas.setHorizontalSpacing(15)
        self.layout_tarjetas.setVerticalSpacing(15)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.contenedor_tarjetas)

        # Para recolocar las tarjetas al cambiar el ancho
        self._viewport = self.scroll_area.viewport()
        self._viewport.installEventFilter(self)

    def _configurar_menus(self):
        """Barra de menús de la ventana principal."""

        barra = self.menuBar()
        barra.setStyleSheet("""
            QMenuBar { background-color: #171827; color: #FFFFFF; }
            QMenuBar::item:selected { background-color: #7C3AED; }
            QMenu { background-color: #1F2235; color: #FFFFFF; }
            QMenu::item:selected { background-color: #7C3AED; }
        """)

        menu_archivo = barra.addMenu("&Archivo")

        accion_nuevo = QAction("&Añadir videojuego", self)
        accion_nuevo.setShortcut(QKeySequence("Ctrl+N"))
        accion_nuevo.triggered.connect(self.anadir_videojuego)
        menu_archivo.addAction(accion_nuevo)

        menu_archivo.addSeparator()

        accion_salir = QAction("&Salir", self)
        accion_salir.setShortcut(QKeySequence("Ctrl+Q"))
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        menu_ver = barra.addMenu("&Ver")

        accion_inicio = QAction("&Inicio", self)
        accion_inicio.triggered.connect(self.ir_a_inicio)
        menu_ver.addAction(accion_inicio)

        accion_biblioteca = QAction("&Biblioteca", self)
        accion_biblioteca.triggered.connect(self.ir_a_biblioteca)
        menu_ver.addAction(accion_biblioteca)

        menu_ayuda = barra.addMenu("A&yuda")

        accion_acerca = QAction("&Acerca de GameDex", self)
        accion_acerca.triggered.connect(self.mostrar_acerca_de)
        menu_ayuda.addAction(accion_acerca)

    # ---------------------------------------------------------
    # Navegación
    # ---------------------------------------------------------

    def _configurar_navegacion(self):

        def conectar(nombre, funcion):
            boton = self.findChild(QPushButton, nombre)
            if boton is not None:
                boton.clicked.connect(funcion)

        conectar("btnInicio", self.ir_a_inicio)
        conectar("btnBiblioteca", self.ir_a_biblioteca)
        conectar("btnIrBiblioteca", self.ir_a_biblioteca)
        conectar("btnAnadir", self.anadir_videojuego)
        conectar("btnSalir", self.close)

    def ir_a_inicio(self, *_):
        self.stack.setCurrentWidget(self.pagina_inicio)

    def ir_a_biblioteca(self, *_):
        self.stack.setCurrentWidget(self.pagina_biblioteca)
        self.actualizar_catalogo()

    def mostrar_acerca_de(self, *_):
        QMessageBox.information(
            self,
            "Acerca de GameDex",
            "GameDex\nGestión de tu biblioteca de videojuegos.\n\n"
            "Python · PySide6 · SQLite",
        )

    # ---------------------------------------------------------
    # Búsqueda y filtros (RF03 y RF04)
    # ---------------------------------------------------------

    def _configurar_filtros(self):

        self.txt_buscador = self.findChild(QLineEdit, "textBuscar")
        self.cmb_genero = self.findChild(QComboBox, "cmbGenero")
        self.cmb_plataforma = self.findChild(QComboBox, "cmbPlataforma")
        self.btn_limpiar = self.findChild(QPushButton, "btnNuevoJuego")

        self.txt_buscador.setPlaceholderText(
            "Escribe el título del videojuego..."
        )
        self.txt_buscador.setAccessibleName("Buscar videojuego por título")
        self.cmb_genero.setAccessibleName("Filtrar por género")
        self.cmb_plataforma.setAccessibleName("Filtrar por plataforma")

        # Botón reutilizado: ahora limpia los filtros
        self.btn_limpiar.setText("Limpiar filtros")
        self.btn_limpiar.setAccessibleName("Limpiar búsqueda y filtros")

        self._rellenar_filtros()

        # Búsqueda en tiempo real: cada letra actualiza el catálogo
        self.txt_buscador.textChanged.connect(self.actualizar_catalogo)
        self.cmb_genero.currentIndexChanged.connect(self.actualizar_catalogo)
        self.cmb_plataforma.currentIndexChanged.connect(self.actualizar_catalogo)
        self.btn_limpiar.clicked.connect(self.limpiar_filtros)

        # Orden de tabulación de la biblioteca
        QWidget.setTabOrder(self.txt_buscador, self.cmb_genero)
        QWidget.setTabOrder(self.cmb_genero, self.cmb_plataforma)
        QWidget.setTabOrder(self.cmb_plataforma, self.btn_limpiar)

    def _rellenar_combo(self, combo, texto_todos, base, existentes):
        """Rellena un desplegable conservando la selección actual."""

        seleccionado = combo.currentText()

        combo.blockSignals(True)
        combo.clear()
        combo.addItem(texto_todos)

        valores = list(base)
        for valor in existentes:
            if valor not in valores:
                valores.append(valor)

        combo.addItems(valores)

        indice = combo.findText(seleccionado)
        combo.setCurrentIndex(indice if indice >= 0 else 0)
        combo.blockSignals(False)

    def _rellenar_filtros(self):
        """Opciones base + las que existan en la base de datos."""

        self._rellenar_combo(
            self.cmb_genero, TODOS_GENEROS,
            GENEROS_BASE, db.obtener_generos()
        )
        self._rellenar_combo(
            self.cmb_plataforma, TODAS_PLATAFORMAS,
            PLATAFORMAS_BASE, db.obtener_plataformas()
        )

    def limpiar_filtros(self, *_):
        self.txt_buscador.blockSignals(True)
        self.txt_buscador.clear()
        self.txt_buscador.blockSignals(False)

        self.cmb_genero.blockSignals(True)
        self.cmb_genero.setCurrentIndex(0)
        self.cmb_genero.blockSignals(False)

        self.cmb_plataforma.blockSignals(True)
        self.cmb_plataforma.setCurrentIndex(0)
        self.cmb_plataforma.blockSignals(False)

        self.actualizar_catalogo()

    # ---------------------------------------------------------
    # Catálogo (RF02)
    # ---------------------------------------------------------

    def actualizar_catalogo(self, *_):
        """Consulta SQLite con los filtros actuales y dibuja las tarjetas."""

        try:
            texto = self.txt_buscador.text().strip()
            genero = self.cmb_genero.currentText()
            plataforma = self.cmb_plataforma.currentText()

            juegos = db.filtrar_videojuegos(
                genero=None if genero == TODOS_GENEROS else genero,
                plataforma=None if plataforma == TODAS_PLATAFORMAS else plataforma,
                texto=texto or None,
            )
            total = len(db.obtener_videojuegos())

        except sqlite3.Error as error:
            QMessageBox.critical(
                self, "Error de base de datos",
                f"No se pudieron leer los videojuegos:\n{error}"
            )
            return

        # Eliminar tarjetas anteriores
        self._vaciar_catalogo()

        if not juegos:
            self.lbl_vacio = QLabel(
                "Todavía no hay videojuegos. Pulsa «Añadir videojuego»."
                if total == 0
                else "No se encontraron videojuegos con esos filtros."
            )
            self.lbl_vacio.setStyleSheet(
                "background: transparent; color: #FFFFFF;"
                "font-size: 15px; padding: 20px;"
            )
            self.layout_tarjetas.addWidget(self.lbl_vacio, 0, 0)
        else:
            for id_juego, titulo, genero_j, plataforma_j, anio, puntuacion in juegos:
                tarjeta = GameCard(
                    id_juego, titulo, genero_j, plataforma_j, anio, puntuacion
                )
                tarjeta.editar_solicitado.connect(self.editar_videojuego)
                tarjeta.eliminar_solicitado.connect(self.eliminar_videojuego)
                self.tarjetas.append(tarjeta)

            self._colocar_tarjetas()

        self.statusBar().showMessage(
            f"Mostrando {len(juegos)} de {total} videojuegos"
        )

    def _vaciar_catalogo(self):
        while self.layout_tarjetas.count() > 0:
            item = self.layout_tarjetas.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        self.tarjetas = []
        self.lbl_vacio = None
        self._columnas_actuales = 0

    def _calcular_columnas(self):
        ancho = self._viewport.width() - 30
        return max(1, (ancho + 15) // (GameCard.ANCHO + 15))

    def _colocar_tarjetas(self):
        """Reparte las tarjetas en tantas columnas como quepan."""

        columnas = self._calcular_columnas()

        # Sacamos los widgets del layout sin destruirlos
        while self.layout_tarjetas.count() > 0:
            self.layout_tarjetas.takeAt(0)

        for indice, tarjeta in enumerate(self.tarjetas):
            self.layout_tarjetas.addWidget(
                tarjeta, indice // columnas, indice % columnas
            )
            tarjeta.show()

        self._columnas_actuales = columnas

    def eventFilter(self, objeto, evento):
        """Recoloca las tarjetas cuando cambia el ancho del scroll."""

        if (
            objeto is getattr(self, "_viewport", None)
            and evento.type() == QEvent.Type.Resize
            and self.tarjetas
            and self._calcular_columnas() != self._columnas_actuales
        ):
            self._colocar_tarjetas()

        return super().eventFilter(objeto, evento)

    # ---------------------------------------------------------
    # Formulario de alta / edición (RF05, RF06, RF11, RF12)
    # ---------------------------------------------------------

    def anadir_videojuego(self, *_):
        self._abrir_formulario(None)

    def editar_videojuego(self, id_juego):
        juego = next(
            (j for j in db.obtener_videojuegos() if j[0] == id_juego), None
        )

        if juego is None:
            QMessageBox.warning(
                self, "Videojuego no encontrado",
                "El videojuego ya no existe en la base de datos."
            )
            self.actualizar_catalogo()
            return

        self._abrir_formulario(juego)

    def _abrir_formulario(self, juego):
        """Abre game_form.ui. Si 'juego' no es None, se edita."""

        try:
            dialogo = cargar_ui("game_form.ui", self)
        except (FileNotFoundError, RuntimeError) as error:
            QMessageBox.critical(self, "Error", str(error))
            return

        editando = juego is not None

        dialogo.setStyleSheet(ESTILO_FORMULARIO)
        dialogo.setWindowTitle(
            "Editar videojuego" if editando else "Añadir videojuego"
        )
        dialogo.setModal(True)

        if RUTA_ICONO_APP.exists():
            dialogo.setWindowIcon(QIcon(str(RUTA_ICONO_APP)))

        lbl_titulo_form = dialogo.findChild(QLabel, "lblTituloForm")
        txt_titulo = dialogo.findChild(QLineEdit, "txtTitulo")
        cmb_genero = dialogo.findChild(QComboBox, "txtGenero")
        cmb_plataforma = dialogo.findChild(QComboBox, "txtPlataforma")
        spin_anio = dialogo.findChild(QSpinBox, "spinAnio")
        spin_puntuacion = dialogo.findChild(QSpinBox, "spinPuntuacion")
        btn_guardar = dialogo.findChild(QPushButton, "btnGuardar")
        btn_cancelar = dialogo.findChild(QPushButton, "btnCancelar")

        if lbl_titulo_form is not None:
            lbl_titulo_form.setText(
                "Editar videojuego" if editando else "Añadir videojuego"
            )

        txt_titulo.setAccessibleName("Título del videojuego (obligatorio)")
        cmb_genero.setAccessibleName("Género")
        cmb_plataforma.setAccessibleName("Plataforma")
        spin_anio.setAccessibleName("Año de lanzamiento")
        spin_puntuacion.setAccessibleName("Puntuación de 1 a 5")
        spin_puntuacion.setSuffix(" / 5")

        # Valores iniciales
        if editando:
            _, titulo, genero, plataforma, anio, puntuacion = juego

            txt_titulo.setText(titulo or "")

            for combo, valor in ((cmb_genero, genero), (cmb_plataforma, plataforma)):
                if valor:
                    if combo.findText(valor) < 0:
                        combo.addItem(valor)  # valor antiguo no listado
                    combo.setCurrentText(valor)

            if anio is not None:
                spin_anio.setValue(int(anio))
            if puntuacion is not None:
                spin_puntuacion.setValue(int(round(float(puntuacion))))
        else:
            anio_actual = QDate.currentDate().year()
            spin_anio.setValue(
                max(spin_anio.minimum(), min(anio_actual, spin_anio.maximum()))
            )
            spin_puntuacion.setValue(3)

        # Orden de tabulación lógico
        orden = [txt_titulo, cmb_genero, cmb_plataforma, spin_anio,
                 spin_puntuacion, btn_guardar, btn_cancelar]
        for anterior, siguiente in zip(orden, orden[1:]):
            QWidget.setTabOrder(anterior, siguiente)

        btn_guardar.setDefault(True)
        txt_titulo.setFocus()

        resultado = {"guardado": False, "titulo": ""}

        def guardar():
            titulo = txt_titulo.text().strip()

            if not titulo:
                QMessageBox.warning(
                    dialogo, "Campo obligatorio",
                    "Error: debes introducir el título del videojuego."
                )
                txt_titulo.setFocus()
                return

            try:
                if editando:
                    db.editar_videojuego(
                        juego[0], titulo,
                        cmb_genero.currentText().strip(),
                        cmb_plataforma.currentText().strip(),
                        spin_anio.value(), spin_puntuacion.value(),
                    )
                else:
                    db.agregar_videojuego(
                        titulo,
                        cmb_genero.currentText().strip(),
                        cmb_plataforma.currentText().strip(),
                        spin_anio.value(), spin_puntuacion.value(),
                    )
            except ValueError as error:
                QMessageBox.warning(
                    dialogo, "Datos no válidos", f"Error: {error}"
                )
                return
            except sqlite3.Error as error:
                QMessageBox.critical(
                    dialogo, "Error de base de datos",
                    f"No se pudo guardar el videojuego:\n{error}"
                )
                return

            resultado["guardado"] = True
            resultado["titulo"] = titulo
            dialogo.accept()

        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialogo.reject)

        dialogo.exec()

        if resultado["guardado"]:
            accion = "actualizado" if editando else "añadido"
            QMessageBox.information(
                self, "Videojuego guardado",
                f"Correcto: «{resultado['titulo']}» se ha {accion}."
            )
            self._rellenar_filtros()
            self.ir_a_biblioteca()

    # ---------------------------------------------------------
    # Eliminar (RF07 y RF08)
    # ---------------------------------------------------------

    def eliminar_videojuego(self, id_juego):
        juego = next(
            (j for j in db.obtener_videojuegos() if j[0] == id_juego), None
        )
        titulo = juego[1] if juego else "este videojuego"

        caja = QMessageBox(self)
        caja.setIcon(QMessageBox.Icon.Question)
        caja.setWindowTitle("Eliminar videojuego")
        caja.setText(f"¿Seguro que quieres eliminar «{titulo}»?")
        caja.setInformativeText("Esta acción no se puede deshacer.")

        boton_si = caja.addButton(
            "Sí, eliminar", QMessageBox.ButtonRole.DestructiveRole
        )
        boton_no = caja.addButton(
            "Cancelar", QMessageBox.ButtonRole.RejectRole
        )
        caja.setDefaultButton(boton_no)
        caja.exec()

        if caja.clickedButton() is not boton_si:
            return

        try:
            db.eliminar_videojuego(id_juego)
        except sqlite3.Error as error:
            QMessageBox.critical(
                self, "Error de base de datos",
                f"No se pudo eliminar el videojuego:\n{error}"
            )
            return

        self._rellenar_filtros()
        self.actualizar_catalogo()
        self.statusBar().showMessage(f"«{titulo}» eliminado.", 4000)


# =============================================================
# INICIO DE LA APLICACIÓN
# =============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())
