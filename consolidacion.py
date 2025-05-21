# consolidacion.py
import pandas as pd
from pathlib import Path

def consolidar_csv(ruta_csv="Test/mpd2024_csv", salida="Test/datos_consolidados_2024.csv"): # Rutas predeterminadas
    ruta_csv = Path(ruta_csv)
    # Buscar todos los archivos con extensión .csv dentro de esa carpeta
    archivos_csv = sorted(ruta_csv.glob("*.csv"))

    # Lista de nombres de columnas, ya que los archivos CSV no tienen encabezado
    columnas = [
        "Date", "Time", "File", "Rge", "Ht", "Vrad", "delVr",
        "Theta", "Phi0", "Ambig", "Delphase", "ant-pair", "IREX",
        "amax", "Tau", "vmet", "snrdb"
    ]
    
    # Lista vacía para acumular los DataFrames de cada archivo
    dataframes = []

    # Iterar sobre cada archivo CSV individual
    for archivo in archivos_csv:
        # Notificacion de progreso.
        print(f"Leyendo: {archivo.name}")

        # Leer el archivo sin encabezado, asigna los nombres de columnas definidas arriba y usando ; como separador y , como decimal
        df = pd.read_csv(archivo, header=None, names=columnas, sep=";", decimal=",")
        
        # Añadir columna con el nombre del archivo de origen (Para conocer su origen)
        df["archivo"] = archivo.stem

        # Agregar el DataFrame a la lista
        dataframes.append(df)

    # Unir todos los DataFrames
    df_total = pd.concat(dataframes, ignore_index=True)

    # Guardar
    df_total.to_csv(salida, index=False, sep=";",decimal=",")
    
    # Mensaje de confirmación al finalizar
    print("✅ Consolidación completada sin errores de columnas.")

consolidar_csv() # MODIFICAR PARAMETROS SEGUN CORRESPONDA
