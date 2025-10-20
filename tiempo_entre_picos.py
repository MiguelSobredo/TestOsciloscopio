import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import glob

# Configuración del osciloscopio
sample_rate = 2_500_000  # 10 MS/s
dt = 1 / sample_rate      # Tiempo entre muestras en segundos

# Función para convertir datos de complemento a 2 a valores con signo
def complemento_a2_to_signed(values, bits=8):
    max_val = 2 ** bits
    signed_values = np.where(values >= max_val // 2, values - max_val, values)
    return signed_values

# Buscar archivos CSV en el directorio actual
csv_files = glob.glob("*.csv")

# Lista para almacenar resultados
resultados = []

if csv_files:
    for file in csv_files:
        df = pd.read_csv(file)

        if 'CH1' in df.columns:
            ch1_original = df['CH1'].astype(int).values
            ch1_signed = complemento_a2_to_signed(ch1_original)

            # Detectar picos principales
            min_distance = 10_000  # Ajusta según la separación mínima esperada entre pulsos
            peaks, _ = find_peaks(ch1_signed, height=0, distance=min_distance)

            # Si hay al menos 2 picos, tomar los dos más altos
            if len(peaks) >= 2:
                peak_heights = ch1_signed[peaks]
                top_two_indices = np.argsort(peak_heights)[-2:]
                top_two_peaks = peaks[top_two_indices]
                top_two_peaks = np.sort(top_two_peaks)

                # Calcular tiempo entre los dos picos más altos
                time_diff_ms = abs(top_two_peaks[1] - top_two_peaks[0]) * dt * 1000
                print(f"{file}: Tiempo entre los dos picos más altos = {time_diff_ms:.3f} ms")
                resultados.append({'Archivo': file, 'Tiempo_ms': round(time_diff_ms, 3)})
            else:
                print(f"{file}: No se encontraron 2 picos principales. Se guarda 0.")
                resultados.append({'Archivo': file, 'Tiempo_ms': 0})
        else:
            print(f"{file}: No se encontró CH1. Se guarda 0.")
            resultados.append({'Archivo': file, 'Tiempo_ms': 0})
else:
    print("No se encontraron archivos CSV en el directorio.")

# Guardar resultados en un archivo CSV
df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv('resultados_picos.csv', index=False)