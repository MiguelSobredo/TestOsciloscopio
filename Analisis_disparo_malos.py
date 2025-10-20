import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os
import glob
# Configuración
sample_rate = 2_500_000  # 2.5 MS/s
dt = 1 / sample_rate      # Tiempo entre muestras en segundos
limite_inferior = 39.725  # Nuevo límite inferior
limite_superior = 40.178  # Nuevo límite superior
ciclo_muestras = int(sample_rate / 50)  # 1 ciclo a 50 Hz ≈ 200000 muestras
csv_files = glob.glob("*.csv")

# Definir funciones
def complemento_a2_to_signed(values, bits=8):
    max_val = 2 ** bits
    return np.where(values >= max_val // 2, values - max_val, values)

def moving_average(signal, window):
    return np.convolve(signal, np.ones(window)/window, mode='same')

def zero_crossing_after_peak(signal, peak_index):
    end = min(len(signal) - 1, peak_index + ciclo_muestras)
    for i in range(peak_index, end):
        if signal[i] > 0 and signal[i + 1] < 0:
            return i
    return None

def drop_before_cross_ma(short_ma, long_ma, cross_index, original_signal):
    for i in range(cross_index, 1, -1):
        if short_ma[i] < long_ma[i] and short_ma[i - 1] >= long_ma[i - 1]:
            before_window = original_signal[max(0, i - 200):i]
            after_window = original_signal[i:min(len(original_signal), i + 200)]
            if before_window.size > 0 and after_window.size > 0:
                if np.mean(before_window) > 40 and np.mean(after_window) < 10:
                    return i
    return None
# Inicializar archivo CSV de resultados
results_file = 'results.csv'
if not os.path.exists(results_file):
    pd.DataFrame(columns=['Archivo', 'Δpicos(ms)', 'Δbajada-cruce1(ms)', 'Δbajada-cruce2(ms)', 'Nº Bajadas']).to_csv(results_file, index=False)

# Lista para almacenar resultados
for file in csv_files:
    if os.path.exists(file):
        df = pd.read_csv(file)
        if {'CH1', 'CH2', 'CH3'}.issubset(df.columns):
            # Convertir señales a valores con signo
            ch1_signed = complemento_a2_to_signed(df['CH1'].astype(int).values)
            ch2_signed = complemento_a2_to_signed(df['CH2'].astype(int).values)
            ch3_signed = complemento_a2_to_signed(df['CH3'].astype(int).values)

            # Suavizar señales
            ch2_smooth = moving_average(ch2_signed, 50)
            ch3_short_ma = moving_average(ch3_signed, 500)
            ch3_long_ma = moving_average(ch3_signed, 1000)

            # Detectar picos en CH1 (dos más altos)
            peaks, _ = find_peaks(ch1_signed, height=0, distance=10_000)
            if len(peaks) >= 2:
                peak_heights = ch1_signed[peaks]
                top_two_indices = np.argsort(peak_heights)[-2:]
                top_two_peaks = np.sort(peaks[top_two_indices])
                time_diff_ms = abs(top_two_peaks[1] - top_two_peaks[0]) * dt * 1000
                tiempo_filtrado = round(time_diff_ms, 3) if limite_inferior <= time_diff_ms <= limite_superior else 0
            else:
                tiempo_filtrado = 0
                top_two_peaks = []

            # Calcular tiempos Bajada-Cruce
            tiempos_bajada_cruce = []
            cruces_indices = []
            bajadas_indices = []
            for peak in top_two_peaks:
                zc_index = zero_crossing_after_peak(ch2_smooth, peak)
                cruces_indices.append(zc_index)
                if zc_index is not None:
                    drop_index = drop_before_cross_ma(ch3_short_ma, ch3_long_ma, zc_index, ch3_signed)
                    bajadas_indices.append(drop_index)
                    if drop_index is not None:
                        tiempo_ms = round((zc_index - drop_index) * dt * 1000, 3)
                        tiempos_bajada_cruce.append(tiempo_ms)
                    else:
                        tiempos_bajada_cruce.append(None)
                else:
                    bajadas_indices.append(None)
                    tiempos_bajada_cruce.append(None)

            # Contar todas las bajadas en CH3 según la lógica
            total_bajadas = 0
            for i in range(1, len(ch3_short_ma)):
                if ch3_short_ma[i] < ch3_long_ma[i] and ch3_short_ma[i - 1] >= ch3_long_ma[i - 1]:
                    before_window = ch3_signed[max(0, i - 200):i]
                    after_window = ch3_signed[i:min(len(ch3_signed), i + 200)]
                    if before_window.size > 0 and after_window.size > 0:
                        if np.mean(before_window) > 40 and np.mean(after_window) < 10:
                            total_bajadas += 1
            # Almacenar resultados
            result = {
                'Archivo': file,
                'Δpicos(ms)': tiempo_filtrado,
                'Δbajada-cruce1(ms)': tiempos_bajada_cruce[0] if len(tiempos_bajada_cruce) > 0 else None,
                'Δbajada-cruce2(ms)': tiempos_bajada_cruce[1] if len(tiempos_bajada_cruce) > 1 else None,
                'Nº Bajadas': total_bajadas
            }

            # Guardar resultados en CSV
            pd.DataFrame([result]).to_csv(results_file, mode='a', header=False, index=False)

            # Gráfico
            fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
            axs[0].plot(ch1_signed, label='CH1')
            axs[0].plot(top_two_peaks, ch1_signed[top_two_peaks], 'ro', label='Picos CH1')
            for i, peak in enumerate(top_two_peaks):
                axs[0].annotate(f"Pico {i+1}\nIdx={peak}", (peak, ch1_signed[peak]), xytext=(0, 10),
                                textcoords="offset points", ha='center', color='blue')
            axs[0].legend(); axs[0].grid(True); axs[0].set_ylabel('CH1')

            axs[1].plot(ch2_signed, label='CH2 Original', color='orange', alpha=0.5)
            axs[1].plot(ch2_smooth, label='CH2 MA corta', color='green')
            for i, zc in enumerate(cruces_indices):
                if zc is not None:
                    axs[1].axvline(zc, color='green', linestyle='--')
                    axs[1].plot(zc, ch2_smooth[zc], 'go', markersize=6)
                    axs[1].annotate(f"Cruce\nIdx={zc}", (zc, ch2_smooth[zc]), xytext=(0, 10),
                                    textcoords="offset points", ha='center', color='green')
            axs[1].legend(); axs[1].grid(True); axs[1].set_ylabel('CH2')

            axs[2].plot(ch3_signed, label='CH3 Original', color='purple', alpha=0.5)
            axs[2].plot(ch3_short_ma, label='CH3 MA corta', color='blue')
            axs[2].plot(ch3_long_ma, label='CH3 MA larga', color='red')
            for i, drop in enumerate(bajadas_indices):
                if drop is not None:
                    axs[2].axvline(drop, color='red', linestyle='--')
                    axs[2].plot(drop, ch3_signed[drop], 'ro', markersize=6)
                    texto = f"Bajada\nIdx={drop}\nΔ={tiempos_bajada_cruce[i]} ms\n({drop}->{cruces_indices[i]})" if tiempos_bajada_cruce[i] else f"Bajada\nIdx={drop}"
                    axs[2].annotate(texto, (drop, ch3_signed[drop]), xytext=(0, 10),
                                    textcoords="offset points", ha='center', color='red')
                    if cruces_indices[i] is not None:
                        axs[2].annotate("", xy=(cruces_indices[i], ch3_signed[drop]),
                                        xytext=(drop, ch3_signed[drop]),
                                        arrowprops=dict(arrowstyle="<->", color='black'))
            axs[2].legend(); axs[2].grid(True); axs[2].set_ylabel('CH3'); axs[2].set_xlabel('Índice de muestra')

            fig.suptitle(f'Archivo: {file}\nΔpicos(ms)={tiempo_filtrado}, Δbajada-cruce(ms)={tiempos_bajada_cruce}')
            plt.tight_layout()
            output_file = f"{os.path.splitext(file)[0]}_plot.png"
            plt.savefig(output_file)
            plt.close(fig)

            print(f"{file}: Δpicos(ms)={tiempo_filtrado}, Δbajada-cruce(ms)={tiempos_bajada_cruce}, Nº Bajadas={total_bajadas}")#, Gráfico guardado en {output_file}")
        else:
            print(f"{file}: No se encontraron columnas CH1, CH2 y CH3")
            pd.DataFrame([{'Archivo': file, 'Δpicos(ms)': None, 'Δbajada-cruce1(ms)': None, 'Δbajada-cruce2(ms)': None, 'Nº Bajadas': None}]).to_csv(results_file, mode='a', header=False, index=False)
    else:
        print(f"{file}: No existe en el directorio")
        pd.DataFrame([{'Archivo': file, 'Δpicos(ms)': None, 'Δbajada-cruce1(ms)': None, 'Δbajada-cruce2(ms)': None, 'Nº Bajadas': None}]).to_csv(results_file, mode='a', header=False, index=False)
