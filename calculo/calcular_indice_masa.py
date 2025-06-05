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
from matplotlib.gridspec import GridSpec
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MeteoriteMassAnalyzer:
    """
    Clase principal para el análisis de índice de masa de meteoritos.
    """
    
    def __init__(self, project_root=None):
        """
        Inicializa el analizador.
        
        Parámetros:
        -----------
        project_root : str, opcional
            Ruta raíz del proyecto. Si None, se calcula automáticamente.
        """
        if project_root is None:
            # Obtener la ruta del proyecto desde la ubicación del archivo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_root = os.path.dirname(current_dir)  # Subir un nivel desde /calculo
        else:
            self.project_root = project_root
            
        self.data_dir = os.path.join(self.project_root, 'data', 'processed')
        self.reports_dir = os.path.join(self.project_root, 'reports')
        self.figures_dir = os.path.join(self.project_root, 'reports', 'figures')
        
        # Crear directorios si no existen
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        
        print(f"Proyecto inicializado:")
        print(f"  - Raíz del proyecto: {self.project_root}")
        print(f"  - Datos: {self.data_dir}")
        print(f"  - Reportes: {self.reports_dir}")
        print(f"  - Figuras: {self.figures_dir}")
    
    def load_data(self, file_type='csv', file_name=None):
        """
        Carga datos desde archivo CSV o TXT.
        
        Parámetros:
        -----------
        file_type : str
            'csv' para archivo CSV con headers, 'txt' para archivo TXT simple
        file_name : str, opcional
            Nombre específico del archivo. Si None, usa nombres por defecto.
            
        Retorna:
        --------
        tuple : (amplitudes, dataframe_original)
            - amplitudes: numpy.array con valores de amplitud
            - dataframe_original: pandas.DataFrame (CSV) o None (TXT)
        """
        if file_name is None:
            if file_type == 'csv':
                file_path = os.path.join(self.data_dir, '2024_consolidado.csv')
            else:
                file_path = os.path.join(self.data_dir, '2024_consolidado_amax.txt')
        else:
            file_path = os.path.join(self.data_dir, file_name)
        
        print(f"Cargando datos desde: {file_path}")
        
        try:
            if file_type == 'csv':
                # Cargar CSV con pandas
                df = pd.read_csv(file_path, sep=';', decimal=',')
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
                data = np.loadtxt(file_path, dtype=str)
                data = np.char.replace(data, ",", ".").astype(float)
                amplitudes = data.flatten()
                print(f"Datos TXT cargados: {len(amplitudes)} valores")
                
                return amplitudes, None
                
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return None, None
    
    def filter_data_by_period(self, df, period='anual'):
        """
        Filtra datos por período temporal específico.
        
        Parámetros:
        -----------
        df : pandas.DataFrame
            DataFrame con columna datetime
        period : str
            Período: 'diario', 'semanal', 'mensual', 'bimestral', 
                    'trimestral', 'cuatrimestral', 'semestral', 'anual'
        
        Retorna:
        --------
        dict : Diccionario con DataFrames filtrados por período
        """
        if df is None or 'datetime' not in df.columns:
            print("No hay datos temporales disponibles para filtrado por período")
            return {'anual': df}
        
        periods_data = {}
        
        if period == 'anual':
            periods_data['2024'] = df
            
        elif period == 'diario':
            # Agrupar por día
            df['date'] = df['datetime'].dt.date
            for date in sorted(df['date'].unique()):
                date_str = str(date)
                periods_data[date_str] = df[df['date'] == date]
                
        elif period == 'semanal':
            # Agrupar por semana del año
            df['week'] = df['datetime'].dt.isocalendar().week
            for week in sorted(df['week'].unique()):
                week_str = f"Semana_{week:02d}"
                periods_data[week_str] = df[df['week'] == week]
                
        elif period == 'mensual':
            # Agrupar por mes
            df['month'] = df['datetime'].dt.month
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            for month in sorted(df['month'].unique()):
                month_str = meses[month-1]
                periods_data[month_str] = df[df['month'] == month]
                
        elif period == 'bimestral':
            # Agrupar por bimestre
            df['bimester'] = ((df['datetime'].dt.month - 1) // 2) + 1
            for bim in sorted(df['bimester'].unique()):
                bim_str = f"Bimestre_{bim}"
                periods_data[bim_str] = df[df['bimester'] == bim]
                
        elif period == 'trimestral':
            # Agrupar por trimestre
            df['quarter'] = df['datetime'].dt.quarter
            for q in sorted(df['quarter'].unique()):
                q_str = f"Trimestre_{q}"
                periods_data[q_str] = df[df['quarter'] == q]
                
        elif period == 'cuatrimestral':
            # Agrupar por cuatrimestre
            df['quadrimester'] = ((df['datetime'].dt.month - 1) // 4) + 1
            for quad in sorted(df['quadrimester'].unique()):
                quad_str = f"Cuatrimestre_{quad}"
                periods_data[quad_str] = df[df['quadrimester'] == quad]
                
        elif period == 'semestral':
            # Agrupar por semestre
            df['semester'] = ((df['datetime'].dt.month - 1) // 6) + 1
            for sem in sorted(df['semester'].unique()):
                sem_str = f"Semestre_{sem}"
                periods_data[sem_str] = df[df['semester'] == sem]
        
        print(f"Datos agrupados por {period}: {len(periods_data)} períodos")
        return periods_data
    
    def calculate_mass_index(self, amplitudes, min_amplitude=None, use_binning=False, n_bins=50):
        """
        Calcula el índice de masa usando el método estándar.
        
        Parámetros:
        -----------
        amplitudes : numpy.array
            Array con valores de amplitud
        min_amplitude : float, opcional
            Amplitud mínima para filtrar datos
        use_binning : bool, opcional
            Si usar binning logarítmico
        n_bins : int, opcional
            Número de bins si use_binning=True
            
        Retorna:
        --------
        dict : Diccionario con resultados del análisis
        """
        
        # Filtrar datos si se especifica amplitud mínima
        if min_amplitude is not None:
            amplitudes = amplitudes[amplitudes >= min_amplitude]
            print(f"Después del filtrado: {len(amplitudes)} valores")
        
        # Remover valores <= 0
        amplitudes = amplitudes[amplitudes > 0]
        
        if len(amplitudes) < 10:
            print("Error: Muy pocos datos para análisis confiable")
            return None
        
        # Ordenar amplitudes de mayor a menor
        amplitudes_sorted = np.sort(amplitudes)[::-1]
        
        # Calcular conteo acumulado descendente
        N = np.arange(1, len(amplitudes_sorted) + 1)
        
        # Aplicar binning si se solicita
        if use_binning:
            print(f"Aplicando binning logarítmico con {n_bins} bins...")
            
            log_min = np.log10(amplitudes_sorted.min())
            log_max = np.log10(amplitudes_sorted.max())
            bin_edges = np.logspace(log_min, log_max, n_bins + 1)
            
            bin_amplitudes = []
            bin_counts = []
            
            for i in range(len(bin_edges) - 1):
                mask = (amplitudes_sorted >= bin_edges[i]) & (amplitudes_sorted < bin_edges[i + 1])
                if np.sum(mask) > 0:
                    bin_amplitudes.append(np.mean(amplitudes_sorted[mask]))
                    bin_counts.append(np.sum(N <= np.sum(mask)))
            
            amplitudes_final = np.array(bin_amplitudes)
            N_final = np.array(bin_counts)
        else:
            amplitudes_final = amplitudes_sorted
            N_final = N
        
        # Preparar datos para regresión lineal
        log_A = np.log10(amplitudes_final)
        log_N = np.log10(N_final)
        
        # Realizar regresión lineal: log(N) = -(s-1) * log(A) + C
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_A, log_N)
        
        # Calcular índice de masa: s = 1 - pendiente
        mass_index = 1 - slope
        
        # Calcular estadísticas adicionales
        r_squared = r_value ** 2
        n_points = len(log_A)
        
        # Preparar resultados
        results = {
            'mass_index': mass_index,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'r_value': r_value,
            'p_value': p_value,
            'std_error': std_err,
            'n_data_points': len(amplitudes),
            'n_regression_points': n_points,
            'amplitude_range': (amplitudes.min(), amplitudes.max()),
            'amplitude_mean': amplitudes.mean(),
            'binning_used': use_binning,
            # Datos para gráficos
            'amplitudes_original': amplitudes,
            'amplitudes_final': amplitudes_final,
            'N_final': N_final,
            'log_A': log_A,
            'log_N': log_N
        }
        
        return results
    
    def print_results(self, results, period_name=""):
        """
        Imprime los resultados del análisis de forma clara.
        
        Parámetros:
        -----------
        results : dict
            Diccionario con resultados del análisis
        period_name : str
            Nombre del período analizado
        """
        if results is None:
            print("No hay resultados para mostrar")
            return
        
        header = f"RESULTADOS DEL ANÁLISIS DE ÍNDICE DE MASA"
        if period_name:
            header += f" - {period_name}"
            
        print("\n" + "="*60)
        print(header)
        print("="*60)
        print(f"Índice de masa (s):           {results['mass_index']:.4f}")
        print(f"Pendiente de regresión:       {results['slope']:.4f}")
        print(f"Intercepto:                   {results['intercept']:.4f}")
        print(f"Coeficiente de correlación:   {results['r_value']:.4f}")
        print(f"R² (bondad de ajuste):        {results['r_squared']:.4f}")
        print(f"P-value:                      {results['p_value']:.2e}")
        print(f"Error estándar:               {results['std_error']:.4f}")
        print(f"Número de datos originales:   {results['n_data_points']}")
        print(f"Puntos usados en regresión:   {results['n_regression_points']}")
        print(f"Amplitud mínima:              {results['amplitude_range'][0]:.2f}")
        print(f"Amplitud máxima:              {results['amplitude_range'][1]:.2f}")
        print(f"Amplitud promedio:            {results['amplitude_mean']:.2f}")
        print(f"Binning aplicado:             {'Sí' if results['binning_used'] else 'No'}")
        print("="*60)
        
        # Interpretación básica
        if results['r_squared'] > 0.8:
            print("✓ Excelente ajuste de la regresión")
        elif results['r_squared'] > 0.6:
            print("✓ Buen ajuste de la regresión")
        else:
            print("⚠ Ajuste de regresión podría mejorarse")
        
        print(f"✓ Índice de masa calculado: s = {results['mass_index']:.4f}")
    
    def save_results_to_file(self, results, period_name="", file_suffix=""):
        """
        Guarda los resultados en un archivo de texto.
        
        Parámetros:
        -----------
        results : dict
            Diccionario con resultados del análisis
        period_name : str
            Nombre del período analizado
        file_suffix : str
            Sufijo adicional para el nombre del archivo
        """
        if results is None:
            print("No hay resultados para guardar")
            return None
            
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if period_name:
            filename = f"indice_masa_{period_name}_{timestamp}{file_suffix}.txt"
        else:
            filename = f"indice_masa_{timestamp}{file_suffix}.txt"
            
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS\n")
                f.write("="*50 + "\n")
                f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if period_name:
                    f.write(f"Período analizado: {period_name}\n")
                f.write("\n")
                
                f.write("RESULTADOS PRINCIPALES:\n")
                f.write("-"*25 + "\n")
                f.write(f"Índice de masa (s):           {results['mass_index']:.4f}\n")
                f.write(f"Pendiente de regresión:       {results['slope']:.4f}\n")
                f.write(f"Intercepto:                   {results['intercept']:.4f}\n")
                f.write(f"Coeficiente de correlación:   {results['r_value']:.4f}\n")
                f.write(f"R² (bondad de ajuste):        {results['r_squared']:.4f}\n")
                f.write(f"P-value:                      {results['p_value']:.2e}\n")
                f.write(f"Error estándar:               {results['std_error']:.4f}\n")
                f.write("\n")
                
                f.write("ESTADÍSTICAS DE DATOS:\n")
                f.write("-"*22 + "\n")
                f.write(f"Número de datos originales:   {results['n_data_points']}\n")
                f.write(f"Puntos usados en regresión:   {results['n_regression_points']}\n")
                f.write(f"Amplitud mínima:              {results['amplitude_range'][0]:.2f}\n")
                f.write(f"Amplitud máxima:              {results['amplitude_range'][1]:.2f}\n")
                f.write(f"Amplitud promedio:            {results['amplitude_mean']:.2f}\n")
                f.write(f"Binning aplicado:             {'Sí' if results['binning_used'] else 'No'}\n")
                f.write("\n")
                
                f.write("INTERPRETACIÓN:\n")
                f.write("-"*15 + "\n")
                if results['r_squared'] > 0.8:
                    f.write("✓ Excelente ajuste de la regresión\n")
                elif results['r_squared'] > 0.6:
                    f.write("✓ Buen ajuste de la regresión\n")
                else:
                    f.write("⚠ Ajuste de regresión podría mejorarse\n")
                
                f.write(f"✓ Índice de masa calculado: s = {results['mass_index']:.4f}\n")
            
            print(f"Resultados guardados en: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error al guardar resultados: {e}")
            return None
    
    def create_summary_plot(self, results, period_name="", save_plot=True):
        """
        Crea un gráfico resumen con análisis completo.
        
        Parámetros:
        -----------
        results : dict
            Diccionario con resultados del análisis
        period_name : str
            Nombre del período analizado
        save_plot : bool
            Si guardar el gráfico en archivo
        """
        if results is None:
            print("No hay resultados para graficar")
            return
        
        # Crear figura con grilla personalizada
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 4, figure=fig, hspace=0.4, wspace=0.4)
        
        # 1. Línea de ajuste (3x2 = ocupa 3 columnas y 2 filas)
        ax1 = fig.add_subplot(gs[0:2, 0:3])
        log_A = results['log_A']
        log_N = results['log_N']
        
        # Datos observados
        ax1.scatter(log_A, log_N, alpha=0.7, s=30, color='blue', label='Datos observados')
        
        # Línea de ajuste
        A_fit = np.linspace(log_A.min(), log_A.max(), 100)
        N_fit = results['slope'] * A_fit + results['intercept']
        ax1.plot(A_fit, N_fit, 'r-', linewidth=2, 
                label=f'Ajuste: s = {results["mass_index"]:.3f}')
        
        ax1.set_xlabel('log₁₀(Amplitud)')
        ax1.set_ylabel('log₁₀(N acumulado)')
        ax1.set_title(f'Regresión Log-Log (R² = {results["r_squared"]:.4f})')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Distribución de residuos (1x2 = 1 columna, 2 filas)
        ax2 = fig.add_subplot(gs[0:2, 3])
        predicted = results['slope'] * log_A + results['intercept']
        residuals = log_N - predicted
        ax2.boxplot(residuals, vert=True)
        ax2.set_ylabel('Residuos')
        ax2.set_title('Distribución de Residuos')
        ax2.grid(True, alpha=0.3)
        
        # 3. Distribución de amplitudes (2x1 = 2 columnas, 1 fila)
        ax3 = fig.add_subplot(gs[2, 0:2])
        ax3.hist(results['amplitudes_original'], bins=50, alpha=0.7, 
                color='green', edgecolor='black')
        ax3.set_xlabel('Amplitud')
        ax3.set_ylabel('Frecuencia')
        ax3.set_title('Distribución de Amplitudes')
        ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3)
        
        # 4. Residuos del ajuste (2x1 = 2 columnas, 1 fila)
        ax4 = fig.add_subplot(gs[2, 2:4])
        ax4.scatter(log_A, residuals, alpha=0.7, s=20, color='orange')
        ax4.axhline(y=0, color='red', linestyle='--', alpha=0.8)
        ax4.set_xlabel('log₁₀(Amplitud)')
        ax4.set_ylabel('Residuos')
        ax4.set_title('Residuos del Ajuste vs Amplitud')
        ax4.grid(True, alpha=0.3)
        
        # Título general
        title = 'Análisis de Índice de Masa'
        if period_name:
            title += f' - {period_name}'
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        plt.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.92, 
                           wspace=0.3, hspace=0.4)
        
        plt.show()
        
        # Guardar figura si se solicita
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if period_name:
                filename = f"indice_masa_{period_name}_{timestamp}.png"
            else:
                filename = f"indice_masa_{timestamp}.png"
            
            filepath = os.path.join(self.figures_dir, filename)
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado como: {filepath}")
            
        return fig
    
    def analyze_mass_index(self, file_type='csv', period='anual', min_amplitude=None, 
                          use_binning=False, n_bins=50, save_results=True, 
                          save_plots=True, file_name=None):
        """
        Función principal para analizar el índice de masa.
        
        Parámetros:
        -----------
        file_type : str
            'csv' o 'txt' según el tipo de archivo
        period : str
            Período de análisis: 'anual', 'mensual', 'semanal', etc.
        min_amplitude : float, opcional
            Amplitud mínima para filtrar datos
        use_binning : bool
            Si usar binning logarítmico
        n_bins : int
            Número de bins si use_binning=True
        save_results : bool
            Si guardar resultados en archivo txt
        save_plots : bool
            Si guardar gráficos
        file_name : str, opcional
            Nombre específico del archivo
            
        Retorna:
        --------
        dict : Diccionario con todos los resultados por período
        """
        
        print("="*60)
        print("INICIANDO ANÁLISIS DE ÍNDICE DE MASA DE METEORITOS")
        print("="*60)
        print(f"Tipo de archivo: {file_type.upper()}")
        print(f"Período de análisis: {period}")
        if min_amplitude:
            print(f"Amplitud mínima: {min_amplitude}")
        if use_binning:
            print(f"Binning logarítmico: {n_bins} bins")
        print()
        
        # Cargar datos
        amplitudes, df = self.load_data(file_type, file_name)
        
        if amplitudes is None:
            print("Error: No se pudieron cargar los datos")
            return None
        
        # Filtrar por período si es CSV y hay datos temporales
        if file_type == 'csv' and df is not None and 'datetime' in df.columns:
            periods_data = self.filter_data_by_period(df, period)
        else:
            # Para archivos TXT o cuando no hay datos temporales
            periods_data = {'todos_los_datos': df if df is not None else amplitudes}
        
        all_results = {}
        
        # Analizar cada período
        for period_name, period_data in periods_data.items():
            print(f"\n--- Analizando período: {period_name} ---")
            
            # Extraer amplitudes para este período
            if isinstance(period_data, pd.DataFrame):
                period_amplitudes = period_data['amax'].values
            else:
                period_amplitudes = amplitudes  # Para datos TXT
            
            # Calcular índice de masa
            results = self.calculate_mass_index(
                period_amplitudes, 
                min_amplitude=min_amplitude,
                use_binning=use_binning, 
                n_bins=n_bins
            )
            
            if results is not None:
                # Mostrar resultados
                self.print_results(results, period_name)
                
                # Guardar resultados si se solicita
                if save_results:
                    self.save_results_to_file(results, period_name)
                
                # Crear gráfico si se solicita
                if save_plots:
                    self.create_summary_plot(results, period_name, save_plot=True)
                
                all_results[period_name] = results
            else:
                print(f"No se pudo calcular el índice para el período {period_name}")
        
        print(f"\n{'='*60}")
        print(f"ANÁLISIS COMPLETADO - {len(all_results)} períodos procesados")
        print(f"{'='*60}")
        
        return all_results


def main():
    """
    Función principal para ejecutar desde línea de comandos.
    """
    # Crear analizador
    analyzer = MeteoriteMassAnalyzer()
    
    # Ejemplo de uso básico - análisis anual desde CSV
    print("Ejecutando análisis de ejemplo...")
    results = analyzer.analyze_mass_index(
        file_type='csv',
        period='anual',
        save_results=True,
        save_plots=True
    )
    
    return results


if __name__ == "__main__":
    main()