import pandas as pd
from pathlib import Path

def filtro_ambig(ruta_entrada="INDICE_DE_MASA/csv/conversion",
           ruta_salida="INDICE_DE_MASA/csv/filtrado/ambig", 
           columna_objetivo=9,
           valor_permitido=1,
           columnas_a_eliminar=[2, 9, 12]):
    
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(exist_ok=True)

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

    print("✅ Proceso de filtrado y depuración completado correctamente.")
filtro_ambig()
