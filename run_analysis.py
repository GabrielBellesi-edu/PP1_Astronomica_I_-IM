#!/usr/bin/env python3
"""
Script de línea de comandos para ejecutar análisis de índice de masa.
Ubicación: run_analysis.py (en la raíz del proyecto)

Uso:
    python run_analysis.py --help
    python run_analysis.py --basic
    python run_analysis.py --period mensual --min-amp 2.0
    python run_analysis.py --compare-methods
"""

import argparse
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar el módulo
sys.path.append(str(Path(__file__).parent))

from calculo.calcular_indice_masa import MeteoriteMassAnalyzer


def run_basic_analysis(analyzer):
    """Ejecutar análisis básico estándar."""
    print("🔬 EJECUTANDO ANÁLISIS BÁSICO")
    print("="*40)
    
    results = analyzer.analyze_mass_index(
        file_type='csv',
        period='anual',
        save_results=True,
        save_plots=True
    )
    
    return results


def run_period_analysis(analyzer, period, min_amplitude=None):
    """Ejecutar análisis por período específico."""
    print(f"📅 EJECUTANDO ANÁLISIS POR {period.upper()}")
    print("="*50)
    
    results = analyzer.analyze_mass_index(
        file_type='csv',
        period=period,
        min_amplitude=min_amplitude,
        save_results=True,
        save_plots=True
    )
    
    return results


def run_comparison_analysis(analyzer):
    """Ejecutar análisis comparativo de métodos."""
    print("⚖️ EJECUTANDO ANÁLISIS COMPARATIVO")
    print("="*45)
    
    # Configuraciones para comparar
    configs = [
        {'name': 'Estándar', 'min_amplitude': None, 'use_binning': False},
        {'name': 'Filtrado_2.0', 'min_amplitude': 2.0, 'use_binning': False},
        {'name': 'Filtrado_5.0', 'min_amplitude': 5.0, 'use_binning': False},
        {'name': 'Binning_50', 'min_amplitude': None, 'use_binning': True, 'n_bins': 50},
        {'name': 'Combinado', 'min_amplitude': 2.0, 'use_binning': True, 'n_bins': 50}
    ]
    
    all_results = {}
    
    for config in configs:
        print(f"\n--- Ejecutando: {config['name']} ---")
        
        result = analyzer.analyze_mass_index(
            file_type='csv',
            period='anual',
            min_amplitude=config.get('min_amplitude'),
            use_binning=config.get('use_binning', False),
            n_bins=config.get('n_bins', 50),
            save_results=False,  # No guardar cada uno individualmente
            save_plots=False
        )
        
        if result and 'todos_los_datos' in result:
            all_results[config['name']] = result['todos_los_datos']
    
    # Crear tabla comparativa
    print_comparison_table(all_results)
    
    # Guardar resumen comparativo
    save_comparison_summary(analyzer, all_results)
    
    return all_results


def print_comparison_table(results):
    """Imprimir tabla comparativa de resultados."""
    if not results:
        print("No hay resultados para comparar")
        return
    
    print(f"\n📋 TABLA COMPARATIVA DE MÉTODOS:")
    print("=" * 100)
    print(f"{'Método':<15} {'N_datos':<8} {'N_regres':<9} {'Índice_s':<10} {'R²':<8} {'P-value':<12} {'Error_std':<10}")
    print("=" * 100)
    
    for method, result in results.items():
        print(f"{method:<15} {result['n_data_points']:<8} {result['n_regression_points']:<9} "
              f"{result['mass_index']:<10.4f} {result['r_squared']:<8.4f} {result['p_value']:<12.2e} "
              f"{result['std_error']:<10.4f}")
    
    print("=" * 100)


def save_comparison_summary(analyzer, results):
    """Guardar resumen comparativo en archivo."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comparacion_metodos_{timestamp}.txt"
    filepath = os.path.join(analyzer.reports_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("COMPARACIÓN DE MÉTODOS - ÍNDICE DE MASA\n")
            f.write("="*50 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("RESULTADOS COMPARATIVOS:\n")
            f.write("-"*25 + "\n")
            f.write(f"{'Método':<15} {'N_datos':<8} {'Índice_s':<10} {'R²':<8} {'P-value':<12}\n")
            f.write("-"*60 + "\n")
            
            for method, result in results.items():
                f.write(f"{method:<15} {result['n_data_points']:<8} "
                       f"{result['mass_index']:<10.4f} {result['r_squared']:<8.4f} "
                       f"{result['p_value']:<12.2e}\n")
            
            f.write(f"\nMEJOR MÉTODO (por R²):\n")
            best_method = max(results.items(), key=lambda x: x[1]['r_squared'])
            f.write(f"  • {best_method[0]}: s = {best_method[1]['mass_index']:.4f}, R² = {best_method[1]['r_squared']:.4f}\n")
        
        print(f"✅ Resumen comparativo guardado en: {filepath}")
        
    except Exception as e:
        print(f"❌ Error al guardar resumen: {e}")


def run_custom_analysis(analyzer, args):
    """Ejecutar análisis con parámetros personalizados."""
    print("🛠️ EJECUTANDO ANÁLISIS PERSONALIZADO")
    print("="*45)
    
    results = analyzer.analyze_mass_index(
        file_type=args.file_type,
        period=args.period,
        min_amplitude=args.min_amplitude,
        use_binning=args.use_binning,
        n_bins=args.n_bins,
        save_results=True,
        save_plots=True
    )
    
    return results


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Análisis de Índice de Masa de Meteoritos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_analysis.py --basic
  python run_analysis.py --period mensual
  python run_analysis.py --period anual --min-amp 2.0
  python run_analysis.py --compare-methods
  python run_analysis.py --period trimestral --binning --n-bins 25
        """
    )
    
    # Argumentos principales
    parser.add_argument('--basic', action='store_true',
                       help='Ejecutar análisis básico estándar')
    
    parser.add_argument('--compare-methods', action='store_true',
                       help='Ejecutar comparación de métodos')
    
    parser.add_argument('--period', choices=['anual', 'mensual', 'semanal', 'trimestral', 
                                           'bimestral', 'cuatrimestral', 'semestral'],
                       default='anual', help='Período de análisis (default: anual)')
    
    parser.add_argument('--file-type', choices=['csv', 'txt'], default='csv',
                       help='Tipo de archivo de datos (default: csv)')
    
    parser.add_argument('--min-amp', type=float, dest='min_amplitude',
                       help='Amplitud mínima para filtrar datos')
    
    parser.add_argument('--binning', action='store_true', dest='use_binning',
                       help='Usar binning logarítmico')
    
    parser.add_argument('--n-bins', type=int, default=50,
                       help='Número de bins para binning logarítmico (default: 50)')
    
    parser.add_argument('--no-save', action='store_true',
                       help='No guardar resultados ni gráficos')
    
    args = parser.parse_args()
    
    # Mostrar configuración
    print("🚀 INICIANDO ANÁLISIS DE ÍNDICE DE MASA")
    print("="*50)
    
    # Crear analizador
    try:
        analyzer = MeteoriteMassAnalyzer()
    except Exception as e:
        print(f"❌ Error al inicializar el analizador: {e}")
        return 1
    
    # Ejecutar análisis según argumentos
    try:
        if args.basic:
            results = run_basic_analysis(analyzer)
            
        elif args.compare_methods:
            results = run_comparison_analysis(analyzer)
            
        else:
            # Análisis personalizado
            results = run_custom_analysis(analyzer, args)
        
        if results:
            print(f"\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
            print(f"   • Resultados en: {analyzer.reports_dir}")
            print(f"   • Gráficos en: {analyzer.figures_dir}")
        else:
            print(f"\n❌ ERROR EN EL ANÁLISIS")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Análisis interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())