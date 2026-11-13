
# ==========================================
# GAMEDEX
# Archivo: game_form.py
# Gestión del formulario de videojuegos
# ==========================================

import os
import sqlite3

from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QLabel,
    QMessageBox
)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

import database


# ==========================================
# CLASE DEL FORMULARIO
# ==========================================

class GameForm:

    def __init__(self, parent=None, videojuego=None):
        """
        Constructor del formulario.

        parent: ventana principal de GameDex.
        videojuego: datos del videojuego que queremos editar.

        Si videojuego es None, estamos añadiendo.
        Si contiene datos, estamos editando.
        """

        # Guardamos el videojuego que queremos editar
        self.videojuego = videojuego

        # Si estamos editando, guardamos su ID
        self.id_videojuego = None

        if videojuego is not None:
            self.id_videojuego = videojuego[0]

        # ----------------------------------
        # CARGAR ARCHIVO UI
        # ----------------------------------

        loader = QUiLoader()

        # Obtener la ruta de la carpeta del proyecto
        ruta_proyecto = os.path.dirname(
            os.path.abspath(__file__)
        )

        # Construir la ruta del formulario
        ruta_ui = os.path.join(
            ruta_proyecto,
            "ui",
            "game_form.ui"
        )

        # Abrir el archivo
        archivo = QFile(ruta_ui)

        if not archivo.open(QFile.OpenModeFlag.ReadOnly):
            raise RuntimeError(
                f"No se encuentra el formulario: {ruta_ui}"
            )

        # Cargar el formulario
        self.dialogo = loader.load(archivo, parent)

        archivo.close()

        if self.dialogo is None:
            raise RuntimeError(
                "No se ha podido cargar game_form.ui"
            )

        # ----------------------------------
        # OBTENER LOS COMPONENTES
        # ----------------------------------

        self.lblTituloForm = self.dialogo.findChild(
            QLabel, "lblTituloForm"
        )

        self.txtTitulo = self.dialogo.findChild(
            QLineEdit, "txtTitulo"
        )

        self.txtGenero = self.dialogo.findChild(
            QLineEdit, "txtGenero"
        )

        self.txtPlataforma = self.dialogo.findChild(
            QLineEdit, "txtPlataforma"
        )

        self.spinAnio = self.dialogo.findChild(
            QSpinBox, "spinAnio"
        )

        self.spinPuntuacion = self.dialogo.findChild(
            QSpinBox, "spinPuntuacion"
        )

        self.btnGuardar = self.dialogo.findChild(
            QPushButton, "btnGuardar"
        )

        self.btnCancelar = self.dialogo.findChild(
            QPushButton, "btnCancelar"
        )

        # Comprobar que todos los componentes existen
        componentes = [
            self.lblTituloForm,
            self.txtTitulo,
            self.txtGenero,
            self.txtPlataforma,
            self.spinAnio,
            self.spinPuntuacion,
            self.btnGuardar,
            self.btnCancelar
        ]

        if any(componente is None for componente in componentes):
            raise RuntimeError(
                "Falta algún componente en game_form.ui. "
                "Comprueba sus nombres en Qt Designer."
            )

        # ----------------------------------
        # CONFIGURAR EL FORMULARIO
        # ----------------------------------

        # Si estamos editando, cargamos los datos
        if self.videojuego is not None:

            self.cargar_datos()

            self.dialogo.setWindowTitle(
                "Editar videojuego"
            )

            self.lblTituloForm.setText(
                "Editar videojuego"
            )

        else:

            self.dialogo.setWindowTitle(
                "Añadir videojuego"
            )

            self.lblTituloForm.setText(
                "Añadir videojuego"
            )

        # ----------------------------------
        # CONECTAR LOS BOTONES
        # ----------------------------------

        # Al pulsar Guardar ejecutamos guardar_videojuego
        self.btnGuardar.clicked.connect(
            self.guardar_videojuego
        )

        # Al pulsar Cancelar cerramos sin guardar
        self.btnCancelar.clicked.connect(
            self.dialogo.reject
        )

    # ======================================
    # CARGAR DATOS PARA EDITAR
    # ======================================

    def cargar_datos(self):
        """
        Introduce en los campos los datos
        del videojuego que queremos modificar.
        """

        # Descomponemos los datos recibidos de SQLite
        (
            id_juego,
            titulo,
            genero,
            plataforma,
            anio,
            puntuacion
        ) = self.videojuego

        # Rellenamos los campos
        self.txtTitulo.setText(titulo)

        self.txtGenero.setText(
            genero if genero else ""
        )

        self.txtPlataforma.setText(
            plataforma if plataforma else ""
        )

        # Cargamos el año si existe
        if anio is not None:
            self.spinAnio.setValue(anio)

        # Cargamos la puntuación si existe
        if puntuacion is not None:
            self.spinPuntuacion.setValue(
                int(puntuacion)
            )

    # ======================================
    # GUARDAR VIDEOJUEGO
    # ======================================

    def guardar_videojuego(self):
        """
        Recoge los datos del formulario,
        los valida y los guarda en SQLite.
        """

        # Recoger los valores escritos
        titulo = self.txtTitulo.text().strip()

        genero = self.txtGenero.text().strip()

        plataforma = self.txtPlataforma.text().strip()

        anio = self.spinAnio.value()

        puntuacion = self.spinPuntuacion.value()

        # ----------------------------------
        # VALIDAR TÍTULO
        # ----------------------------------

        if not titulo:

            QMessageBox.warning(
                self.dialogo,
                "Campo obligatorio",
                "Debes introducir el título del videojuego."
            )

            self.txtTitulo.setFocus()

            return

        # Convertir los campos opcionales vacíos en None
        genero = genero if genero else None

        plataforma = plataforma if plataforma else None

        # ----------------------------------
        # GUARDAR O EDITAR
        # ----------------------------------

        try:

            # Si existe un ID, estamos editando
            if self.id_videojuego is not None:

                actualizado = database.editar_videojuego(
                    self.id_videojuego,
                    titulo,
                    genero,
                    plataforma,
                    anio,
                    puntuacion
                )

                if not actualizado:

                    QMessageBox.warning(
                        self.dialogo,
                        "Aviso",
                        "No se ha encontrado el videojuego."
                    )

                    return

                mensaje = "Videojuego actualizado correctamente."

            else:

                # Si no existe ID, estamos añadiendo
                database.agregar_videojuego(
                    titulo,
                    genero,
                    plataforma,
                    anio,
                    puntuacion
                )

                mensaje = "Videojuego añadido correctamente."

            # ----------------------------------
            # CONFIRMAR OPERACIÓN
            # ----------------------------------

            QMessageBox.information(
                self.dialogo,
                "GameDex",
                mensaje
            )

            # Cerramos el formulario indicando éxito
            self.dialogo.accept()

        except ValueError as error:

            # Errores de validación de database.py
            QMessageBox.warning(
                self.dialogo,
                "Datos incorrectos",
                str(error)
            )

        except sqlite3.Error as error:

            # Errores de SQLite
            QMessageBox.critical(
                self.dialogo,
                "Error de base de datos",
                f"No se ha podido guardar el videojuego:\n{error}"
            )

    # ======================================
    # MOSTRAR EL FORMULARIO
    # ======================================

    def ejecutar(self):
        """
        Muestra el formulario de manera modal.
        Devuelve Accepted si se guardó correctamente
        o Rejected si se canceló.
        """

        return self.dialogo.exec()
