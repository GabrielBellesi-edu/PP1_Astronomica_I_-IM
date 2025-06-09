#python src/limpieza/data_cleaning.py

import pandas as pd
from pathlib import Path

def convertir_mpd_a_csv(ruta_mpd="data/raw", ruta_salida="data/interim/conversion", filas_saltadas=29): 
    ruta_mpd = Path(ruta_mpd)      # Ruta a los .mpd
    ruta_csv = Path(ruta_salida)   # Ruta donde guardar los .csv 
    ruta_csv.mkdir(parents=True, exist_ok=True) # Crea la carpeta si no existe

    # Buscar todos los archivos .mpd
    archivos_mpd = sorted(ruta_mpd.glob("mp*.riogrande.mpd"))  
    colspecs = [
    (0, 11),     # Date (YYYY/MM/DD)
    (12, 24),    # Time (hh:mm:ss.sss)
    (25, 30),    # File ID (ej: 00RU0)
    (31, 36),    # Rge
    (37, 43),    # Ht
    (44, 51),    # Vrad
    (52, 58),    # delVr
    (59, 65),    # Theta
    (66, 73),    # Phi0
    (75, 76),    # Ambig
    (80, 85),    # Delphase
    (89, 92),    # ant-pair
    (99, 100),   # IREX
    (102, 109),  # amax
    (110, 114),  # Tau
    (115, 120),  # vmet
    (122, 127),  # snrdb
    ]

    for archivo in archivos_mpd:
        # Notificacion de progreso. 
        print(f"Convirtiendo: {archivo.name}")
        
        # Leer datos ignorando las primeras filas. Avisa al pandas que viene sin header
        df = pd.read_fwf(archivo, skiprows=filas_saltadas, header=None, colspecs=colspecs)

        # Unir fecha y hora en una sola columna datetime
        dt = df[0].astype(str).str.strip() + " " + df[1].astype(str).str.strip()
        df_datetime = pd.to_datetime(dt, format="%Y/%m/%d %H:%M:%S.%f", errors='coerce')
        df.insert(0, "Fecha y hora", df_datetime)
        df = df.drop(columns=[0, 1])  # Elimina columnas originales

        # Nombre de archivo .csv en la nueva carpeta
        nuevo_nombre = ruta_csv / (archivo.stem + ".csv")

        # Guardar como CSV con separador ";" y decimal "," y sin agregar header
        df.to_csv(nuevo_nombre, index=False, sep=";", decimal=",", header=False)

    # Confirmacion de proceso terminado.
    print("✅ Conversión completa.")


def filtro_ambig(ruta_entrada="data/interim/conversion", ruta_salida="data/interim/transformacion", 
                 columna_objetivo=8, valor_permitido=1, #De la columna 8 (ambig) Elimina todos los registros distintos a 1
                 columnas_a_eliminar=[1, 8, 11]): #Elimina las columnas 1 (file) 8 (ambig) y 11 (IREX)

    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(parents=True, exist_ok=True)

    archivos_csv = sorted(ruta_entrada.glob("*.csv"))

    for archivo in archivos_csv:
        print(f"Procesando: {archivo.name}")
        
        # Leer el CSV sin encabezado
        df = pd.read_csv(archivo, sep=";", header=None, decimal=",")

        # Filtrar por ambigüedad
        df_filtrado = df[df[columna_objetivo] == valor_permitido]

        # Eliminar columnas especificadas
        df_resultado = df_filtrado.drop(columns=columnas_a_eliminar)

        # Guardar resultado
        nuevo_nombre = ruta_salida / archivo.name
        df_resultado.to_csv(nuevo_nombre, index=False, sep=";", decimal=",", header=False)

    print("✅ Filtro por ambig completado.")



def filtro_rge(ruta_entrada="data/interim/transformacion", ruta_salida="data/interim/filtrado",
               indice_rge=1, rge_min=100, rge_max=130):

    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(parents=True, exist_ok=True)

    archivos_csv = sorted(ruta_entrada.glob("*.csv"))

    for archivo in archivos_csv:
        print(f"Filtrando por Rge: {archivo.name}")
        
        # Leer archivo filtrado previamente
        df = pd.read_csv(archivo, sep=";", header=None, decimal=",")

        # Aplicar filtro por Rge entre 100 y 130 inclusive
        df_filtrado = df[(df[indice_rge] >= rge_min) & (df[indice_rge] <= rge_max)]

        # Guardar archivo filtrado
        nuevo_nombre = ruta_salida / archivo.name
        df_filtrado.to_csv(nuevo_nombre, index=False, sep=";", decimal=",", header=False)

    print("✅ Filtrado por Rge completado.")



def consolidar_csv(ruta_entrada="data/interim/filtrado", ruta_salida="data/processed/2024_consolidado.csv"):
    ruta_entrada = Path(ruta_entrada)
    archivos_csv = sorted(ruta_entrada.glob("*.csv"))

    # Lista de nombres de columnas, ya que los archivos CSV individuales no tienen encabezado
    columnas = [
        "Fecha y hora", "Rge", "Ht", "Vrad", "delVr",
        "Theta", "Phi0", "Delphase", "ant-pair",
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
        
        # Agregar el DataFrame a la lista
        dataframes.append(df)

    # Unir todos los DataFrames
    df_total = pd.concat(dataframes, ignore_index=True)

    # Agregar columna ID incremental al principio
    df_total.insert(0, 'ID', range(1, len(df_total) + 1))

    df_total.to_csv(ruta_salida, index=False, sep=";", decimal=",")

    print("✅ Consolidación completada.")

if __name__ == "__main__":
    convertir_mpd_a_csv()
    filtro_ambig()
    filtro_rge()
    consolidar_csv()