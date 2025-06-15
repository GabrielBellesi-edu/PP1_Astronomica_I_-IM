"""
Índice de Masa de Meteoritos
==========================================
Este módulo calcula el índice de masa de meteoritos usando el método estándar de regresión log-log. 
Procesa datos desde archivos CSV con estructura específica.
Agrega resultados a un archivo csv con columnas de índices de masa por temporalidad.
"""

#PARA EJECUTAR DESDE LA RAÍZ DEL PROYECTO:
# python src/calculo/tabla_indice_masa.py agregar_indices 2024_consolidado.csv
# Se ejuta analisis.agregar_indices_masa_a_csv(nombre_archivo=sys.argv[2])

# python src/calculo/tabla_indice_masa.py semanal
# Se ejecuta analisis.analizar_periodo_especifico(periodo=periodo, nombre_archivo=None)

import numpy as np
import pandas as pd
from scipy import stats
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

#Clase principal para el análisis de índice de masa de meteoritos.
class AnalisisMasaMeteoritos:
    

    #Inicializa el analisis de masa de meteoritos.
    def __init__(self, raiz_proyecto=None):

        if raiz_proyecto is None:
            # Obtener la ruta del proyecto desde la ubicación del archivo
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            # Subir dos niveles desde /src/calculo_indice_masa
            self.raiz_proyecto = os.path.dirname(os.path.dirname(directorio_actual))
        else:
            self.raiz_proyecto = raiz_proyecto
            
        self.directorio_datos = os.path.join(self.raiz_proyecto, 'data', 'processed')
        self.directorio_reportes = os.path.join(self.raiz_proyecto, 'reports')
        
        # Crear directorios base si no existen
        os.makedirs(self.directorio_reportes, exist_ok=True)
        
        print(f"Proyecto inicializado:")
        print(f"  - Raíz del proyecto: {self.raiz_proyecto}")
        print(f"  - Datos: {self.directorio_datos}")
        print(f"  - Reportes: {self.directorio_reportes}")
    

    #Carga datos de amplitudes desde archivo CSV con formato específico.
    def cargar_datos_csv(self, nombre_archivo=None):
        """
        Parámetros: nombre_archivo : str, opcional / Nombre específico del archivo. Si None, usa '2024_consolidado.csv'
        Retorna: pandas.DataFrame : DataFrame con los datos cargados
        """

        if nombre_archivo is None:
            nombre_archivo = '2024_consolidado.csv'
            
        ruta_archivo = os.path.join(self.directorio_datos, nombre_archivo)
        print(f"Cargando datos desde: {ruta_archivo}")
        
        try:
            # Cargar CSV con separador ; y decimal ,
            df = pd.read_csv(ruta_archivo, sep=';', decimal=',')
            print(f"Datos CSV cargados: {len(df)} filas, {len(df.columns)} columnas")
            
            # Verificar columnas requeridas
            if 'amax' not in df.columns:
                raise ValueError("Columna 'amax' no encontrada en el archivo CSV")
            
            # Convertir 'Fecha y hora' a datetime para análisis temporal
            if 'Fecha y hora' in df.columns:
                try:
                    df['datetime'] = pd.to_datetime(df['Fecha y hora'], errors='coerce')
                    print("Columna 'datetime' creada exitosamente a partir de 'Fecha y hora'")
                except Exception as e:
                    print(f"Advertencia: No se pudo crear columna datetime: {e}")
            
            return df
                
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return None
    

    #Filtra y agrupa datos por período temporal específico.
    def filtrar_datos_por_periodo(self, df, periodo='anual'):
        """
        Parámetros: periodo : str / Período: 'diario', 'semanal', 'mensual', 'bimestral', 'trimestral', 'cuatrimestral', 'semestral', 'anual'
        Retorna: Diccionario con DataFrames filtrados por período
        """

        if df is None or 'datetime' not in df.columns:
            print("No hay datos temporales disponibles para filtrado por período")
            return {'anual': df}
        
        datos_periodos = {}
        
        if periodo == 'anual':
            datos_periodos['2024'] = df
            
        elif periodo == 'diario':
            # Agrupar por día
            df['date'] = df['datetime'].dt.date
            for fecha in sorted(df['date'].unique()):
                fecha_str = fecha.strftime('%d/%m')
                day_number = fecha.timetuple().tm_yday  # día del año
                key = f"{day_number:03d}_{fecha_str}"
                datos_periodos[key] = df[df['date'] == fecha]
                
        elif periodo == 'semanal':
            # Agrupar por semana del año
            df['week'] = df['datetime'].dt.isocalendar().week
            df['date'] = df['datetime'].dt.date
            
            for semana in sorted(df['week'].unique()):
                # Obtener fechas de inicio y fin de la semana
                datos_semana = df[df['week'] == semana]
                fecha_inicio = datos_semana['date'].min()
                fecha_fin = datos_semana['date'].max()
                
                inicio_str = fecha_inicio.strftime('%d/%m')
                fin_str = fecha_fin.strftime('%d/%m')
                key = f"{semana:02d}_{inicio_str}-{fin_str}"
                datos_periodos[key] = datos_semana
                
        elif periodo == 'mensual':
            # Agrupar por mes
            df['month'] = df['datetime'].dt.month
            meses_nombres = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                           'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            
            for mes in sorted(df['month'].unique()):
                mes_nombre = meses_nombres[mes-1]
                key = f"{mes:02d}_{mes_nombre}"
                datos_periodos[key] = df[df['month'] == mes]
                
        elif periodo == 'bimestral':
            # Agrupar por bimestre (cada 2 meses)
            df['bimester'] = ((df['datetime'].dt.month - 1) // 2) + 1
            bimestres = ['ene-feb', 'mar-abr', 'may-jun', 'jul-ago', 'sep-oct', 'nov-dic']

            for b in sorted(df['bimester'].unique()):
                if b <= len(bimestres):
                    bimestre_nombre = bimestres[b-1]
                    key = f"{b}_{bimestre_nombre}"
                    datos_periodos[key] = df[df['bimester'] == b]             

        elif periodo == 'trimestral':
            # Agrupar por trimestre
            df['quarter'] = df['datetime'].dt.quarter
            trimestres = ['ene-mar', 'abr-jun', 'jul-sep', 'oct-dic']
            
            for q in sorted(df['quarter'].unique()):
                trimestre_nombre = trimestres[q-1]
                key = f"{q}_{trimestre_nombre}"
                datos_periodos[key] = df[df['quarter'] == q]
                
        elif periodo == 'cuatrimestral':
            # Agrupar por cuatrimestre
            df['quadrimester'] = ((df['datetime'].dt.month - 1) // 4) + 1
            cuatrimestres = ['ene-abr', 'may-ago', 'sep-dic']
            
            for cuad in sorted(df['quadrimester'].unique()):
                if cuad <= len(cuatrimestres):
                    cuatrimestre_nombre = cuatrimestres[cuad-1]
                    key = f"{cuad}_{cuatrimestre_nombre}"
                    datos_periodos[key] = df[df['quadrimester'] == cuad]
                
        elif periodo == 'semestral':
            # Agrupar por semestre
            df['semester'] = ((df['datetime'].dt.month - 1) // 6) + 1
            semestres = ['ene-jun', 'jul-dic']
            
            for sem in sorted(df['semester'].unique()):
                if sem <= len(semestres):
                    semestre_nombre = semestres[sem-1]
                    key = f"{sem}_{semestre_nombre}"
                    datos_periodos[key] = df[df['semester'] == sem]
        
        print(f"Datos agrupados por {periodo}: {len(datos_periodos)} períodos")
        return datos_periodos
    

    #Calcula el índice de masa usando regresión log-log del método estándar.
    #Aplica la fórmula: log(N) = -(s-1) * log(A) + C, donde s es el índice de masa.
    def calcular_indice_masa(self, amplitudes):
        """
        Parámetros:
        -----------
        amplitudes : numpy.array
            Array con valores de amplitud de meteoritos
        amplitud_minima : float, opcional
            Amplitud mínima para filtrar datos
            
        Retorna:
        --------
        dict : Diccionario con resultados del análisis estadístico
        """
        
        # Remover valores <= 0
        amplitudes = amplitudes[amplitudes > 0]
        
        if len(amplitudes) < 10:
            print("Error: Muy pocos datos para análisis confiable")
            return None
        
        # Ordenar amplitudes de mayor a menor
        amplitudes_finales = np.sort(amplitudes)[::-1]
        
        # Calcular conteo acumulado descendente
        N_final = np.arange(1, len(amplitudes_finales) + 1)


        # Preparar datos para regresión lineal
        log_A = np.log10(amplitudes_finales)
        log_N = np.log10(N_final)
        
        # Realizar regresión lineal: log(N) = -(s-1) * log(A) + C
        pendiente, intercepto, r_value, p_value, error_std = stats.linregress(log_A, log_N)
        
        # Calcular índice de masa: s = 1 - pendiente
        indice_masa = 1 - pendiente
        
        # Calcular estadísticas adicionales
        r_cuadrado = r_value ** 2
        n_puntos = len(log_A)
        
        # Preparar resultados
        resultados = {
            'indice_masa': indice_masa,
            'pendiente': pendiente,
            'intercepto': intercepto,
            'r_cuadrado': r_cuadrado,
            'r_value': r_value,
            'p_value': p_value,
            'error_estandar': error_std,
            'n_datos_originales': len(amplitudes),
            'n_puntos_regresion': n_puntos,
            'rango_amplitud': (amplitudes.min(), amplitudes.max()),
            'amplitud_promedio': amplitudes.mean()
        }
        
        return resultados
    

    #Crea un directorio específico para el período de análisis.
    def _crear_directorio_periodo(self, periodo):
        """
        Parámetros: periodo : str / Tipo de período ('diario', 'semanal', etc.)
        Retorna: str : Ruta del directorio creado
        """
        mapeo_directorios = {
            'diario': 'CalculoDiario',
            'semanal': 'CalculoSemanal', 
            'mensual': 'CalculoMensual',
            'bimestral': 'CalculoBimestral',
            'trimestral': 'CalculoTrimestral',
            'cuatrimestral': 'CalculoCuatrimestral',
            'semestral': 'CalculoSemestral',
            'anual': 'CalculoAnual'
        }
        
        nombre_directorio = mapeo_directorios.get(periodo, f'Calculo{periodo.capitalize()}')
        directorio_periodo = os.path.join(self.directorio_reportes, nombre_directorio)
        os.makedirs(directorio_periodo, exist_ok=True)
        
        return directorio_periodo
    
    
    #Analiza un período específico de datos y guarda los resultados en archivos.
    def analizar_periodo_especifico(self, periodo, nombre_archivo=None):
        """
        Parámetros:
        periodo : str / Período de análisis: 'diario', 'semanal', 'mensual', 'bimestral', 'trimestral', 'cuatrimestral', 'semestral', 'anual'
        nombre_archivo : str, opcional / Nombre específico del archivo CSV
            
        Retorna: dict : Diccionario con todos los resultados por período
        """
        
        print("="*60)
        print("INICIANDO ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS")
        print("="*60)
        print(f"Período de análisis: {periodo}")
        print()
        
        # Cargar datos
        df = self.cargar_datos_csv(nombre_archivo)
        
        if df is None:
            print("Error: No se pudieron cargar los datos")
            return None
        
        # Filtrar por período
        datos_periodos = self.filtrar_datos_por_periodo(df, periodo)
        
        todos_resultados = {}
        
        # Analizar cada período
        for nombre_periodo, datos_periodo in datos_periodos.items():
            print(f"\n--- Analizando período: {nombre_periodo} ---")
            
            # Extraer amplitudes para este período
            amplitudes_periodo = datos_periodo['amax'].values
            
            # Calcular índice de masa
            resultados = self.calcular_indice_masa(
                amplitudes_periodo
            )
            
            if resultados is not None:
                # Guardar resultados
                self.guardar_resultados_en_archivo(resultados, periodo, nombre_periodo)
                todos_resultados[nombre_periodo] = resultados
            else:
                print(f"No se pudo calcular el índice para el período {nombre_periodo}")
        
        print(f"\n{'='*60}")
        print(f"ANÁLISIS COMPLETADO - {len(todos_resultados)} períodos procesados")
        print(f"{'='*60}")
        
        return todos_resultados

    def agregar_indices_masa_a_csv(self, nombre_archivo=None):
        """
        Calcula el índice de masa para cada temporalidad y agrega una columna por temporalidad al CSV original.
        Guarda el nuevo archivo en reports/ con sufijo _IM_temporalidades.csv
        """
        # Definir temporalidades y sus columnas de agrupamiento
        temporalidades = [
            ('anual', None),
            ('semestral', 'semestre'),
            ('cuatrimestral', 'cuatrimestre'),
            ('trimestral', 'trimestre'),
            ('bimestral', 'bimestre'),
            ('mensual', 'mes'),
            ('semanal', 'semana'),
            ('diario', 'dia')
        ]
        df = self.cargar_datos_csv(nombre_archivo)
        if df is None:
            print("No se pudo cargar el archivo original.")
            return

        # Solo conservar la columna 'Fecha y hora'
        df_resultado = df[['Fecha y hora']].copy()

        # Para cada temporalidad, calcular el índice de masa y asignar a cada fila
        for periodo, col_agrup in temporalidades:
            print(f"\nProcesando temporalidad: {periodo}")
            datos_periodos = self.filtrar_datos_por_periodo(df, periodo)
            col_im = f'IM_{periodo}'
            df_resultado[col_im] = np.nan
            if col_agrup:
                df_resultado[col_agrup] = np.nan

            for nombre_periodo, datos_periodo in datos_periodos.items():
                amplitudes = datos_periodo['amax'].values
                resultados = self.calcular_indice_masa(amplitudes)
                if resultados is not None:
                    idx = datos_periodo.index
                    df_resultado.loc[idx, col_im] = round(resultados['indice_masa'], 6)
                    if col_agrup:
                        # Extraer solo el número del período (antes del guion bajo)
                        numero_periodo = str(nombre_periodo).split('_')[0]
                        # Asignar el número a la columna de agrupamiento
                        df_resultado.loc[idx, col_agrup] = numero_periodo

        # Ordenar columnas: Fecha y hora, luego cada agrupador seguido de su IM
        columnas_finales = ['Fecha y hora']
        for periodo, col_agrup in temporalidades:
            if col_agrup:
                columnas_finales.append(col_agrup)
            columnas_finales.append(f'IM_{periodo}')
        columnas_finales = [col for col in columnas_finales if col in df_resultado.columns]
        df_final = df_resultado[columnas_finales]

        # Agregar columna ID incremental (1, 2, 3, ...)
        df_final.insert(0, 'ID', range(1, len(df_final) + 1))

        # Guardar el nuevo archivo
        nombre_base = os.path.splitext(nombre_archivo or '2024_consolidado.csv')[0]
        nombre_nuevo = f"{nombre_base}_IM_temporalidades.csv"
        ruta_salida = os.path.join(self.directorio_reportes, nombre_nuevo)
        df_final.to_csv(ruta_salida, sep=';', decimal=',', index=False, encoding='utf-8', float_format='%.6f')
        print(f"\nArchivo con índices de masa por temporalidad guardado en: {ruta_salida}")



# Agrega esto al final para ejecución directa:
if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "agregar_indices":
        analisis = AnalisisMasaMeteoritos()
        if len(sys.argv) >= 3:
            analisis.agregar_indices_masa_a_csv(nombre_archivo=sys.argv[2])
        else:
            analisis.agregar_indices_masa_a_csv()
    else:
        temporalidades = ['anual', 'semestral', 'cuatrimestral', 'trimestral','bimestral', 'mensual', 'semanal', 'diario']
        if len(sys.argv) < 2 or sys.argv[1] not in temporalidades:
            print("Uso: python tabla_indice_masa <temporalidad>")
            print("Temporalidades válidas:", ", ".join(temporalidades))
            print("O: python tabla_indice_masa agregar_indices [nombre_archivo.csv]")
            sys.exit(1)
        periodo = sys.argv[1]
        analisis = AnalisisMasaMeteoritos()
        analisis.analizar_periodo_especifico(
            periodo=periodo,
            nombre_archivo=None
        )



""" def agregar_indices_masa_a_csv(self, nombre_archivo=None):
        """"""
        Calcula el índice de masa para cada temporalidad y agrega una columna por temporalidad al CSV original.
        Guarda el nuevo archivo en reports/ con sufijo _IM_temporalidades.csv
        """"""
        temporalidades = ['anual', 'semestral', 'cuatrimestral', 'trimestral', 'bimestral', 'mensual', 'semanal', 'diario']
        df = self.cargar_datos_csv(nombre_archivo)
        if df is None:
            print("No se pudo cargar el archivo original.")
            return

        # Asegurarse de tener columna datetime
        if 'datetime' not in df.columns:
            print("No hay columna 'datetime' en el archivo.")
            return

        # Para cada temporalidad, calcular el índice de masa y asignar a cada fila
        for periodo in temporalidades:
            print(f"\nProcesando temporalidad: {periodo}")
            # Agrupar por período
            datos_periodos = self.filtrar_datos_por_periodo(df, periodo)
            # Crear una columna vacía para esta temporalidad
            col_name = f'IM_{periodo}'
            df[col_name] = np.nan

            for nombre_periodo, datos_periodo in datos_periodos.items():
                amplitudes = datos_periodo['amax'].values
                resultados = self.calcular_indice_masa(amplitudes)
                if resultados is not None:
                    # Asignar el índice de masa a todas las filas de este período
                    idx = datos_periodo.index
                    df.loc[idx, col_name] = round(resultados['indice_masa'], 6)



        # Renombrar columnas temporales al español
        renombres = {
            'semester': 'semestre',
            'quadrimester': 'cuatrimestre',
            'quarter': 'trimestre',
            'bimester': 'bimestre',
            'month': 'mes',
            'week': 'semana'
        }
        df.rename(columns=renombres, inplace=True)

        # Eliminar columna 'date.1' si existe antes de guardar
        if 'date' in df.columns:
            df.drop(columns=['date'], inplace=True)

        # Guardar el nuevo archivo
        nombre_base = os.path.splitext(nombre_archivo or '2024_consolidado.csv')[0]
        nombre_nuevo = f"{nombre_base}_IM_temporalidades.csv"
        ruta_salida = os.path.join(self.directorio_reportes, nombre_nuevo)
        df.to_csv(ruta_salida, sep=';', decimal=',', index=False, encoding='utf-8', float_format='%.6f')
        print(f"\nArchivo con índices de masa por temporalidad guardado en: {ruta_salida}")
        """