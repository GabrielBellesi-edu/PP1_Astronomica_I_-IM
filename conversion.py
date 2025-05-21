# conversion-v4.py
import pandas as pd
from pathlib import Path

def convertir_mpd_a_csv(ruta_mpd="Test/mpd2024", ruta_salida="Test/mpd2024_csv", filas_saltadas=29): # MODIFICAR SEGUN CORRESPONDA
    ruta_mpd = Path(ruta_mpd) # Ruta a los .mpd
    ruta_csv = Path(ruta_salida) # Ruta donde guardar los .csv (puede ser la misma o distinta)
    ruta_csv.mkdir(exist_ok=True) # Crea la carpeta si no existe

    archivos_mpd = sorted(ruta_mpd.glob("mp*.riogrande.mpd"))  # Buscar todos los archivos .mpd
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

        # 👉 Convertir la columna de fecha al formato DD/MM/AAAA
        df[0] = pd.to_datetime(df[0], format="%Y/%m/%d").dt.strftime("%d/%m/%Y")

        # Nombre de archivo .csv en la nueva carpeta 
        nuevo_nombre = ruta_csv / (archivo.stem + ".csv")

        # Guardar como CSV con separador ";" y decimal "," y sin agregar header
        df.to_csv(nuevo_nombre, index=False, sep=";", decimal=",",header=False)
    
    # Confirmacion de proceso terminado. 
    print("✅ Proceso completado: todos los archivos han sido convertidos correctamente.")

convertir_mpd_a_csv()# MODIFICAR PARAMETROS SEGUN CORRESPONDA
