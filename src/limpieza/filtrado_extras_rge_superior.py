#Ejecutar desde jupyternotebook

import pandas as pd
from pathlib import Path

def procesar_y_consolidar_rge(
    ruta_entrada="data/interim/transformacion", 
    ruta_salida="data/processed/2024_consolidado_extra_rge_superior.csv",
    indice_rge=1,  # Ahora Rge es la columna 1
    rge_min=130, 
    rge_max=1000
):
    """
    Procesa archivos CSV aplicando filtro por RGE y los consolida en un único archivo.
    
    Args:
        ruta_entrada (str): Ruta donde se encuentran los archivos CSV originales
        ruta_salida (str): Ruta del archivo consolidado final
        indice_rge (int): Índice de la columna RGE (por defecto 1)
        rge_min (int): Valor mínimo de RGE para el filtro (por defecto 130)
        rge_max (int): Valor máximo de RGE para el filtro (por defecto 1000)
    """
    
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    
    # Crear directorio de salida si no existe
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    
    # Obtener todos los archivos CSV
    archivos_csv = sorted(ruta_entrada.glob("*.csv"))

    if not archivos_csv:
        print("⚠️ No se encontraron archivos CSV en la ruta especificada.")
        return
    
    # Lista de nombres de columnas
    columnas = [
        "Fecha y hora", "Rge", "Ht", "Vrad", "delVr",
        "Theta", "Phi0", "Delphase", "ant-pair",
        "amax", "Tau", "vmet", "snrdb"
    ]
    
    # Lista para acumular los DataFrames procesados
    dataframes = []
    
    print(f"Procesando {len(archivos_csv)} archivos...")
    
    # Procesar cada archivo
    for archivo in archivos_csv:
        print(f"Procesando: {archivo.name}")
        
        # Leer archivo
        df = pd.read_csv(archivo, sep=";", header=None, decimal=",")
        
        # Aplicar filtro por RGE
        df_filtrado = df[(df[indice_rge] >= rge_min) & (df[indice_rge] <= rge_max)]
        
        # Solo agregar si el DataFrame filtrado no está vacío
        if not df_filtrado.empty:
            # Asignar nombres de columnas
            df_filtrado.columns = columnas
            dataframes.append(df_filtrado)
        else:
            print(f"  ⚠️ Archivo {archivo.name} no tiene datos después del filtrado")
    
    # Verificar si hay datos para consolidar
    if not dataframes:
        print("⚠️ No hay datos para consolidar después del filtrado.")
        return
    
    # Consolidar todos los DataFrames
    print("Consolidando datos...")
    df_total = pd.concat(dataframes, ignore_index=True)
    
    # Guardar archivo consolidado
    df_total.to_csv(ruta_salida, index=False, sep=";", decimal=",")
    
    print(f"✅ Procesamiento completado.")
    print(f"📄 Archivo consolidado guardado en: {ruta_salida}")
    print(f"📊 Total de registros: {len(df_total):,}")
    
    return df_total