# Ejemplo de uso:
# extraer_ultima_columna("2024_consolidado")

import pandas as pd
from pathlib import Path

def extraer_ultima_columna(nombre_archivo):
    """
    Extrae la última columna de un archivo CSV y la guarda como archivo .txt
    
    Args: nombre_archivo (str): Nombre del archivo CSV (sin extensión ni ruta)
    Ejemplo: "2024_consolidado"
    """
    
    # Construir rutas
    ruta_entrada = Path(f"data/processed/{nombre_archivo}.csv")
    nombre_salida = f"{nombre_archivo}_solo_amax.txt"
    ruta_salida = Path(f"data/processed/{nombre_salida}")
    
    # Verificar que el archivo de entrada existe
    if not ruta_entrada.exists():
        print(f"❌ Error: El archivo {ruta_entrada} no existe.")
        return
    
    try:
        # Leer el CSV original (con encabezado, separador ; y decimal ,)
        df = pd.read_csv(ruta_entrada, sep=";", decimal=",")
        
        # Seleccionar solo la última columna
        ultima_columna = df.iloc[:, [-4]]
        
        # Guardar sin encabezado y sin índice
        ultima_columna.to_csv(ruta_salida, sep=";", decimal=",", index=False, header=False)
        
        print(f"✅ Archivo guardado: {nombre_salida}")
        print(f"📊 Registros procesados: {len(ultima_columna):,}")
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")


import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Debes indicar el nombre del archivo sin extensión.")
        print("🧭 Ejemplo: python src/limpieza/solo_amax.py 2024_consolidado_extra_rge_inferior")
    else:
        nombre = sys.argv[1]
        extraer_ultima_columna(nombre)







