import pandas as pd
from pathlib import Path

def filtro_rge(ruta_entrada="INDICE_DE_MASA/csv/filtrado/ambig",
                   ruta_salida="INDICE_DE_MASA/csv/filtrado/rge",
                   indice_rge=2,
                   rge_min=100,
                   rge_max=130):
    
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(exist_ok=True)

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

    print("✅ Filtrado por Rge completado correctamente.")

filtro_rge()
