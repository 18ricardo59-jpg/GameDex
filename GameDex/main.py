import sys

from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QGridLayout,  
    QScrollArea, 
    QWidget,
    QSizePolicy
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt

from components.game_card import GameCard
from database import inicializar_base_datos, obtener_todos_los_juegos, insertar_juego, eliminar_juego_db


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Inicializar la base de datos al arrancar
        inicializar_base_datos()

        # Cargar interfaz principal
        archivo_ui = QFile("ui/main_window.ui")
        if not archivo_ui.open(QFile.OpenModeFlag.ReadOnly):
            print("Error: No se pudo abrir el archivo ui/main_window.ui")

        loader = QUiLoader()
        self.ui = loader.load(archivo_ui)
        archivo_ui.close()

        self.setCentralWidget(self.ui)
        self.setWindowTitle("GameDex")

        # =====================================================================
        # CONFIGURACIÓN DE LA CUADRÍCULA (GRID) PARA EL SCROLL
        # =====================================================================
        widget_viejo = self.ui.findChild(QWidget, "scrollArea")
        
        if widget_viejo and widget_viejo.parentWidget():
            parent_layout = widget_viejo.parentWidget().layout()
            
            if parent_layout:
                index = parent_layout.indexOf(widget_viejo)
                parent_layout.removeWidget(widget_viejo)
                widget_viejo.deleteLater()

                self.scroll_area = QScrollArea()
                self.scroll_area.setWidgetResizable(True)
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.scroll_area.setStyleSheet("""
                    QScrollArea {
                        background-color: #171827;
                        border: 1px solid #292B40;
                        border-radius: 10px;
                    }
                """)

                self.contenedor_tarjetas = QWidget()
                self.contenedor_tarjetas.setStyleSheet("background: transparent;")
                
                self.layout_tarjetas = QGridLayout(self.contenedor_tarjetas)
                self.layout_tarjetas.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.layout_tarjetas.setContentsMargins(15, 15, 15, 15)
                self.layout_tarjetas.setHorizontalSpacing(15)
                self.layout_tarjetas.setVerticalSpacing(15)

                self.scroll_area.setWidget(self.contenedor_tarjetas)
                parent_layout.insertWidget(index, self.scroll_area)
        else:
            self.layout_tarjetas = None

        # =====================================================================
        # NAVEGACIÓN ENTRE PÁGINAS
        # =====================================================================
        if hasattr(self.ui, "btnInicio"):
            self.ui.btnInicio.clicked.connect(
                lambda: self.ui.contenidoPrincipal.setCurrentWidget(self.ui.pageInicio)
            )

        if hasattr(self.ui, "btnBiblioteca"):
            self.ui.btnBiblioteca.clicked.connect(self.ir_a_biblioteca)

        if hasattr(self.ui, "btnIrBiblioteca"):
            self.ui.btnIrBiblioteca.clicked.connect(self.ir_a_biblioteca)

        if hasattr(self.ui, "btnSalir"):
            self.ui.btnSalir.clicked.connect(self.close)

        # =====================================================================
        # CONEXIÓN DE BOTONES PARA AÑADIR JUEGOS
        # =====================================================================
        if hasattr(self.ui, "btnAnadir"):
            self.ui.btnAnadir.clicked.connect(self.abrir_formulario_juego)

        if hasattr(self.ui, "btnNuevoJuego"):
            self.ui.btnNuevoJuego.clicked.connect(self.abrir_formulario_juego)

        # =====================================================================
        # CONFIGURACIÓN Y CONEXIÓN DE BUSCADOR Y FILTROS
        # =====================================================================
        self.configurar_buscador_y_filtros()

        # Cargar los juegos iniciales de la base de datos
        self.cargar_catalogo()

    def configurar_buscador_y_filtros(self):
        """Configura los inputs de búsqueda y filtros con placeholders y eventos."""
        # 1. Buscador por texto (QLineEdit)
        self.txt_buscador = self.ui.findChild(QWidget, "txtBuscar") # Ajusta el objectName si se llama distinto en tu UI
        if self.txt_buscador:
            self.txt_buscador.setPlaceholderText("Buscar videojuego...")
            self.txt_buscador.textChanged.connect(self.cargar_catalogo)

        # 2. Filtro por género (QComboBox)
        self.combo_filtro_genero = self.ui.findChild(QWidget, "comboGeneroFiltro") # O el nombre que tenga en tu UI
        if self.combo_filtro_genero:
            # Asegurar opción por defecto
            if self.combo_filtro_genero.count() == 0 or self.combo_filtro_genero.itemText(0) != "Todos los géneros":
                self.combo_filtro_genero.insertItem(0, "Todos los géneros")
            self.combo_filtro_genero.currentIndexChanged.connect(self.cargar_catalogo)

        # 3. Filtro por plataforma (QComboBox)
        self.combo_filtro_plataforma = self.ui.findChild(QWidget, "comboPlataformaFiltro") # O el nombre que tenga en tu UI
        if self.combo_filtro_plataforma:
            if self.combo_filtro_plataforma.count() == 0 or self.combo_filtro_plataforma.itemText(0) != "Todas las plataformas":
                self.combo_filtro_plataforma.insertItem(0, "Todas las plataformas")
            self.combo_filtro_plataforma.currentIndexChanged.connect(self.cargar_catalogo)

    def ir_a_biblioteca(self):
        """Cambia a la página de biblioteca y actualiza el catálogo."""
        self.ui.contenidoPrincipal.setCurrentWidget(self.ui.pageBiblioteca)
        self.cargar_catalogo()

    def cargar_catalogo(self):
        """Lee de SQLite, aplica filtros de búsqueda/género/plataforma y dibuja las tarjetas."""
        if self.layout_tarjetas is None:
            return

        # Limpiar cuadrícula actual
        while self.layout_tarjetas.count() > 0:
            item = self.layout_tarjetas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Obtener todos los juegos de la base de datos
        juegos = obtener_todos_los_juegos()

        # Recoger textos de búsqueda y filtros activos de forma segura
        texto_busqueda = self.txt_buscador.text().strip().lower() if hasattr(self, "txt_buscador") and self.txt_buscador else ""
        
        genero_seleccionado = "Todos los géneros"
        if hasattr(self, "combo_filtro_genero") and self.combo_filtro_genero:
            genero_seleccionado = self.combo_filtro_genero.currentText()

        plataforma_seleccionada = "Todas las plataformas"
        if hasattr(self, "combo_filtro_plataforma") and self.combo_filtro_plataforma:
            plataforma_seleccionada = self.combo_filtro_plataforma.currentText()

        # Filtrar los registros en memoria antes de pintarlos
        juegos_filtrados = []
        for juego in juegos:
            id_j, titulo, genero, plataforma, anio, puntuacion = juego

            # Filtro por texto (Título)
            match_texto = texto_busqueda in titulo.lower() if texto_busqueda else True
            
            # Filtro por Género
            match_genero = (genero_seleccionado == "Todos los géneros" or genero == genero_seleccionado)
            
            # Filtro por Plataforma
            match_plataforma = (plataforma_seleccionada == "Todas las plataformas" or plataforma == plataforma_seleccionada)

            if match_texto and match_genero and match_plataforma:
                juegos_filtrados.append(juego)

        # Dibujar tarjetas filtradas en cuadrícula de 3 columnas
        for index, juego in enumerate(juegos_filtrados):
            id_j, titulo, genero, plataforma, anio, puntuacion = juego
            
            tarjeta = GameCard(id_j, titulo, genero, plataforma, anio, puntuacion)
            tarjeta.eliminar_solicitado.connect(self.eliminar_videojuego)

            fila = index // 3
            columna = index % 3
            self.layout_tarjetas.addWidget(tarjeta, fila, columna)

    def abrir_formulario_juego(self):
        """Abre la ventana de diálogo para añadir un nuevo videojuego."""
        print("-> Abriendo formulario de videojuego...")
        
        archivo_form = QFile("ui/game_form.ui")
        if not archivo_form.open(QFile.OpenModeFlag.ReadOnly):
            print("❌ Error: No se pudo abrir el archivo ui/game_form.ui")
            return

        loader = QUiLoader()
        self.dialogo_juego = loader.load(archivo_form, self)
        archivo_form.close()

        self.dialogo_juego.setStyleSheet("""
            QDialog {
                background-color: #171827;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #1f2235;
                color: #ffffff;
                border: 1px solid #292B40;
                border-radius: 6px;
                padding: 6px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #7c3aed;
            }
            QComboBox::drop-down { border: 0px; }
            QComboBox QAbstractItemView {
                background-color: #1f2235;
                color: #ffffff;
                selection-background-color: #7c3aed;
                border: 1px solid #292B40;
            }
            QPushButton {
                background-color: #7c3aed;
                color: #ffffff;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6d28d9; }
            QPushButton#btnCancelar { background-color: #292B40; }
            QPushButton#btnCancelar:hover { background-color: #374151; }
        """)

        if hasattr(self.dialogo_juego, "btnCancelar"):
            self.dialogo_juego.btnCancelar.clicked.connect(self.dialogo_juego.close)

        if hasattr(self.dialogo_juego, "btnGuardar"):
            self.dialogo_juego.btnGuardar.clicked.connect(self.guardar_y_crear_tarjeta)

        self.dialogo_juego.exec()

    def guardar_y_crear_tarjeta(self):
        """Guarda el juego en SQLite y actualiza la biblioteca."""
        titulo = self.dialogo_juego.txtTitulo.text().strip()
        genero = self.dialogo_juego.txtGenero.currentText().strip()
        plataforma = self.dialogo_juego.txtPlataforma.currentText().strip()
        anio = self.dialogo_juego.spinAnio.value()
        puntuacion = self.dialogo_juego.spinPuntuacion.value()

        if not titulo:
            print("⚠️ El título del videojuego es obligatorio.")
            return

        # Insertar permanentemente en la base de datos SQLite
        insertar_juego(titulo, genero, plataforma, anio, puntuacion)
        print(f"¡Videojuego '{titulo}' guardado en SQLite!")

        self.dialogo_juego.close()
        
        # Volver a la biblioteca y refrescar las tarjetas automáticamente
        self.ir_a_biblioteca()

    def eliminar_videojuego(self, id_juego):
        """Elimina un videojuego de la base de datos y refresca la vista."""
        eliminar_juego_db(id_juego)
        print(f"🗑️ Videojuego con ID {id_juego} eliminado.")
        self.cargar_catalogo()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())