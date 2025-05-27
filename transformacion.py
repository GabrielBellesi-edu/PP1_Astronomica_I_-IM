#transformacion.py
import pandas as pd
from pathlib import Path

def transformar_archivos_csv(
        ruta_entrada="INDICE_DE_MASA/csv/filtrado/rge",
        ruta_salida="INDICE_DE_MASA/csv/transformado"):
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(exist_ok=True)

    archivos_csv = sorted(ruta_entrada.glob("*.csv"))

    for archivo in archivos_csv:
        print(f"Procesando: {archivo.name}")
        
        # Cargar el CSV sin encabezado, usando ; como separador y , como decimal
        df = pd.read_csv(archivo, sep=";", decimal=",", header=None)

        # Verificar que haya al menos 14 columnas
        if df.shape[1] < 14:
            print(f"⚠️ {archivo.name} tiene menos de 14 columnas. Se omite.")
            continue

        # Nueva columna: columna 10 - columna 13 (índices)
        nueva_columna = df.iloc[:, 10] - df.iloc[:, 13]
        
        # Agregar la nueva columna al final
        df[df.shape[1]] = nueva_columna

        # Guardar el nuevo archivo, sin encabezado
        salida = ruta_salida / archivo.name
        df.to_csv(salida, sep=";", decimal=",", index=False, header=False)
    
    print("✅ Transformación completa.")

transformar_archivos_csv()
