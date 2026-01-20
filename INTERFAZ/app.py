import sys
import os
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               )

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sqlite3
from collections import Counter
import subprocess

from ingenieria import VentanaIngenieria


def actualizar_recursos():
    # Rutas basadas en tu estructura profesional
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_qrc = os.path.join(base_dir, "IMAGENES", "recursos.qrc")
    ruta_py = os.path.join(base_dir, "IMAGENES", "recursos_rc.py")

    # Solo compilamos si el archivo .qrc existe
    if os.path.exists(ruta_qrc):
        try:
            # Ejecuta el comando de terminal de forma invisible
            subprocess.run(["pyside6-rcc", ruta_qrc, "-o", ruta_py], check=True)
            print("🔄 Recursos actualizados automáticamente desde el Designer.")
        except Exception as e:
            print(f"⚠️ No se pudo auto-compilar: {e}")



# Detectamos dónde está parado el script
directorio_actual = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel para llegar a 'AUTOMETRICS 3.0'
# Determinamos la raíz del proyecto (AUTOMETRICS 3.0)
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Agregamos la raíz al sistema para que Python vea TODAS las carpetas
if raiz not in sys.path:
    sys.path.insert(0, raiz)

# IMPORTACIÓN TEÓRICA CORRECTA: [Carpeta].[Archivo]
try:
    from IMAGENES import recursos_rc
    print("✅ Pictogramas cargados desde el paquete IMAGENES")
except ImportError as e:
    print(f"❌ Error de importación: {e}")

class VentanaInicio(QDialog):
    def __init__(self,ruta_ui=None,titulo="AutoMetrics 3.0 - Dashboard Profesional"):
        super().__init__()
        # 1. Definir rutas
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ruta_ui = os.path.join(self.base_dir, "INICIO.ui")
        
        # 2. CARGA DE UI MEJORADA
        self.configurar_interfaz()

    def configurar_interfaz(self):
        loader = QUiLoader()
        ui_file = QFile(self.ruta_ui)
        
        if not ui_file.open(QFile.ReadOnly):
            print("No se pudo abrir la UI")
            return

        # IMPORTANTE: Cargamos la UI pero NO la asignamos a self.ui todavía
        # La cargamos como un widget independiente primero
        contenedor_ui = loader.load(ui_file)
        ui_file.close()

        if contenedor_ui:
            # 3. TRANSFERENCIA DE ATRIBUTOS
            # Esto hace que todos los botones (ingeniería, flota, etc.) 
            # existan dentro de 'self' directamente.
            self.ui = contenedor_ui
            
            # Crear el layout para que el contenedor ocupe TODA la ventana
            layout_principal = QVBoxLayout(self)
            layout_principal.addWidget(contenedor_ui)
            layout_principal.setContentsMargins(0, 0, 0, 0)
            
            # Ajustar tamaño al diseño original
            self.setFixedSize(contenedor_ui.size())
            self.setWindowTitle("AutoMetrics 3.0 - Dashboard Profesional")
            
            print("✅ Interfaz cargada y vinculada")
            
            # 4. Conectamos los botones (esto lo haremos en el siguiente paso)
            self.conectar_botones()
            print("🚀 Interfaz desplegada correctamente")


    def conectar_botones(self):
        # Conexión de los botones de navegación
        self.ui.push_sgte.clicked.connect(self.navegar_adelante)
        self.ui.push_atras.clicked.connect(self.navegar_atras)

        #carga de las demas interfaces
        # Conexión del botón de Ingeniería
        if hasattr(self.ui, 'tool_ingenieria'):
            self.ui.tool_ingenieria.clicked.connect(self.abrir_modulo_ingenieria)

    def navegar_adelante(self):
        # 1. Obtenemos el índice actual y el total de pestañas
        indice_actual = self.ui.stackedWidget.currentIndex()
        total_pestañas = self.ui.stackedWidget.count() # Cuenta cuántas páginas hay

        # 2. Lógica de bucle: Si es la última, vuelve a la cero
        if indice_actual == total_pestañas - 1:
            nuevo_indice = 0
        else:
            nuevo_indice = indice_actual + 1
        
        self.ui.stackedWidget.setCurrentIndex(nuevo_indice)
        print(f"Pestaña siguiente: {nuevo_indice}")

    def navegar_atras(self):
        # 1. Obtenemos el índice actual y el total
        indice_actual = self.ui.stackedWidget.currentIndex()
        total_pestañas = self.ui.stackedWidget.count()

        # 2. Lógica de bucle: Si es la cero, va a la última (total - 1)
        if indice_actual == 0:
            nuevo_indice = total_pestañas - 1
        else:
            nuevo_indice = indice_actual - 1
            
        self.ui.stackedWidget.setCurrentIndex(nuevo_indice)
        print(f"Pestaña anterior: {nuevo_indice}")

    
    def abrir_modulo_ingenieria(self):
        self.ventana_ingenieria = VentanaIngenieria(self) # Le pasas el padre
        self.ventana_ingenieria.show()
        self.hide()






# =========================================================
# 3. EJECUCIÓN
# =========================================================

if __name__ == "__main__":

    actualizar_recursos()
    app = QApplication(sys.argv)
    window = VentanaInicio()
    window.show() # <--- ¡Asegúrate de que esto esté presente!
    sys.exit(app.exec())