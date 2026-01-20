import os
import sys # Asegúrate de tener este import al inicio
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,QApplication,
                               QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,
                               QMessageBox,QTreeWidgetItem, QHeaderView , QFileDialog
                               )
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt,QSize
import sqlite3
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer
from exportar import exportar_a_excel 
from PySide6 import QtGui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from datetime import datetime
from fpdf import FPDF

class VentanaIngenieria(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.join(base_dir, "ingenieria.ui")
        
        loader = QUiLoader()
        ui_file = QFile(ruta_ui)
        
        if ui_file.open(QFile.ReadOnly):
            # 1. Cargamos el diseño
            self.ui_content = loader.load(ui_file)
            ui_file.close()
            
            # 2. Creamos el contenedor central para el QMainWindow
            # Esto evita que la pantalla salga en blanco
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 3. Layout que "estira" tu ingenieria.ui al máximo
            layout = QVBoxLayout(central_widget)
            layout.addWidget(self.ui_content)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.setWindowTitle("AutoMetrics 3.0 - Ingeniería")
            self.resize(self.ui_content.size())
            


            # 4. Conectar el botón de la Menu Bar para volver
            #inventario prototipos
            # Conectar acciones a cambio de página en el stackedWidget_2
            # Conectar acciones a cambio de página sincronizado
            # Suponiendo que el stackedWidget_principal contiene al stackedWidget_2 en su Índice 0
            self.ui_content.actionDASHBOARD.triggered.connect(lambda: self.cambiar_pestana(0, 0))
            self.ui_content.actionCRUD.triggered.connect(lambda: self.cambiar_pestana(0, 1))
            self.ui_content.actionANAL_TICA.triggered.connect(lambda: self.cambiar_pestana(0, 2))

            
            



            #inventario prototipos
            
            self.ruta_db = os.path.join(os.path.dirname(__file__), "..", "DB", "Autometrics.db")
            # ... resto de tus conexiones ...
            self.cargar_datos_tabla()
            # Al hacer clic en una celda, se dispara la función
            # 1. Cargar imagen por defecto al abrir
            QTimer.singleShot(50, lambda: self.establecer_imagen("seleccione_algo"))
            
            # 2. Conectar el clic de la tabla
            self.ui_content.tableWidget_inventario.cellClicked.connect(self.actualizar_imagen_y_campos)

            # 3. Conectar el botón Agregar
            self.ui_content.push_anadir.clicked.connect(self.agregar_prototipo)

            # 4. Conectar el botón Eliminar
            self.ui_content.push_eliminar.clicked.connect(self.eliminar_prototipo)

            # 5. Conectar el botón Actualizar
            self.ui_content.push_actualizar.clicked.connect(self.actualizar_prototipo)

            # 6. Conectar el botón Exportar a Excel
            self.ui_content.push_exportar.clicked.connect(self.ejecutar_exportacion)

            # 7  Cargar el treeWidget categorizado
            self.cargar_tree_categorizado()

            # 8 obtener datos de la tabla y ponerlos en los comboBox
            if not self.ui_content.frame_5.layout():
                layout_grafica = QVBoxLayout(self.ui_content.frame_5)
                self.ui_content.frame_5.setLayout(layout_grafica)
            self.poblar_combos_columnas()

            # 9 Conectar el botón Generar Gráfica
            self.ui_content.push_grafica.clicked.connect(self.generar_grafica)

            # 10 transformar conclusión en un archivo pdf
            
            self.ui_content.pushButton_pdf.clicked.connect(self.generar_reporte_pdf)

            # 11 generar grafica relevante en el qframe
            if not self.ui_content.frame_grafica.layout():
                layout_grafica = QVBoxLayout(self.ui_content.frame_grafica)
                self.ui_content.frame_grafica.setLayout(layout_grafica)
            self.graficar_costo_relevante()

            if not self.ui_content.frame_2.layout():
                self.ui_content.frame_2.setLayout(QVBoxLayout(self.ui_content.frame_2))
            self.graficar_rendimiento_firmware()

            
            if not self.ui_content.frame_3.layout():
                self.ui_content.frame_3.setLayout(QVBoxLayout(self.ui_content.frame_3))
            self.graficar_distribucion_ubicacion()

    
            if not self.ui_content.frame_4.layout():
                self.ui_content.frame_4.setLayout(QVBoxLayout(self.ui_content.frame_4))
            self.graficar_analisis_costo_uso()


    def cambiar_pestana(self, indice_principal, indice_secundario):
        # 1. Primero aseguramos que el contenedor principal muestre la página donde está el stackedWidget_2
        self.ui_content.stackedWidget_principal.setCurrentIndex(indice_principal)
        
        # 2. Luego movemos el stackedWidget_2 a la sub-página deseada (Dashboard, CRUD o Analítica)
        self.ui_content.stackedWidget_2.setCurrentIndex(indice_secundario)
        
        # 3. Opcional: Refrescar gráficas si entramos a Analítica (índice 2)
        if indice_secundario == 2:
            self.refrescar_dashboard_ingenieria()

    def closeEvent(self, event):
        """Este método se activa al tocar la X"""
        try:
            print("🛑 Cerrando AutoMetrics 3.0 por completo...")
            event.accept() # Aceptamos el cierre de la ventana
            QApplication.quit() # Cerramos el motor de la app
        except Exception as e:
            # Si algo falla, forzamos la salida para liberar la terminal
            sys.exit()


    # 5. Método para cargar datos en la tabla desde la base de datos
    # inventario_prototipos

    def cargar_datos_tabla(self):
        # 1. Rutas universales (como ya lo tienes configurado)
        carpeta_interfaz = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(carpeta_interfaz)
        ruta_db = os.path.join(ruta_raiz, "DB", "Autometrics.db")
        
        try:
            conexion = sqlite3.connect(ruta_db)
            cursor = conexion.cursor()
            
            # 2. Consulta de datos
            query = "SELECT id_chasis, estado_disponibilidad, kilometraje_horas, ubicacion_fisica, version_firmware, costo_construccion FROM inventario_prototipos"
            cursor.execute(query)
            datos = cursor.fetchall()
            
            # 3. Configuración visual de la tabla
            tabla = self.ui_content.tableWidget_inventario
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(6)
            
            # --- MEJORAS SOLICITADAS ---
            # A. Poner los nombres de las columnas
            columnas = ["ID Chasis", "Estado", "Km/Horas", "Ubicación", "Firmware", "Costo ($)"]
            tabla.setHorizontalHeaderLabels(columnas)
            
            # B. Quitar los índices de las filas (los números 1, 2, 3 de la izquierda)
            tabla.verticalHeader().setVisible(False)
            
            # C. Hacer que las columnas ocupen todo el ancho de la tabla
            header = tabla.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            
            # D. Opcional: Quitar los índices de las columnas si los hubiera (ya los reemplazamos con etiquetas)
            # ---------------------------

            # 4. Llenado de datos
            for row_number, row_data in enumerate(datos):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    tabla.setItem(row_number, column_number, item)
            
            conexion.close()
            
            # Confirmación en la consola (textBrowser)
            self.ui_content.textBrowser.append(f"> [SISTEMA] {len(datos)} registros visualizados correctamente.")

        except sqlite3.Error as e:
            print(f"Error: {e}")


    #label encargado de subir las imagenes de prototipos

    def establecer_imagen(self, nombre_archivo):
        """Carga imágenes asegurando que el tamaño sea constante"""
        carpeta_interfaz = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(carpeta_interfaz)
        
        nombre_limpio = nombre_archivo.strip()
        ruta_imagen = os.path.join(ruta_raiz, "IMAGENES", "prototipo", f"{nombre_limpio}.png")

        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            
            # --- SOLUCIÓN AL TAMAÑO PEQUEÑO ---
            # Intentamos obtener el tamaño actual del label
            ancho = self.ui_content.label_imagen.width()
            alto = self.ui_content.label_imagen.height()

            # Si el ancho es muy pequeño (menor a 100px), significa que la UI no ha cargado.
            # En ese caso, usamos un tamaño fijo basado en tu diseño de Qt Designer.
            # Ajusta estos números (ej. 400x300) a lo que mide tu label en el Designer.
            if ancho < 100:
                ancho = 400  
                alto = 250   

            self.ui_content.label_imagen.setPixmap(pixmap.scaled(
                ancho, alto, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            self.ui_content.label_imagen.setAlignment(Qt.AlignCenter)
            # ----------------------------------
        else:
            self.ui_content.label_imagen.setText(f"Error: {nombre_limpio}.png")

    def actualizar_imagen_y_campos(self, fila, columna):

        try:
            # 1. Extraer datos de la fila seleccionada en la tabla
            id_chasis = self.ui_content.tableWidget_inventario.item(fila, 0).text()
            estado = self.ui_content.tableWidget_inventario.item(fila, 1).text()
            kilometraje = self.ui_content.tableWidget_inventario.item(fila, 2).text()
            ubicacion = self.ui_content.tableWidget_inventario.item(fila, 3).text()
            version = self.ui_content.tableWidget_inventario.item(fila, 4).text()
            costo = self.ui_content.tableWidget_inventario.item(fila, 5).text()

            # 2. Enviar los datos a los LineEdits
            # Usamos los nombres de objeto que tienes en tu Designer
            self.ui_content.lineEdit_chasis.setText(id_chasis)
            self.ui_content.txt_estado.setText(estado)
            self.ui_content.txt_kilometraje.setText(kilometraje)
            self.ui_content.txt_ubicacion.setText(ubicacion)
            self.ui_content.txt_version.setText(version)
            self.ui_content.txt_costo.setText(costo)

            # 3. Actualizar la imagen técnica (Look & Feel v2.0)
            self.establecer_imagen(estado)
            
            # 4. Feedback en la consola
            self.ui_content.textBrowser.append(f"> [SISTEMA]: Editando prototipo {id_chasis}...")

        except AttributeError:
            # Por si el usuario hace clic en una celda vacía
            pass


        # Obtenemos el texto exacto de la columna 'Estado' (columna 1)
        item_estado = self.ui_content.tableWidget_inventario.item(fila, 1)
        
        if item_estado:
            estado_texto = item_estado.text()
            # Llamamos a la función con el nombre del estado
            self.establecer_imagen(estado_texto)
            
            # Log para depuración en tu textBrowser
            self.ui_content.textBrowser.append(f"> [LOG] Buscando imagen para estado: {estado_texto}")
        else:
            self.establecer_imagen("seleccione_algo")


    #boton añadir
    def agregar_prototipo(self):
        # 1. Obtener la ruta de la DB (misma lógica que antes)
        carpeta_interfaz = os.path.dirname(os.path.abspath(__file__))
        ruta_raiz = os.path.dirname(carpeta_interfaz)
        ruta_db = os.path.join(ruta_raiz, "DB", "Autometrics.db")
        
        # 2. Capturar los datos de los LineEdits
        id_chasis = self.ui_content.lineEdit_chasis.text().strip()
        estado = self.ui_content.txt_estado.text().strip()
        km = self.ui_content.txt_kilometraje.text().strip()
        ubicacion = self.ui_content.txt_ubicacion.text().strip()
        version = self.ui_content.txt_version.text().strip()
        costo = self.ui_content.txt_costo.text().strip()


        if not id_chasis:
            QMessageBox.warning(self, "Campos Incompletos", "El ID de Chasis es obligatorio para el registro.")
            return

        try:
            # 1. Ejecutar la inserción en la DB
            conexion = sqlite3.connect(ruta_db)
            cursor = conexion.cursor()
            
            query = """INSERT INTO inventario_prototipos 
                    (id_chasis, estado_disponibilidad, kilometraje_horas, ubicacion_fisica, version_firmware, costo_construccion) 
                    VALUES (?, ?, ?, ?, ?, ?)"""
            
            cursor.execute(query, (id_chasis, estado, km, ubicacion, version, costo))
            conexion.commit()
            conexion.close()

            # 2. MOSTRAR MENSAJE DE ÉXITO
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Registro Exitoso")
            msg.setText(f"El prototipo {id_chasis} ha sido añadido correctamente.")
            msg.setInformativeText("La tabla de inventario se ha actualizado.")
            msg.setStyleSheet("QLabel{ color: white; } QMessageBox{ background-color: #1e1e1e; }") # Estilo Dark
            msg.exec()

            # 3. Refrescar y limpiar
            self.cargar_datos_tabla()
            self.limpiar_campos()
            self.ui_content.textBrowser.append(f"> [SISTEMA]: Registro {id_chasis} confirmado.")

        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error de Duplicidad", f"El ID {id_chasis} ya existe en la base de datos.")
        except Exception as e:
            QMessageBox.critical(self, "Error de Sistema", f"No se pudo guardar el registro: {str(e)}")

    #limpiar campos despues de usar un boton
    def limpiar_campos(self):
        """Limpia los campos después de añadir para nuevo registro"""
        self.ui_content.lineEdit_chasis.clear()
        self.ui_content.txt_estado.clear()
        self.ui_content.txt_kilometraje.clear()
        self.ui_content.txt_ubicacion.clear()
        self.ui_content.txt_version.clear()
        self.ui_content.txt_costo.clear()
        self.establecer_imagen("seleccione_algo")


          
    #boton para elimnar datos de la tabla inventario prototipos
    def eliminar_prototipo(self):
        # 1. Obtener el ID del chasis desde el LineEdit
        id_chasis = self.ui_content.lineEdit_chasis.text().strip()

        if not id_chasis:
            QMessageBox.warning(self, "Atención", "Por favor, selecciona un prototipo de la tabla para eliminar.")
            return

        # 2. Ventana de Confirmación (Crucial para la UX)
        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar permanentemente el prototipo {id_chasis}?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            try:
                # 3. Conexión y Ejecución
                carpeta_interfaz = os.path.dirname(os.path.abspath(__file__))
                ruta_raiz = os.path.dirname(carpeta_interfaz)
                ruta_db = os.path.join(ruta_raiz, "DB", "Autometrics.db")

                conexion = sqlite3.connect(ruta_db)
                cursor = conexion.cursor()
                
                # Borramos usando el ID único
                query = "DELETE FROM inventario_prototipos WHERE id_chasis = ?"
                cursor.execute(query, (id_chasis,))
                
                # Verificar si realmente se borró algo (por si el ID no existe en DB)
                if cursor.rowcount > 0:
                    conexion.commit()
                    QMessageBox.information(self, "Eliminado", f"El prototipo {id_chasis} ha sido removido del sistema.")
                    
                    # 4. Actualizar Interfaz
                    self.cargar_datos_tabla()
                    self.limpiar_campos()
                    self.ui_content.textBrowser.append(f"> [BORRADO]: Registro {id_chasis} eliminado con éxito.")
                else:
                    QMessageBox.warning(self, "Error", "El registro no se encontró en la base de datos.")
                
                conexion.close()

            except Exception as e:
                QMessageBox.critical(self, "Error de Sistema", f"Error al eliminar: {str(e)}")


    #boton para actualizar los datos de la tabla inventario prototipos
    def actualizar_prototipo(self):
        # 1. Capturar el ID (Llave principal) y los nuevos datos
        id_chasis = self.ui_content.lineEdit_chasis.text().strip()
        
        if not id_chasis:
            QMessageBox.warning(self, "Atención", "No hay un ID de chasis válido para actualizar.")
            return

        # Capturar los nuevos valores de los campos
        nuevo_estado = self.ui_content.txt_estado.text().strip()
        nuevo_km = self.ui_content.txt_kilometraje.text().strip()
        nueva_ubicacion = self.ui_content.txt_ubicacion.text().strip()
        nueva_version = self.ui_content.txt_version.text().strip()
        nuevo_costo = self.ui_content.txt_costo.text().strip()

        try:
            # 2. Configurar ruta y conexión
            carpeta_interfaz = os.path.dirname(os.path.abspath(__file__))
            ruta_raiz = os.path.dirname(carpeta_interfaz)
            ruta_db = os.path.join(ruta_raiz, "DB", "Autometrics.db")

            conexion = sqlite3.connect(ruta_db)
            cursor = conexion.cursor()
            
            # 3. Ejecutar sentencia UPDATE
            query = """UPDATE inventario_prototipos 
                    SET estado_disponibilidad = ?, 
                        kilometraje_horas = ?, 
                        ubicacion_fisica = ?, 
                        version_firmware = ?, 
                        costo_construccion = ? 
                    WHERE id_chasis = ?"""
            
            cursor.execute(query, (nuevo_estado, nuevo_km, nueva_ubicacion, nueva_version, nuevo_costo, id_chasis))
            
            if cursor.rowcount > 0:
                conexion.commit()
                QMessageBox.information(self, "Éxito", f"Datos del prototipo {id_chasis} actualizados correctamente.")
                
                # 4. Refrescar la tabla para ver los cambios
                self.cargar_datos_tabla()
                self.ui_content.textBrowser.append(f"> [ACTUALIZAR]: Cambios guardados para {id_chasis}.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró el registro para actualizar.")
                
            conexion.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la base de datos: {str(e)}")

    
    #boton para exportar los datos de la tabla inventario prototipos a excel

    def ejecutar_exportacion(self):
        resultado = exportar_a_excel("inventario_prototipos")
        
        if resultado is True:
            QMessageBox.information(self, "Éxito", "El archivo Excel se generó correctamente.")
            self.ui_content.textBrowser.append("> [REPORTE]: Excel generado con éxito.")
        elif resultado == "vacia":
            QMessageBox.warning(self, "Aviso", "No hay datos en la tabla para exportar.")
        elif resultado is False:
            pass # El usuario cerró la ventana sin guardar
        else:
            QMessageBox.critical(self, "Error", f"Falló la exportación: {resultado}")

    
    #treewidget analítica
    def cargar_tree_categorizado(self):
        # 1. Configuración de columnas
        self.ui_content.treeWidget_tabla.setColumnCount(6)
        self.ui_content.treeWidget_tabla.setHeaderLabels([
            "ID Chasis", "Kilometraje", "Ubicación", "Versión", "Costo", "Fecha Registro"
        ])
        
        # Estiramiento de columnas para evitar el "apeñuscamiento"
        header = self.ui_content.treeWidget_tabla.header()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.ui_content.treeWidget_tabla.clear()

        try:
            # Usar self.ruta_db (asegúrate que esté definida en el __init__)
            conexion = sqlite3.connect(self.ruta_db) 
            cursor = conexion.cursor()
            
            # 1. Obtener estados únicos
            cursor.execute("SELECT DISTINCT estado_disponibilidad FROM inventario_prototipos")
            estados = cursor.fetchall()

            for estado_tuple in estados:
                estado_nombre = str(estado_tuple[0])
                
                # 2. Crear la Carpeta (Padre)
                carpeta = QTreeWidgetItem(self.ui_content.treeWidget_tabla)
                carpeta.setText(0, f"📁 {estado_nombre.upper()}") # Se pone en la columna 0
                carpeta.setExpanded(True)
                carpeta.setForeground(0, QtGui.QColor("#00F0FF")) # Color neón

                # 3. Traer prototipos de este estado
                query = """SELECT id_chasis, kilometraje_horas, ubicacion_fisica, 
                                version_firmware, costo_construccion, fecha_registro 
                        FROM inventario_prototipos WHERE estado_disponibilidad = ?"""
                cursor.execute(query, (estado_nombre,))
                prototipos = cursor.fetchall()

                for p in prototipos:
                    # 4. Crear el Prototipo (Hijo)
                    item = QTreeWidgetItem(carpeta)
                    # Llenamos cada columna con su dato correspondiente
                    item.setText(0, str(p[0])) # ID Chasis
                    item.setText(1, f"{p[1]} hrs")
                    item.setText(2, str(p[2]))
                    item.setText(3, str(p[3]))
                    item.setText(4, f"${p[4]:,.2f}") # Formato moneda
                    item.setText(5, str(p[5]))

            conexion.close()
        except Exception as e:
            # Esto te avisará si falta la ruta o hay otro error
            self.ui_content.textBrowser.append(f'<span style="color:#FF0033;">> [ERROR TREE]: {str(e)}</span>')


    #llena los comboBox con los nombres de las columnas de la tabla inventario prototipos
    def poblar_combos_columnas(self):
            columnas = [
                "id_chasis", "kilometraje_horas", "costo_construccion", 
                "estado_disponibilidad", "version_firmware", "ubicacion_fisica"
            ]
            self.ui_content.comboBox_opcion.addItems(columnas)
            self.ui_content.comboBox_Opcion.addItems(columnas)
        
    #se encarga de graficar los datos seleccionados en los comboBox
    def generar_grafica(self):
        eje_x = self.ui_content.comboBox_opcion.currentText()
        eje_y = self.ui_content.comboBox_Opcion.currentText()

        try:
            # 1. Limpiar el frame y CERRAR figuras previas para liberar memoria
            plt.close('all') 
            layout = self.ui_content.frame_5.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # 2. Obtener datos
            conexion = sqlite3.connect(self.ruta_db)
            df = pd.read_sql_query("SELECT * FROM inventario_prototipos", conexion)
            conexion.close()

            # 3. Crear figura con estilo oscuro
            fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#121212')

            # 4. Lógica de Graficado con NOMBRES (Labels)
            # Si el eje Y es numérico, agrupamos para evitar el desorden del gráfico de pastel
            if df[eje_y].dtype in ['int64', 'float64']:
                # Agrupamos por eje X y sumamos Y
                df_plot = df.groupby(eje_x)[eje_y].sum().nlargest(10) # Top 10 para que sea legible
                
                # Cambiamos a gráfico de BARRAS si hay muchos datos (más legible que el pastel)
                df_plot.plot(kind='bar', ax=ax, color='#00F0FF', edgecolor='white')
                ax.set_title(f"Distribución de {eje_y} por {eje_x}", color='#00F0FF', pad=20)
            else:
                # Si es texto, hacemos el conteo para el gráfico de pastel
                conteo = df[eje_x].value_counts().nlargest(8) # Limitamos a 8 sectores para ver los nombres
                conteo.plot(kind='pie', ax=ax, autopct='%1.1f%%', 
                            labels=conteo.index, # ESTO MUESTRA LOS NOMBRES
                            textprops={'color':"w", 'fontsize': 8},
                            colors=['#00F0FF', '#FF3131', '#00FF66', '#FFCC00', '#9933FF'])
                ax.set_ylabel('')

            # 5. Ajustes finales de visibilidad
            ax.tick_params(colors='white', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('#444')
                
            plt.tight_layout()

            # 6. Mostrar en la interfaz
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            
        except Exception as e:
            self.ui_content.textBrowser.append(f'<span style="color:#FF3131;">> [ERROR]: {str(e)}</span>')


    #genera un reporte en pdf con la conclusion del analisis de datos
    def generar_reporte_pdf(self):
        # 1. Obtener la ruta de guardado
        ruta_guardado, _ = QFileDialog.getSaveFileName(
            self, "Exportar Reporte", "Reporte_Analitica.pdf", "PDF (*.pdf)"
        )

        if not ruta_guardado:
            return

        try:
            # 2. Capturar el texto de la conclusión (Asegúrate que el nombre coincida con tu UI)
            # Usamos toPlainText() para extraer el texto sin formato HTML
            conclusion_texto = self.ui_content.textEdit_conclusion.toPlainText()

            # 3. Capturar la gráfica del frame_5
            layout = self.ui_content.frame_5.layout()
            if layout and layout.count() > 0:
                canvas = layout.itemAt(0).widget()
                ruta_temp_img = "temp_chart.png"
                # Guardamos con el mismo fondo oscuro que tiene la UI
                canvas.figure.savefig(ruta_temp_img, facecolor='#121212', bbox_inches='tight')
            else:
                QMessageBox.warning(self, "Atención", "No hay ninguna gráfica para exportar.")
                return

            # 4. Configuración del PDF Dark Mode
            pdf = FPDF()
            pdf.add_page()
            
            # PINTAR FONDO OSCURO EN TODA LA HOJA
            pdf.set_fill_color(18, 18, 18) # Color #121212
            pdf.rect(0, 0, 210, 297, 'F')

            # ENCABEZADO
            pdf.set_font("Arial", 'B', 22)
            pdf.set_text_color(0, 240, 255) # Cian Neón
            pdf.cell(0, 15, "AUTOMETRICS 3.0 - REPORT", ln=True, align='C')
            
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(150, 150, 150) # Gris
            pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
            pdf.ln(10)

            # INSERTAR GRÁFICA (Centrada)
            pdf.image(ruta_temp_img, x=15, w=180)
            pdf.ln(10)

            # SECCIÓN DE CONCLUSIONES
            pdf.set_draw_color(0, 240, 255) # Línea divisoria cian
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 16)
            pdf.set_text_color(0, 240, 255)
            pdf.cell(0, 10, "CONCLUSIONES DEL ANALISTA:", ln=True)
            pdf.ln(3)

            # TEXTO DE LA CONCLUSIÓN (Letra grande y legible)
            pdf.set_font("Arial", '', 14)
            pdf.set_text_color(255, 255, 255) # Blanco para legibilidad
            # multi_cell permite que el texto haga salto de línea automático
            pdf.multi_cell(0, 10, conclusion_texto)

            # 5. Guardar y Limpiar
            pdf.output(ruta_guardado)
            if os.path.exists(ruta_temp_img):
                os.remove(ruta_temp_img)

            self.ui_content.textBrowser.append(f'<span style="color:#00FF66;">> [EXITO]: Reporte generado en {ruta_guardado}</span>')
            QMessageBox.information(self, "Reporte Listo", "El PDF se ha guardado correctamente.")

        except Exception as e:
            self.ui_content.textBrowser.append(f'<span style="color:#FF3131;">> [ERROR PDF]: {str(e)}</span>')



    # graficas de los qframe
    def graficar_costo_relevante(self):
        try:
            # 1. Limpieza segura (Aquí es donde fallaba antes si no había layout)
            plt.close('all')
            layout = self.ui_content.frame_grafica.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # 2. Obtención de datos reales de la DB
            conexion = sqlite3.connect(self.ruta_db)
            # Agrupamos por estado y sumamos costos
            query = "SELECT estado_disponibilidad, SUM(costo_construccion) as total FROM inventario_prototipos GROUP BY estado_disponibilidad"
            df = pd.read_sql_query(query, conexion)
            conexion.close()

            # 3. Configuración Dark Mode para el PDF y la UI
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#121212')

            # Graficar barras en Cian Neón
            df.plot(kind='bar', x='estado_disponibilidad', y='total', ax=ax, color='#00F0FF', legend=False)

            # Estética de los ejes
            ax.set_title("VALOR TOTAL POR ESTADO DE DISPONIBILIDAD", color='#00F0FF', pad=15)
            ax.tick_params(colors='white', labelsize=8)
            ax.xaxis.label.set_color('#00F0FF')
            plt.xticks(rotation=45)
            
            # Evitar notación científica en el costo (mostrar números claros)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

            plt.tight_layout()

            # 4. Mostrar en el Frame
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

        except Exception as e:
            self.ui_content.textBrowser.append(f'<span style="color:#FF3131;">> [ERROR]: {str(e)}</span>')

    def graficar_rendimiento_firmware(self):
        try:
            # 1. Limpieza del frame
            plt.close('all')
            layout = self.ui_content.frame_2.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            # 2. Consulta de Datos Relevantes
            conexion = sqlite3.connect(self.ruta_db)
            # Obtenemos el promedio de kilometraje agrupado por versión
            query = """SELECT version_firmware, AVG(kilometraje_horas) as promedio_km 
                    FROM inventario_prototipos 
                    GROUP BY version_firmware 
                    ORDER BY version_firmware ASC"""
            df = pd.read_sql_query(query, conexion)
            conexion.close()

            # 3. Diseño de la Gráfica (Estilo Línea Neón)
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#121212')

            # Dibujar línea con marcadores circulares
            ax.plot(df['version_firmware'], df['promedio_km'], 
                    color='#00FF66',      # Verde Neón para variar del Cian
                    marker='o', 
                    markersize=8, 
                    linewidth=2, 
                    markerfacecolor='#121212', 
                    markeredgecolor='#00FF66')

            # Estética de Ejes
            ax.set_title("RENDIMIENTO: KM PROMEDIO POR FIRMWARE", color='#00FF66', pad=15, fontweight='bold')
            ax.tick_params(colors='white', labelsize=8)
            ax.set_ylabel("Kilometraje (Hrs)", color='white')
            ax.grid(True, linestyle='--', alpha=0.2, color='white') # Cuadrícula sutil

            plt.tight_layout()

            # 4. Integración en la UI
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

        except Exception as e:
            self.ui_content.textBrowser.append(f'<span style="color:#FF3131;">> [ERROR FRAME 2]: {str(e)}</span>')

    def graficar_distribucion_ubicacion(self):
        try:
            # 1. Limpieza del frame
            plt.close('all')
            layout = self.ui_content.frame_3.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            # 2. Obtener datos: Conteo por Ubicación
            conexion = sqlite3.connect(self.ruta_db)
            query = "SELECT ubicacion_fisica, COUNT(*) as cantidad FROM inventario_prototipos GROUP BY ubicacion_fisica"
            df = pd.read_sql_query(query, conexion)
            conexion.close()

            # 3. Diseño del Gráfico de Pastel
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#121212')

            # Colores neón para las rebanadas
            colores = ['#FF3131', '#00F0FF', '#00FF66', '#FFCC00', '#FF00FF']

            # Crear el Pie Chart
            wedges, texts, autotexts = ax.pie(
                df['cantidad'], 
                labels=df['ubicacion_fisica'], 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=colores,
                textprops={'color': "w", 'fontsize': 9}
            )

            # Hacer que los porcentajes dentro sean más visibles
            for autotext in autotexts:
                autotext.set_fontweight('bold')

            ax.set_title("DISPONIBILIDAD POR PLANTA / UBICACIÓN", color='white', pad=10, fontweight='bold')

            plt.tight_layout()

            # 4. Integración en la UI
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

        except Exception as e:
            self.ui_content.textBrowser.append(f'<span style="color:#FF3131;">> [ERROR FRAME 3]: {str(e)}</span>')


    def graficar_analisis_costo_uso(self):
        try:
            # 1. Limpieza del frame
            plt.close('all')
            layout = self.ui_content.frame_4.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            # 2. Obtener datos: Costo vs Kilometraje
            conexion = sqlite3.connect(self.ruta_db)
            query = "SELECT costo_construccion, kilometraje_horas, estado_disponibilidad FROM inventario_prototipos"
            df = pd.read_sql_query(query, conexion)
            conexion.close()

            # 3. Diseño del Gráfico de Dispersión (Scatter)
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#121212')

            # Dibujar los puntos con un degradado neón
            scatter = ax.scatter(
                df['kilometraje_horas'], 
                df['costo_construccion'], 
                c=df['costo_construccion'], # El color varía según el costo
                cmap='cool',                # Escala de cian a morado neón
                alpha=0.6, 
                edgecolors='white',
                linewidth=0.5
            )

            # Estética de Ejes y Títulos
            ax.set_title("ANÁLISIS DE RETORNO: COSTO VS USO", color='#00F0FF', pad=15, fontweight='bold')
            ax.set_xlabel("Uso Acumulado (Horas/Km)", color='white', fontsize=8)
            ax.set_ylabel("Inversión (USD)", color='white', fontsize=8)
            
            ax.tick_params(colors='white', labelsize=7)
            ax.grid(True, linestyle=':', alpha=0.3, color='white')

            # Formatear el eje Y como moneda
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))

            plt.tight_layout()

            # 4. Integración en la UI
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

        except Exception as e:
            self.ui_content.textBrowser.append(f'<span style="color:#FF3131;">> [ERROR FRAME 4]: {str(e)}</span>')
        

            
    


           