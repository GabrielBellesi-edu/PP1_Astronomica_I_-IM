import pandas as pd
from pathlib import Path

# Ruta a los .mpd
ruta_mpd = Path("Test/mpd2024") # MODIFICAR SEGUN CORRESPONDA
# Ruta donde guardar los .csv (puede ser la misma o distinta)
ruta_csv = Path("Test/mpd2024_csv") # MODIFICAR SEGUN CORRESPONDA
ruta_csv.mkdir(exist_ok=True)  # Crear carpeta si no existe

# Buscar todos los archivos .mpd
archivos_mpd = sorted(ruta_mpd.glob("mp*.riogrande.mpd"))

for archivo in archivos_mpd:
    print(f"Convirtiendo: {archivo.name}")
    
    # Leer tabla desde la línea 30
    df = pd.read_fwf(archivo, skiprows=29)

    # Nombre de archivo .csv en la nueva carpeta
    nuevo_nombre = ruta_csv / (archivo.stem + ".csv")

    # Guardar como CSV
    df.to_csv(nuevo_nombre, index=False)
    # Confirmacion de proceso terminado. 
print("✅ Proceso completado: todos los archivos han sido convertidos correctamente.")
