"""
Índice de Masa de Meteoritos
==========================================
Este módulo calcula el índice de masa de meteoritos usando el método estándar de regresión log-log.
Procesa datos desde archivos CSV con estructura específica.
Crea informes .txt con los resultados del analisis.

Ubicación: src/calculo/indice_masa..py
=========================================="""

#PARA EJECUTAR DESDE LA RAÍZ DEL PROYECTO:
#python src/calculo/indice_masa.py <temporalidad>
# Ejemplo: python src/calculo/indice_masa.py mensual


import numpy as np
import pandas as pd
from scipy import stats
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AnalisisMasaMeteoritos:
    """
    Clase principal para el análisis de índice de masa de meteoritos.
    """
    
    def __init__(self, raiz_proyecto=None):
        """
        Inicializa el analisis de masa de meteoritos.
        
        Parámetros:
        -----------
        raiz_proyecto : str, opcional
            Ruta raíz del proyecto. Si None, se calcula automáticamente.
        """
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
    
    def cargar_datos_csv(self, nombre_archivo=None):
        """
        Carga datos de amplitudes desde archivo CSV con formato específico.
        
        Parámetros:
        -----------
        nombre_archivo : str, opcional
            Nombre específico del archivo. Si None, usa '2024_consolidado.csv'
            
        Retorna:
        --------
        pandas.DataFrame : DataFrame con los datos cargados
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
            
            # Convertir fecha y hora para análisis temporal
            if 'Date' in df.columns and 'Time' in df.columns:
                try:
                    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], 
                                                  format='%d/%m/%Y %H:%M:%S.%f')
                    print("Columna datetime creada exitosamente")
                except Exception as e:
                    print(f"Advertencia: No se pudo crear columna datetime: {e}")
            
            return df
                
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return None
    
    def filtrar_datos_por_periodo(self, df, periodo='anual'):
        """
        Filtra y agrupa los datos por período temporal específico.
        
        Parámetros:
        -----------
        df : pandas.DataFrame
            DataFrame con columna datetime
        periodo : str
            Período: 'diario', 'semanal', 'mensual', 'bimestral', 'trimestral', 'cuatrimestral', 'semestral', 'anual'
        
        Retorna:
        --------
        dict : Diccionario con DataFrames filtrados por período
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
    
    def calcular_indice_masa(self, amplitudes, amplitud_minima=None, usar_binning=False, n_bins=50):
        """
        Calcula el índice de masa usando regresión log-log del método estándar.
        Aplica la fórmula: log(N) = -(s-1) * log(A) + C, donde s es el índice de masa.
        
        Parámetros:
        -----------
        amplitudes : numpy.array
            Array con valores de amplitud de meteoritos
        amplitud_minima : float, opcional
            Amplitud mínima para filtrar datos
        usar_binning : bool, opcional
            Si usar binning logarítmico para agrupar datos
        n_bins : int, opcional
            Número de bins si usar_binning=True
            
        Retorna:
        --------
        dict : Diccionario con resultados del análisis estadístico
        """
        
        # Filtrar datos si se especifica amplitud mínima
        if amplitud_minima is not None:
            amplitudes = amplitudes[amplitudes >= amplitud_minima]
            print(f"Después del filtrado: {len(amplitudes)} valores")
        
        # Remover valores <= 0
        amplitudes = amplitudes[amplitudes > 0]
        
        if len(amplitudes) < 10:
            print("Error: Muy pocos datos para análisis confiable")
            return None
        
        # Ordenar amplitudes de mayor a menor
        amplitudes_ordenadas = np.sort(amplitudes)[::-1]
        
        # Calcular conteo acumulado descendente
        N = np.arange(1, len(amplitudes_ordenadas) + 1)
        
        # Aplicar binning si se solicita
        if usar_binning:
            print(f"Aplicando binning logarítmico con {n_bins} bins...")
            
            log_min = np.log10(amplitudes_ordenadas.min())
            log_max = np.log10(amplitudes_ordenadas.max())
            bin_edges = np.logspace(log_min, log_max, n_bins + 1)
            
            bin_amplitudes = []
            bin_counts = []
            
            for i in range(len(bin_edges) - 1):
                mask = (amplitudes_ordenadas >= bin_edges[i]) & (amplitudes_ordenadas < bin_edges[i + 1])
                if np.sum(mask) > 0:
                    bin_amplitudes.append(np.mean(amplitudes_ordenadas[mask]))
                    bin_counts.append(np.sum(N <= np.sum(mask)))
            
            amplitudes_finales = np.array(bin_amplitudes)
            N_final = np.array(bin_counts)
        else:
            amplitudes_finales = amplitudes_ordenadas
            N_final = N
        
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
            'amplitud_promedio': amplitudes.mean(),
            'binning_usado': usar_binning
        }
        
        return resultados
    
    def _crear_directorio_periodo(self, periodo):
        """
        Crea el directorio específico para el período de análisis.
        
        Parámetros:
        -----------
        periodo : str
            Tipo de período ('diario', 'semanal', etc.)
            
        Retorna:
        --------
        str : Ruta del directorio creado
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
    
    def guardar_resultados_en_archivo(self, resultados, periodo, nombre_periodo_especifico):
        """
        Guarda los resultados del análisis en un archivo de texto con estructura específica.
        
        Parámetros:
        -----------
        resultados : dict
            Diccionario con resultados del análisis
        periodo : str
            Tipo de período ('diario', 'semanal', etc.)
        nombre_periodo_especifico : str
            Nombre específico del período (ej: '001_01/01')
            
        Retorna:
        --------
        str : Ruta del archivo guardado
        """
        if resultados is None:
            print("No hay resultados para guardar")
            return None
            
        # Crear directorio específico del período
        directorio_periodo = self._crear_directorio_periodo(periodo)
        
        # Limpiar el nombre del período para uso en nombres de archivo
        def limpiar_nombre_archivo(nombre):
            """Reemplaza caracteres problemáticos en nombres de archivo"""
            # Reemplazar caracteres problemáticos
            caracteres_problematicos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
            nombre_limpio = nombre
            for char in caracteres_problematicos:
                nombre_limpio = nombre_limpio.replace(char, '-')
            return nombre_limpio
        
        nombre_limpio = limpiar_nombre_archivo(nombre_periodo_especifico)
        
        # Generar nombre de archivo según el formato requerido
        if periodo == 'diario':
            nombre_archivo = f"diario_{nombre_limpio}.txt"
        elif periodo == 'semanal':
            nombre_archivo = f"semanal_{nombre_limpio}.txt"
        elif periodo == 'mensual':
            nombre_archivo = f"mensual_{nombre_limpio}.txt"
        elif periodo == 'bimestral':
            nombre_archivo = f"bimestral_{nombre_limpio}.txt"
        elif periodo == 'trimestral':
            nombre_archivo = f"trimestral_{nombre_limpio}.txt"
        elif periodo == 'cuatrimestral':
            nombre_archivo = f"cuatrimestral_{nombre_limpio}.txt"
        elif periodo == 'semestral':
            nombre_archivo = f"semestral_{nombre_limpio}.txt"
        elif periodo == 'anual':
            nombre_archivo = f"Anual_{nombre_limpio}.txt"
        else:
            nombre_archivo = f"{periodo}_{nombre_limpio}.txt"
            
        ruta_archivo = os.path.join(directorio_periodo, nombre_archivo)
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write("ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS\n")
                f.write("="*50 + "\n")
                f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Período analizado: {periodo} - {nombre_periodo_especifico}\n")
                f.write("\n")
                
                f.write("RESULTADOS PRINCIPALES:\n")
                f.write("-"*25 + "\n")
                f.write(f"Índice de masa (s):           {resultados['indice_masa']:.6f}\n")
                f.write(f"Pendiente de regresión:       {resultados['pendiente']:.4f}\n")
                f.write(f"Intercepto:                   {resultados['intercepto']:.4f}\n")
                f.write(f"Coeficiente de correlación:   {resultados['r_value']:.4f}\n")
                f.write(f"R² (bondad de ajuste):        {resultados['r_cuadrado']:.4f}\n")
                f.write(f"P-value:                      {resultados['p_value']:.2e}\n")
                f.write(f"Error estándar:               {resultados['error_estandar']:.4f}\n")
                f.write("\n")
                
                f.write("ESTADÍSTICAS DE DATOS:\n")
                f.write("-"*22 + "\n")
                f.write(f"Número de datos originales:   {resultados['n_datos_originales']}\n")
                f.write(f"Puntos usados en regresión:   {resultados['n_puntos_regresion']}\n")
                f.write(f"Amplitud mínima:              {resultados['rango_amplitud'][0]:.2f}\n")
                f.write(f"Amplitud máxima:              {resultados['rango_amplitud'][1]:.2f}\n")
                f.write(f"Amplitud promedio:            {resultados['amplitud_promedio']:.2f}\n")
                f.write(f"Binning aplicado:             {'Sí' if resultados['binning_usado'] else 'No'}\n")
                f.write("\n")
                
                f.write("INTERPRETACIÓN:\n")
                f.write("-"*15 + "\n")
                if resultados['r_cuadrado'] > 0.8:
                    f.write("✓ Excelente ajuste de la regresión\n")
                elif resultados['r_cuadrado'] > 0.6:
                    f.write("✓ Buen ajuste de la regresión\n")
                else:
                    f.write("⚠ Ajuste de regresión podría mejorarse\n")
                
                f.write(f"✓ Índice de masa calculado: s = {resultados['indice_masa']:.4f}\n")
            
            print(f"Resultados guardados en: {ruta_archivo}")
            return ruta_archivo
            
        except Exception as e:
            print(f"Error al guardar resultados: {e}")
            return None
    
    def analizar_periodo_especifico(self, periodo, amplitud_minima=None, usar_binning=False, 
                                  n_bins=50, nombre_archivo=None):
        """
        Función para analizar un período específico de datos.
        
        Parámetros:
        -----------
        periodo : str
            Período de análisis: 'diario', 'semanal', 'mensual', 'bimestral', 'trimestral', 'cuatrimestral', 'semestral', 'anual'
        amplitud_minima : float, opcional
            Amplitud mínima para filtrar datos
        usar_binning : bool
            Si usar binning logarítmico
        n_bins : int
            Número de bins si usar_binning=True
        nombre_archivo : str, opcional
            Nombre específico del archivo CSV
            
        Retorna:
        --------
        dict : Diccionario con todos los resultados por período
        """
        
        print("="*60)
        print("INICIANDO ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS")
        print("="*60)
        print(f"Período de análisis: {periodo}")
        if amplitud_minima:
            print(f"Amplitud mínima: {amplitud_minima}")
        if usar_binning:
            print(f"Binning logarítmico: {n_bins} bins")
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
                amplitudes_periodo, 
                amplitud_minima=amplitud_minima,
                usar_binning=usar_binning, 
                n_bins=n_bins
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

if __name__ == "__main__":
    import sys

    # Temporalidades válidas
    temporalidades = [
        'anual', 'semestral', 'cuatrimestral', 'trimestral',
        'bimestral', 'mensual', 'semanal', 'diario'
    ]

    if len(sys.argv) < 2 or sys.argv[1] not in temporalidades:
        print("Uso: python indice_masa.py <temporalidad>")
        print("Temporalidades válidas:", ", ".join(temporalidades))
        sys.exit(1)

    periodo = sys.argv[1]
    analisis = AnalisisMasaMeteoritos()
    analisis.analizar_periodo_especifico(
        periodo=periodo,
        amplitud_minima=10,
        usar_binning=False,
        n_bins=50,
        nombre_archivo=None
    )
