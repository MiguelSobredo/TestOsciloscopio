import pandas as pd
import matplotlib.pyplot as plt
import glob

# Parámetros de conversión vertical
vdiv_ch1 = 0.1  # 100 mV/div = 0.1 V/div
vdiv_otros = 100  # 100 V/div
adc_range = 256   # 8 bits
ymult_ch1 = vdiv_ch1 / adc_range
ymult_otros = vdiv_otros / adc_range

# Configuración horizontal del osciloscopio
sample_rate = 2_500_000  # 2.5 MS/s
record_length = 250_000  # 250 kpts
dt = (1 / sample_rate) * 1000  # Tiempo entre muestras en milisegundos

# Buscar archivos CSV en el directorio
csv_files = glob.glob("*.csv")

for file in csv_files:
    try:
        print(f"Graficando: {file}")
        df = pd.read_csv(file)

        # Generar eje temporal en milisegundos
        time_axis = [i * dt for i in range(len(df))]

        fig, ax1 = plt.subplots(figsize=(12, 4))

        # Graficar CH2, CH3, CH4 en eje primario
        for ch in ['CH2', 'CH3', 'CH4']:
            if ch in df.columns:
                ax1.plot(time_axis, df[ch] * ymult_otros, label=ch)
        ax1.set_xlabel('Tiempo (ms)')
        ax1.set_ylabel('Voltios (CH2, CH3, CH4)')
        ax1.grid(True)

        # Graficar CH1 en eje secundario
        if 'CH1' in df.columns:
            ax2 = ax1.twinx()
            ax2.plot(time_axis, df['CH1'] * ymult_ch1, color='k', label='CH1')
            ax2.set_ylabel('Voltios (CH1)')
            ax2.legend(loc='upper right')

        # Leyenda para los otros canales
        ax1.legend(loc='upper left')
        plt.title(f'Forma de onda: {file}')
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error al procesar {file}: {e}")