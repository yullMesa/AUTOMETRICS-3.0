import os
import sys # Asegúrate de tener este import al inicio
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,QApplication,
                               QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView
                               )
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sqlite3

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



            #inventario
            self.cargar_datos_tabla()

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
        # 1. Obtener la ruta del archivo actual (ingenieria.py)
        # Subimos un nivel si es necesario para encontrar la carpeta DB
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        ruta_db = os.path.join(base_dir, "DB", "Autometrics.db")
        
        try:
            conexion = sqlite3.connect(ruta_db)
            cursor = conexion.cursor()
            
            # Consulta de datos
            query = "SELECT id_chasis, estado_disponibilidad, kilometraje_horas, ubicacion_fisica, version_firmware, costo_construccion FROM inventario_prototipos"
            cursor.execute(query)
            datos = cursor.fetchall()
            
            # Configuración de la tabla
            self.ui_content.tableWidget_inventario.setRowCount(len(datos))
            self.ui_content.tableWidget_inventario.setColumnCount(6)
            
            # Llenado de datos
            for row_number, row_data in enumerate(datos):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.ui_content.tableWidget_inventario.setItem(row_number, column_number, item)
            
            conexion.close()
            

        except sqlite3.Error as e:
            # CORRECCIÓN DEL NOMBRE AQUÍ TAMBIÉN
            print(f"Error al conectar: {e}") 
            
    


           