import pandas as pd
from pathlib import Path

# Ruta a los .csv
ruta_csv = Path("Test/mpd2024_csv")  # MODIFICAR SEGUN CORRESPONDA
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
    print(f"Leyendo: {archivo.name}")

    # Leer el archivo sin encabezado, y asignar los nombres de columnas definidos arriba
    df = pd.read_csv(archivo, header=None, names=columnas)

    # Agregar una nueva columna con el nombre del archivo (sin la extensión)
    # Esto sirve para saber de qué archivo proviene cada fila
    df["archivo"] = archivo.stem  # o una versión limpia si querés

    # Agregar el DataFrame a la lista
    dataframes.append(df)

# Unir todos los DataFrames
df_total = pd.concat(dataframes, ignore_index=True)

# Guardar
df_total.to_csv("Test/datos_consolidados_2024.csv", index=False)

# Mensaje de confirmación al finalizar
print("✅ Consolidación completada sin errores de columnas.")
