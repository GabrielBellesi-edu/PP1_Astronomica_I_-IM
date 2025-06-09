#!/usr/bin/env python3
"""
Analizador de Índice de Masa de Meteoritos
==========================================

Este módulo calcula el índice de masa de meteoritos usando el método estándar
de regresión log-log. Puede procesar datos desde archivos CSV o TXT y realizar
análisis por diferentes períodos temporales.

Ubicación: calculo/calcular_indice_masa.py
Autor: Adaptado del notebook original
Fecha: 2025
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
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
        Inicializa el analizador de masa de meteoritos.
        
        Parámetros:
        -----------
        raiz_proyecto : str, opcional
            Ruta raíz del proyecto. Si None, se calcula automáticamente.
        """
        if raiz_proyecto is None:
            # Obtener la ruta del proyecto desde la ubicación del archivo
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            self.raiz_proyecto = os.path.dirname(directorio_actual)  # Subir un nivel desde /calculo
        else:
            self.raiz_proyecto = raiz_proyecto
            
        self.directorio_datos = os.path.join(self.raiz_proyecto, 'data', 'processed')
        self.directorio_reportes = os.path.join(self.raiz_proyecto, 'reports')
        self.directorio_figuras = os.path.join(self.raiz_proyecto, 'reports', 'figures')
        
        # Crear directorios si no existen
        os.makedirs(self.directorio_reportes, exist_ok=True)
        os.makedirs(self.directorio_figuras, exist_ok=True)
        
        print(f"Proyecto inicializado:")
        print(f"  - Raíz del proyecto: {self.raiz_proyecto}")
        print(f"  - Datos: {self.directorio_datos}")
        print(f"  - Reportes: {self.directorio_reportes}")
        print(f"  - Figuras: {self.directorio_figuras}")
    
    def cargar_datos(self, tipo_archivo='csv', nombre_archivo=None):
        """
        Carga datos de amplitudes desde archivo CSV o TXT.
        
        Parámetros:
        -----------
        tipo_archivo : str
            'csv' para archivo CSV con headers, 'txt' para archivo TXT simple
        nombre_archivo : str, opcional
            Nombre específico del archivo. Si None, usa nombres por defecto.
            
        Retorna:
        --------
        tuple : (amplitudes, dataframe_original)
            - amplitudes: numpy.array con valores de amplitud
            - dataframe_original: pandas.DataFrame (CSV) o None (TXT)
        """
        if nombre_archivo is None:
            if tipo_archivo == 'csv':
                ruta_archivo = os.path.join(self.directorio_datos, '2024_consolidado.csv')
            else:
                ruta_archivo = os.path.join(self.directorio_datos, '2024_consolidado_amax.txt')
        else:
            ruta_archivo = os.path.join(self.directorio_datos, nombre_archivo)
        
        print(f"Cargando datos desde: {ruta_archivo}")
        
        try:
            if tipo_archivo == 'csv':
                # Cargar CSV con pandas
                df = pd.read_csv(ruta_archivo, sep=';', decimal=',')
                print(f"Datos CSV cargados: {len(df)} filas, {len(df.columns)} columnas")
                print(f"Columnas disponibles: {list(df.columns)}")
                
                # Extraer columna amax
                if 'amax' in df.columns:
                    amplitudes = df['amax'].values
                else:
                    raise ValueError("Columna 'amax' no encontrada en el archivo CSV")
                
                # Convertir fecha para análisis temporal si están disponibles
                if 'Date' in df.columns and 'Time' in df.columns:
                    try:
                        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], 
                                                      format='%d/%m/%Y %H:%M:%S.%f')
                        print("Columna datetime creada exitosamente")
                    except Exception as e:
                        print(f"Advertencia: No se pudo crear columna datetime: {e}")
                
                return amplitudes, df
                
            else:  # txt
                # Leer archivo TXT simple (solo valores)
                data = np.loadtxt(ruta_archivo, dtype=str)
                data = np.char.replace(data, ",", ".").astype(float)
                amplitudes = data.flatten()
                print(f"Datos TXT cargados: {len(amplitudes)} valores")
                
                return amplitudes, None
                
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return None, None
    
    def filtrar_datos_por_periodo(self, df, periodo='anual'):
        """
        Filtra y agrupa los datos por período temporal específico.
        
        Parámetros:
        -----------
        df : pandas.DataFrame
            DataFrame con columna datetime
        periodo : str
            Período: 'diario', 'semanal', 'mensual', 'bimestral', 
                    'trimestral', 'cuatrimestral', 'semestral', 'anual'
        
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
                fecha_str = str(fecha)
                datos_periodos[fecha_str] = df[df['date'] == fecha]
                
        elif periodo == 'semanal':
            # Agrupar por semana del año
            df['week'] = df['datetime'].dt.isocalendar().week
            for semana in sorted(df['week'].unique()):
                semana_str = f"Semana_{semana:02d}"
                datos_periodos[semana_str] = df[df['week'] == semana]
                
        elif periodo == 'mensual':
            # Agrupar por mes
            df['month'] = df['datetime'].dt.month
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            for mes in sorted(df['month'].unique()):
                mes_str = meses[mes-1]
                datos_periodos[mes_str] = df[df['month'] == mes]
                
        elif periodo == 'bimestral':
            # Agrupar por bimestre
            df['bimester'] = ((df['datetime'].dt.month - 1) // 2) + 1
            for bim in sorted(df['bimester'].unique()):
                bim_str = f"Bimestre_{bim}"
                datos_periodos[bim_str] = df[df['bimester'] == bim]
                
        elif periodo == 'trimestral':
            # Agrupar por trimestre
            df['quarter'] = df['datetime'].dt.quarter
            for q in sorted(df['quarter'].unique()):
                q_str = f"Trimestre_{q}"
                datos_periodos[q_str] = df[df['quarter'] == q]
                
        elif periodo == 'cuatrimestral':
            # Agrupar por cuatrimestre
            df['quadrimester'] = ((df['datetime'].dt.month - 1) // 4) + 1
            for cuad in sorted(df['quadrimester'].unique()):
                cuad_str = f"Cuatrimestre_{cuad}"
                datos_periodos[cuad_str] = df[df['quadrimester'] == cuad]
                
        elif periodo == 'semestral':
            # Agrupar por semestre
            df['semester'] = ((df['datetime'].dt.month - 1) // 6) + 1
            for sem in sorted(df['semester'].unique()):
                sem_str = f"Semestre_{sem}"
                datos_periodos[sem_str] = df[df['semester'] == sem]
        
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
            'binning_usado': usar_binning,
            # Datos para gráficos
            'amplitudes_originales': amplitudes,
            'amplitudes_finales': amplitudes_finales,
            'N_final': N_final,
            'log_A': log_A,
            'log_N': log_N
        }
        
        return resultados
    
    def imprimir_resultados(self, resultados, nombre_periodo=""):
        """
        Imprime los resultados del análisis de índice de masa de forma clara y organizada.
        
        Parámetros:
        -----------
        resultados : dict
            Diccionario con resultados del análisis
        nombre_periodo : str
            Nombre del período analizado
        """
        if resultados is None:
            print("No hay resultados para mostrar")
            return
        
        encabezado = f"RESULTADOS DEL ANÁLISIS DE ÍNDICE DE MASA"
        if nombre_periodo:
            encabezado += f" - {nombre_periodo}"
            
        print("\n" + "="*60)
        print(encabezado)
        print("="*60)
        print(f"Índice de masa (s):           {resultados['indice_masa']:.4f}")
        print(f"Pendiente de regresión:       {resultados['pendiente']:.4f}")
        print(f"Intercepto:                   {resultados['intercepto']:.4f}")
        print(f"Coeficiente de correlación:   {resultados['r_value']:.4f}")
        print(f"R² (bondad de ajuste):        {resultados['r_cuadrado']:.4f}")
        print(f"P-value:                      {resultados['p_value']:.2e}")
        print(f"Error estándar:               {resultados['error_estandar']:.4f}")
        print(f"Número de datos originales:   {resultados['n_datos_originales']}")
        print(f"Puntos usados en regresión:   {resultados['n_puntos_regresion']}")
        print(f"Amplitud mínima:              {resultados['rango_amplitud'][0]:.2f}")
        print(f"Amplitud máxima:              {resultados['rango_amplitud'][1]:.2f}")
        print(f"Amplitud promedio:            {resultados['amplitud_promedio']:.2f}")
        print(f"Binning aplicado:             {'Sí' if resultados['binning_usado'] else 'No'}")
        print("="*60)
        
        # Interpretación básica
        if resultados['r_cuadrado'] > 0.8:
            print("✓ Excelente ajuste de la regresión")
        elif resultados['r_cuadrado'] > 0.6:
            print("✓ Buen ajuste de la regresión")
        else:
            print("⚠ Ajuste de regresión podría mejorarse")
        
        print(f"✓ Índice de masa calculado: s = {resultados['indice_masa']:.4f}")
    
    def guardar_resultados_en_archivo(self, resultados, nombre_periodo="", sufijo_archivo=""):
        """
        Guarda los resultados del análisis en un archivo de texto para referencia futura.
        
        Parámetros:
        -----------
        resultados : dict
            Diccionario con resultados del análisis
        nombre_periodo : str
            Nombre del período analizado
        sufijo_archivo : str
            Sufijo adicional para el nombre del archivo
        """
        if resultados is None:
            print("No hay resultados para guardar")
            return None
            
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if nombre_periodo:
            nombre_archivo = f"indice_masa_{nombre_periodo}_{timestamp}{sufijo_archivo}.txt"
        else:
            nombre_archivo = f"indice_masa_{timestamp}{sufijo_archivo}.txt"
            
        ruta_archivo = os.path.join(self.directorio_reportes, nombre_archivo)
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write("ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS\n")
                f.write("="*50 + "\n")
                f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if nombre_periodo:
                    f.write(f"Período analizado: {nombre_periodo}\n")
                f.write("\n")
                
                f.write("RESULTADOS PRINCIPALES:\n")
                f.write("-"*25 + "\n")
                f.write(f"Índice de masa (s):           {resultados['indice_masa']:.4f}\n")
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
    
    def crear_grafico_analisis(self, resultados, nombre_periodo="", guardar_grafico=True):
        """
        Crea gráfico con regresión log-log y distribución de amplitudes únicamente.
        
        Parámetros:
        -----------
        resultados : dict
            Diccionario con resultados del análisis
        nombre_periodo : str
            Nombre del período analizado
        guardar_grafico : bool
            Si guardar el gráfico en archivo
        """
        if resultados is None:
            print("No hay resultados para graficar")
            return
        
        # Crear figura con 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. Gráfico de regresión log-log
        log_A = resultados['log_A']
        log_N = resultados['log_N']
        
        # Datos observados
        ax1.scatter(log_A, log_N, alpha=0.7, s=30, color='blue', label='Datos observados')
        
        # Línea de ajuste
        A_fit = np.linspace(log_A.min(), log_A.max(), 100)
        N_fit = resultados['pendiente'] * A_fit + resultados['intercepto']
        ax1.plot(A_fit, N_fit, 'r-', linewidth=2, 
                label=f'Ajuste: s = {resultados["indice_masa"]:.3f}')
        
        ax1.set_xlabel('log₁₀(Amplitud)')
        ax1.set_ylabel('log₁₀(N acumulado)')
        ax1.set_title(f'Regresión Log-Log (R² = {resultados["r_cuadrado"]:.4f})')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Distribución de amplitudes
        ax2.hist(resultados['amplitudes_originales'], bins=50, alpha=0.7, 
                color='green', edgecolor='black')
        ax2.set_xlabel('Amplitud')
        ax2.set_ylabel('Frecuencia')
        ax2.set_title('Distribución de Amplitudes')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
        
        # Título general
        titulo = 'Análisis de Índice de Masa'
        if nombre_periodo:
            titulo += f' - {nombre_periodo}'
        fig.suptitle(titulo, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        # Guardar figura si se solicita
        if guardar_grafico:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if nombre_periodo:
                nombre_archivo = f"indice_masa_{nombre_periodo}_{timestamp}.png"
            else:
                nombre_archivo = f"indice_masa_{timestamp}.png"
            
            ruta_archivo = os.path.join(self.directorio_figuras, nombre_archivo)
            fig.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado como: {ruta_archivo}")
            
        return fig
    
    def analizar_indice_masa(self, tipo_archivo='csv', periodo='anual', amplitud_minima=None, 
                          usar_binning=False, n_bins=50, guardar_resultados=True, 
                          guardar_graficos=True, nombre_archivo=None):
        """
        Función principal para analizar el índice de masa de meteoritos.
        Por defecto hace análisis anual. Solo hace otros períodos si se especifica explícitamente.
        
        Parámetros:
        -----------
        tipo_archivo : str
            'csv' o 'txt' según el tipo de archivo
        periodo : str
            Período de análisis: 'anual' (por defecto), 'mensual', 'semanal', etc.
            Si se especifica otro período, NO se hace análisis anual
        amplitud_minima : float, opcional
            Amplitud mínima para filtrar datos
        usar_binning : bool
            Si usar binning logarítmico
        n_bins : int
            Número de bins si usar_binning=True
        guardar_resultados : bool
            Si guardar resultados en archivo txt
        guardar_graficos : bool
            Si guardar gráficos
        nombre_archivo : str, opcional
            Nombre específico del archivo
            
        Retorna:
        --------
        dict : Diccionario con todos los resultados por período
        """
        
        print("="*60)
        print("INICIANDO ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS")
        print("="*60)
        print(f"Tipo de archivo: {tipo_archivo.upper()}")
        print(f"Período de análisis: {periodo}")
        if amplitud_minima:
            print(f"Amplitud mínima: {amplitud_minima}")
        if usar_binning:
            print(f"Binning logarítmico: {n_bins} bins")
        print()
        
        # Cargar datos
        amplitudes, df = self.cargar_datos(tipo_archivo, nombre_archivo)
        
        if amplitudes is None:
            print("Error: No se pudieron cargar los datos")
            return None
        
        # Filtrar por período - SOLO si hay datos temporales y se especifica período diferente a anual
        if tipo_archivo == 'csv' and df is not None and 'datetime' in df.columns:
            datos_periodos = self.filtrar_datos_por_periodo(df, periodo)
        else:
            # Para archivos TXT o cuando no hay datos temporales, usar todos los datos
            datos_periodos = {'todos_los_datos': df if df is not None else amplitudes}
        
        todos_resultados = {}
        
        # Analizar cada período
        for nombre_periodo, datos_periodo in datos_periodos.items():
            print(f"\n--- Analizando período: {nombre_periodo} ---")
            
            # Extraer amplitudes para este período
            if isinstance(datos_periodo, pd.DataFrame):
                amplitudes_periodo = datos_periodo['amax'].values
            else:
                amplitudes_periodo = amplitudes  # Para datos TXT
            
            # Calcular índice de masa
            resultados = self.calcular_indice_masa(
                amplitudes_periodo, 
                amplitud_minima=amplitud_minima,
                usar_binning=usar_binning, 
                n_bins=n_bins
            )
            
            if resultados is not None:
                # Mostrar resultados
                self.imprimir_resultados(resultados, nombre_periodo)
                
                # Guardar resultados si se solicita
                if guardar_resultados:
                    self.guardar_resultados_en_archivo(resultados, nombre_periodo)
                
                # Crear gráfico si se solicita
                if guardar_graficos:
                    self.crear_grafico_analisis(resultados, nombre_periodo, guardar_grafico=True)
                
                todos_resultados[nombre_periodo] = resultados
            else:
                print(f"No se pudo calcular el índice para el período {nombre_periodo}")
        
        print(f"\n{'='*60}")
        print(f"ANÁLISIS COMPLETADO - {len(todos_resultados)} períodos procesados")
        print(f"{'='*60}")
        
        return todos_resultados


def main():
    """
    Función principal para ejecutar el análisis desde línea de comandos.
    Por defecto ejecuta análisis anual.
    """
    # Crear analizador
    analizador = AnalisisMasaMeteoritos()
    
    # Ejemplo de uso básico - análisis anual desde CSV (comportamiento por defecto)
    print("Ejecutando análisis de ejemplo...")
    resultados = analizador.analizar_indice_masa(
        tipo_archivo='csv',
        periodo='anual',  # Por defecto
        guardar_resultados=True,
        guardar_graficos=True
    )
    
    return resultados


if __name__ == "__main__":
    main()