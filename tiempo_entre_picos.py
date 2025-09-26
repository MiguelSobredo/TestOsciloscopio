import pandas as pd
import glob

# Configuración del osciloscopio
sample_rate = 10_000_000  # 10 MS/s
dt = 1 / sample_rate      # Tiempo entre muestras en segundos

# Buscar archivos CSV en el directorio actual
csv_files = glob.glob("*.csv")

# Analizar cada archivo
for file in csv_files:
    try:
        df = pd.read_csv(file)

        # Verificar que CH1 existe
        if 'CH1' not in df.columns:
            print(f"{file}: No se encontró CH1")
            continue

        # Índice del máximo de CH1
        idx_ch1 = df['CH1'].idxmax()

        # Buscar el canal entre CH2, CH3, CH4 cuyo máximo esté más cercano en tiempo a CH1
        closest_channel = None
        closest_time_diff = float('inf')

        for ch in ['CH2', 'CH3', 'CH4']:
            if ch in df.columns:
                idx_ch = df[ch].idxmax()
                time_diff = abs(idx_ch - idx_ch1) * dt
                if time_diff < closest_time_diff:
                    closest_time_diff = time_diff
                    closest_channel = ch

        if closest_channel:
            print(f"{file}: Δt entre máximo de CH1 y {closest_channel} = {closest_time_diff * 1000:.3f} ms")
        else:
            print(f"{file}: No se encontraron CH2, CH3 o CH4 para comparar")

    except Exception as e:
        print(f"Error al procesar {file}: {e}")