
# ==========================================
# GAMEDEX
# Archivo: main.py
# Ventana principal de la aplicación
# ==========================================

import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QComboBox,
    QStackedWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QDialog
)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt

# Importamos nuestra base de datos
import database

# Importamos el formulario de videojuegos
from game_form import GameForm


# ==========================================
# CLASE PRINCIPAL DE GAMEDEX
# ==========================================

class GameDex:

    def __init__(self):
        """
        Constructor de GameDex.

        Prepara la base de datos, carga la interfaz,
        conecta los botones y muestra el catálogo.
        """

        # Inicializar SQLite
        database.inicializar_bd()

        # ----------------------------------
        # CARGAR INTERFAZ PRINCIPAL
        # ----------------------------------

        loader = QUiLoader()

        # Obtener la ruta del proyecto
        self.RUTA_PROYECTO = os.path.dirname(
            os.path.abspath(__file__)
        )

        # Construir la ruta de main_window.ui
        ruta_ui = os.path.join(
            self.RUTA_PROYECTO,
            "ui",
            "main_window.ui"
        )

        # Abrir el archivo UI
        archivo = QFile(ruta_ui)

        if not archivo.open(QFile.OpenModeFlag.ReadOnly):
            raise RuntimeError(
                f"No se encuentra el archivo: {ruta_ui}"
            )

        # Cargar la ventana
        self.ventana = loader.load(archivo)

        archivo.close()

        if self.ventana is None:
            raise RuntimeError(
                "No se ha podido cargar la ventana principal."
            )

        # ----------------------------------
        # OBTENER COMPONENTES DE LA VENTANA
        # ----------------------------------

        self.btnInicio = self.ventana.findChild(
            QPushButton, "btnInicio"
        )

        self.btnBiblioteca = self.ventana.findChild(
            QPushButton, "btnBiblioteca"
        )

        self.btnSalir = self.ventana.findChild(
            QPushButton, "btnSalir"
        )

        self.btnIrBiblioteca = self.ventana.findChild(
            QPushButton, "btnIrBiblioteca"
        )

        self.btnAnadir = self.ventana.findChild(
            QPushButton, "btnAnadir"
        )

        self.btnNuevoJuego = self.ventana.findChild(
            QPushButton, "btnNuevoJuego"
        )

        self.textBuscar = self.ventana.findChild(
            QLineEdit, "textBuscar"
        )

        self.cmbGenero = self.ventana.findChild(
            QComboBox, "cmbGenero"
        )

        self.cmbPlataforma = self.ventana.findChild(
            QComboBox, "cmbPlataforma"
        )

        self.contenidoPrincipal = self.ventana.findChild(
            QStackedWidget, "contenidoPrincipal"
        )

        self.contenedorTarjetas = self.ventana.findChild(
            QWidget, "contenedorTarjetas"
        )

        # Comprobar que los componentes necesarios existen
        componentes = {
            "btnInicio": self.btnInicio,
            "btnBiblioteca": self.btnBiblioteca,
            "btnSalir": self.btnSalir,
            "btnIrBiblioteca": self.btnIrBiblioteca,
            "btnAnadir": self.btnAnadir,
            "btnNuevoJuego": self.btnNuevoJuego,
            "textBuscar": self.textBuscar,
            "cmbGenero": self.cmbGenero,
            "cmbPlataforma": self.cmbPlataforma,
            "contenidoPrincipal": self.contenidoPrincipal,
            "contenedorTarjetas": self.contenedorTarjetas
        }

        for nombre, componente in componentes.items():

            if componente is None:
                raise RuntimeError(
                    f"No se encuentra el componente {nombre}."
                )

        # ----------------------------------
        # PREPARAR CONTENEDOR DEL CATÁLOGO
        # ----------------------------------

        # Creamos un layout vertical para los videojuegos
        self.layoutTarjetas = QVBoxLayout(
            self.contenedorTarjetas
        )

        self.layoutTarjetas.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        # ----------------------------------
        # CONFIGURAR BUSCADOR
        # ----------------------------------

        self.textBuscar.clear()

        self.textBuscar.setPlaceholderText(
            "Buscar videojuego..."
        )

        # ----------------------------------
        # CONECTAR BOTONES DE NAVEGACIÓN
        # ----------------------------------

        self.btnInicio.clicked.connect(
            lambda: self.cambiar_pagina(0)
        )

        self.btnBiblioteca.clicked.connect(
            lambda: self.cambiar_pagina(1)
        )

        self.btnIrBiblioteca.clicked.connect(
            lambda: self.cambiar_pagina(1)
        )

        self.btnSalir.clicked.connect(
            self.ventana.close
        )

        # ----------------------------------
        # CONECTAR BOTONES DE AÑADIR
        # ----------------------------------

        # Los dos botones abren el mismo formulario
        self.btnAnadir.clicked.connect(
            self.abrir_formulario
        )

        self.btnNuevoJuego.clicked.connect(
            self.abrir_formulario
        )

        # ----------------------------------
        # CONECTAR BUSCADOR Y FILTROS
        # ----------------------------------

        self.textBuscar.textChanged.connect(
            self.actualizar_catalogo
        )

        self.cmbGenero.currentIndexChanged.connect(
            self.actualizar_catalogo
        )

        self.cmbPlataforma.currentIndexChanged.connect(
            self.actualizar_catalogo
        )

        # ----------------------------------
        # CARGAR INFORMACIÓN INICIAL
        # ----------------------------------

        self.cargar_filtros()

        self.actualizar_catalogo()

        # ----------------------------------
        # MOSTRAR VENTANA
        # ----------------------------------

        self.ventana.show()

    # ==========================================
    # CAMBIAR DE PÁGINA
    # ==========================================

    def cambiar_pagina(self, indice):
        """
        Cambia la página visible del QStackedWidget.

        0 = Inicio
        1 = Biblioteca
        """

        self.contenidoPrincipal.setCurrentIndex(indice)

    # ==========================================
    # ABRIR FORMULARIO
    # ==========================================

    def abrir_formulario(self):
        """
        Abre el formulario para añadir un videojuego.

        Cuando el formulario se cierra después de guardar,
        actualiza automáticamente el catálogo y los filtros.
        """

        try:

            # Creamos el formulario en modo añadir
            formulario = GameForm(self.ventana)

            # Ejecutamos el formulario
            resultado = formulario.ejecutar()

            # Si se ha guardado correctamente
            if resultado == QDialog.DialogCode.Accepted:

                # Actualizamos los filtros
                self.cargar_filtros()

                # Actualizamos el catálogo
                self.actualizar_catalogo()

        except (RuntimeError, OSError) as error:

            QMessageBox.critical(
                self.ventana,
                "Error",
                f"No se ha podido abrir el formulario:\n{error}"
            )

    # ==========================================
    # CARGAR FILTROS
    # ==========================================

    
def cargar_filtros(self):
    
   # Carga los géneros y plataformas desde SQLite y actualiza los desplegables.

    # Desactivamos temporalmente las señales
    self.cmbGenero.blockSignals(True)
    self.cmbPlataforma.blockSignals(True)

    # Limpiamos los desplegables
    self.cmbGenero.clear()
    self.cmbPlataforma.clear()

    # Añadimos las opciones generales
    self.cmbGenero.addItem("Todos los géneros", None)
    self.cmbPlataforma.addItem("Todas las plataformas", None)

    # Consultamos los géneros de SQLite
    generos = database.obtener_generos()

    for genero in generos:
        self.cmbGenero.addItem(genero, genero)

    # Consultamos las plataformas de SQLite
    plataformas = database.obtener_plataformas()

    for plataforma in plataformas:
        self.cmbPlataforma.addItem(plataforma, plataforma)

    # Reactivamos las señales
    self.cmbGenero.blockSignals(False)
    self.cmbPlataforma.blockSignals(False)


    # ==========================================
    # ACTUALIZAR CATÁLOGO
    # ==========================================

    def actualizar_catalogo(self):
        """
        Consulta SQLite y muestra los videojuegos
        que coinciden con los filtros seleccionados.
        """

        # Obtener valores de los filtros
        genero = self.cmbGenero.currentData()

        plataforma = self.cmbPlataforma.currentData()

        texto = self.textBuscar.text().strip()

        # Consultar videojuegos
        videojuegos = database.filtrar_videojuegos(
            genero=genero,
            plataforma=plataforma,
            texto=texto
        )

        # ----------------------------------
        # BORRAR RESULTADOS ANTERIORES
        # ----------------------------------

        while self.layoutTarjetas.count():

            elemento = self.layoutTarjetas.takeAt(0)

            widget = elemento.widget()

            if widget is not None:
                widget.deleteLater()

        # ----------------------------------
        # COMPROBAR SI HAY RESULTADOS
        # ----------------------------------

        if not videojuegos:

            etiqueta = QLabel(
                "No se encontraron videojuegos."
            )

            etiqueta.setStyleSheet("""
                QLabel {
                    color: white;
                    padding: 15px;
                }
            """)

            self.layoutTarjetas.addWidget(etiqueta)

            return

        # ----------------------------------
        # MOSTRAR VIDEOJUEGOS
        # ----------------------------------

        for juego in videojuegos:

            (
                id_juego,
                titulo,
                genero,
                plataforma,
                anio,
                puntuacion
            ) = juego

            # Crear una etiqueta provisional
            etiqueta = QLabel(
                f"{titulo} | "
                f"{genero or 'Sin género'} | "
                f"{plataforma or 'Sin plataforma'} | "
                f"{anio if anio is not None else 'Sin año'} | "
                f"Nota: {puntuacion if puntuacion is not None else 'Sin nota'}"
            )

            # Aplicar estilos
            etiqueta.setStyleSheet("""
                QLabel {
                    background-color: #292B40;
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 5px;
                }
            """)

            # Añadir al catálogo
            self.layoutTarjetas.addWidget(etiqueta)


# ==========================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================

if __name__ == "__main__":

    # Crear la aplicación
    app = QApplication(sys.argv)

    # Crear la ventana principal
    aplicacion = GameDex()

    # Iniciar el bucle de eventos
    sys.exit(app.exec())