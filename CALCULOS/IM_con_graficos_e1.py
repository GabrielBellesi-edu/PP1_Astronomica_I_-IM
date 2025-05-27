# Calculadora de Índice de Masa de Meteoritos 
# Jupyter Notebook Version

# ================================
# INSTALACIÓN DE DEPENDENCIAS
# ================================
# Ejecuta esta celda primero si no tienes las librerías instaladas:
# !pip install numpy pandas matplotlib plotly scipy ipywidgets

# ================================
# IMPORTAR LIBRERÍAS
# ================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import ipywidgets as widgets
from IPython.display import display, clear_output
import io
import re

print("✅ Librerías importadas correctamente")

# ================================
# FUNCIONES PRINCIPALES
# ================================

def calculate_mass_index(amplitudes):
    """
    Calcula el índice de masa a partir de valores de amplitud
    usando la relación N ∝ A^(-(s-1))
    """
    # Eliminar valores inválidos y convertir a numpy array
    amplitudes = np.array([float(a) for a in amplitudes if float(a) > 0])
    
    if len(amplitudes) == 0:
        raise ValueError("No hay valores válidos de amplitud")
    
    # Ordenar de mayor a menor
    amplitudes_sorted = np.sort(amplitudes)[::-1]
    
    # Calcular N (conteo acumulado)
    N = np.arange(1, len(amplitudes_sorted) + 1)
    
    # Crear DataFrame con todos los datos
    df_full = pd.DataFrame({
        'A': amplitudes_sorted,
        'N': N,
        'log_A': np.log10(amplitudes_sorted),
        'log_N': np.log10(N)
    })
    
    # Crear bins para reducir ruido en la regresión
    df_binned = create_bins(amplitudes_sorted, num_bins=50)
    
    # Realizar regresión lineal en escala logarítmica
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df_binned['log_A'], df_binned['log_N']
    )
    
    # Calcular índice de masa: s = 1 - slope
    mass_index = 1 - slope
    r_squared = r_value**2
    
    return {
        'df_full': df_full,
        'df_binned': df_binned,
        'mass_index': mass_index,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'p_value': p_value,
        'std_err': std_err,
        'total_detections': len(amplitudes),
        'min_amplitude': np.min(amplitudes),
        'max_amplitude': np.max(amplitudes),
        'mean_amplitude': np.mean(amplitudes),
        'std_amplitude': np.std(amplitudes)
    }

def create_bins(amplitudes, num_bins=50):
    """
    Crea bins logarítmicamente espaciados para reducir ruido
    """
    min_amp = np.min(amplitudes)
    max_amp = np.max(amplitudes)
    
    # Crear bins en escala logarítmica
    log_bins = np.linspace(np.log10(min_amp), np.log10(max_amp), num_bins + 1)
    bins = 10**log_bins
    
    # Contar elementos en cada bin
    bin_data = []
    for i in range(len(bins) - 1):
        bin_min = bins[i]
        bin_max = bins[i + 1]
        
        # Contar amplitudes en este rango
        count = np.sum((amplitudes >= bin_min) & (amplitudes < bin_max))
        
        if count > 0:
            # Usar media geométrica del bin como representativo
            bin_center = np.sqrt(bin_min * bin_max)
            bin_data.append({
                'A': bin_center,
                'N': count,
                'log_A': np.log10(bin_center),
                'log_N': np.log10(count)
            })
    
    # Convertir a conteo acumulado (de mayor a menor amplitud)
    df_bins = pd.DataFrame(bin_data)
    if len(df_bins) > 0:
        df_bins = df_bins.sort_values('A', ascending=False).reset_index(drop=True)
        df_bins['N'] = df_bins['N'].cumsum()
        df_bins['log_N'] = np.log10(df_bins['N'])
    
    return df_bins

def plot_results(results):
    """
    Crear gráficos de los resultados
    """
    df_binned = results['df_binned']
    slope = results['slope']
    intercept = results['intercept']
    
    # Crear subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Distribución log(N) vs log(A)
    ax1.scatter(df_binned['log_A'], df_binned['log_N'], 
               alpha=0.7, color='blue', s=30, label='Datos binneados')
    
    # Línea de ajuste
    x_fit = np.array([df_binned['log_A'].min(), df_binned['log_A'].max()])
    y_fit = slope * x_fit + intercept
    ax1.plot(x_fit, y_fit, 'r-', linewidth=2, 
             label=f'Ajuste: y = {slope:.4f}x + {intercept:.4f}')
    
    ax1.set_xlabel('log(A)')
    ax1.set_ylabel('log(N)')
    ax1.set_title('Distribución log(N) vs log(A)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Histograma de amplitudes
    ax2.hist(np.log10(results['df_full']['A']), bins=50, alpha=0.7, color='green')
    ax2.set_xlabel('log(A)')
    ax2.set_ylabel('Frecuencia')
    ax2.set_title('Distribución de log(Amplitudes)')
    ax2.grid(True, alpha=0.3)
    
    # 3. N vs A en escala normal
    ax3.scatter(df_binned['A'], df_binned['N'], alpha=0.7, color='purple', s=30)
    ax3.set_xlabel('Amplitud (A)')
    ax3.set_ylabel('Número acumulado (N)')
    ax3.set_title('N vs A (Escala lineal)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Residuos del ajuste
    y_pred = slope * df_binned['log_A'] + intercept
    residuals = df_binned['log_N'] - y_pred
    ax4.scatter(df_binned['log_A'], residuals, alpha=0.7, color='orange', s=30)
    ax4.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax4.set_xlabel('log(A)')
    ax4.set_ylabel('Residuos')
    ax4.set_title('Residuos del Ajuste')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_interactive(results):
    """
    Crear gráfico interactivo con Plotly
    """
    df_binned = results['df_binned']
    slope = results['slope']
    intercept = results['intercept']
    
    # Crear gráfico
    fig = go.Figure()
    
    # Datos binneados
    fig.add_trace(go.Scatter(
        x=df_binned['log_A'],
        y=df_binned['log_N'],
        mode='markers',
        name='Datos binneados',
        marker=dict(color='blue', size=8),
        hovertemplate='log(A): %{x:.3f}<br>log(N): %{y:.3f}<br>A: %{customdata[0]:.3f}<br>N: %{customdata[1]}<extra></extra>',
        customdata=np.column_stack((df_binned['A'], df_binned['N']))
    ))
    
    # Línea de ajuste
    x_fit = np.array([df_binned['log_A'].min(), df_binned['log_A'].max()])
    y_fit = slope * x_fit + intercept
    
    fig.add_trace(go.Scatter(
        x=x_fit,
        y=y_fit,
        mode='lines',
        name=f'Ajuste: y = {slope:.4f}x + {intercept:.4f}',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title=f'Distribución log(N) vs log(A) - Índice de masa s = {results["mass_index"]:.4f}',
        xaxis_title='log(A)',
        yaxis_title='log(N)',
        hovermode='closest',
        showlegend=True,
        width=800,
        height=600
    )
    
    fig.show()

def interpret_mass_index(s):
    """
    Interpretar el valor del índice de masa
    """
    if s < 1.5:
        return "🔹 Población dominada por meteoritos pequeños"
    elif s < 2.0:
        return "🔸 Distribución intermedia"
    else:
        return "🔶 Mayor proporción de meteoritos grandes"

def print_results(results):
    """
    Imprimir resultados formateados
    """
    print("="*60)
    print("📊 RESULTADOS DEL ANÁLISIS DE ÍNDICE DE MASA")
    print("="*60)
    
    print(f"\n🎯 ÍNDICE DE MASA (s): {results['mass_index']:.4f}")
    print(f"📈 CORRELACIÓN (R²): {results['r_squared']:.4f}")
    
    correlation_quality = "Excelente" if results['r_squared'] > 0.95 else \
                         "Bueno" if results['r_squared'] > 0.90 else "Moderado"
    print(f"✅ CALIDAD DEL AJUSTE: {correlation_quality}")
    
    print(f"\n📐 ECUACIÓN DE AJUSTE:")
    print(f"   log(N) = {results['slope']:.4f} × log(A) + {results['intercept']:.4f}")
    print(f"   P-value: {results['p_value']:.2e}")
    print(f"   Error estándar: {results['std_err']:.4f}")
    
    print(f"\n📊 ESTADÍSTICAS DE DATOS:")
    print(f"   Total detecciones: {results['total_detections']:,}")
    print(f"   Amplitud mínima: {results['min_amplitude']:.4f}")
    print(f"   Amplitud máxima: {results['max_amplitude']:.4f}")
    print(f"   Amplitud promedio: {results['mean_amplitude']:.4f}")
    print(f"   Desviación estándar: {results['std_amplitude']:.4f}")
    
    print(f"\n🔍 INTERPRETACIÓN:")
    print(f"   {interpret_mass_index(results['mass_index'])}")
    
    print(f"\n📚 GUÍA DE INTERPRETACIÓN:")
    print(f"   • s ≈ 1.0-1.5: Población dominada por meteoritos pequeños")
    print(f"   • s ≈ 1.5-2.0: Distribución intermedia")  
    print(f"   • s > 2.0: Mayor proporción de meteoritos grandes")
    
    print("="*60)

# ================================
# FUNCIÓN PRINCIPAL DE ANÁLISIS
# ================================

def analyze_meteorite_data(file_path=None, data=None):
    """
    Función principal para analizar datos de meteoritos
    
    Parameters:
    - file_path: ruta al archivo txt con datos
    - data: lista de valores de amplitud (alternativa al archivo)
    """
    
    if file_path is not None:
        # Leer desde archivo
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parsear valores
            values = re.split(r'[\s,;]+', content.strip())
            amplitudes = [float(v) for v in values if v and v.replace('.', '').replace('-', '').isdigit()]
            
            print(f"✅ Archivo cargado: {len(amplitudes):,} valores")
            
        except Exception as e:
            print(f"❌ Error al leer archivo: {e}")
            return
    
    elif data is not None:
        amplitudes = data
        print(f"✅ Datos cargados: {len(amplitudes):,} valores")
    
    else:
        print("❌ Debe proporcionar file_path o data")
        return
    
    if len(amplitudes) == 0:
        print("❌ No se encontraron valores válidos")
        return
    
    # Calcular índice de masa
    print("\n⏳ Calculando índice de masa...")
    try:
        results = calculate_mass_index(amplitudes)
        
        # Mostrar resultados
        print_results(results)
        
        # Crear gráficos
        print("\n📈 Generando gráficos...")
        plot_results(results)
        
        # Gráfico interactivo
        print("\n🔍 Gráfico interactivo:")
        plot_interactive(results)
        
        return results
        
    except Exception as e:
        print(f"❌ Error en el cálculo: {e}")
        return None

print("\n🚀 Funciones cargadas correctamente!")
print("\n📝 INSTRUCCIONES DE USO:")
print("1. Para analizar desde archivo: analyze_meteorite_data('ruta_a_tu_archivo.txt')")
print("2. Para analizar datos directos: analyze_meteorite_data(data=[lista_de_amplitudes])")
print("3. Ejemplo: analyze_meteorite_data(data=np.random.lognormal(2, 1, 1000))")

# ================================
# ANÁLISIS DE TUS DATOS REALES
# ================================
ruta_data = 'Test/2024amax.txt'
print("\n" + "="*60)
print("🔥 ANÁLISIS DE DATOS " + ruta_data )
print("="*60)

# Cargar y analizar tus datos

results = analyze_meteorite_data(ruta_data)

print("\n ¡Análisis completado!")
