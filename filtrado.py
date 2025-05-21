import pandas as pd
from pathlib import Path

def filtrar_csv_por_columna(ruta_entrada="Test/mpd2024_csv", ruta_salida="Test/mpd2024_csv", columna_objetivo=9, valor_permitido=1):
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(exist_ok=True)
    
    archivos_csv = sorted(ruta_entrada.glob("*.csv"))

    for archivo in archivos_csv:
        print(f"Filtrando: {archivo.name}")
        
        # Leer el CSV sin encabezado, ya que no lo tiene
        df = pd.read_csv(archivo, sep=";", header=None, decimal=",")

        # Filtrar solo filas donde la columna 10 (índice 9) sea igual al valor permitido (por defecto: 1)
        df_filtrado = df[df[columna_objetivo] == valor_permitido]

        # Guardar el archivo filtrado
        nuevo_nombre = ruta_salida / archivo.name
        df_filtrado.to_csv(nuevo_nombre, index=False, sep=";", decimal=",", header=False)

    print("✅ Filtrado completado correctamente.")

filtrar_csv_por_columna()
