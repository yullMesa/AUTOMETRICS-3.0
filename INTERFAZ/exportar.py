import sqlite3
import pandas as pd
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

def exportar_a_excel(nombre_tabla):
    """
    Convierte cualquier tabla de la DB en un archivo Excel (.xlsx).
    """
    # 1. Configuración de rutas relativas
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_raiz = os.path.dirname(directorio_actual)
    ruta_db = os.path.join(ruta_raiz, "DB", "Autometrics.db")

    try:
        # 2. Conexión y extracción de datos con Pandas
        conexion = sqlite3.connect(ruta_db)
        # Cargamos la tabla completa en un DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conexion)
        conexion.close()

        if df.empty:
            return "vacia"

        # 3. Configurar el diálogo para guardar el archivo (.xlsx por defecto)
        # Usamos QFileDialog para mantener la estética de PySide6
        ruta_guardado, _ = QFileDialog.getSaveFileName(
            None, 
            "Guardar Reporte Excel", 
            f"Reporte_{nombre_tabla}.xlsx", 
            "Archivos de Excel (*.xlsx)"
        )

        if ruta_guardado:
            # 4. Motor de escritura para Excel (requiere openpyxl)
            with pd.ExcelWriter(ruta_guardado, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Datos_Prototipos')
            return True
        
        return False # El usuario canceló la ventana

    except Exception as e:
        print(f"Error técnico: {e}")
        return str(e)