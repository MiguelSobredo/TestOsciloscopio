import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd  # Añadido para manejar CSV

# Buscar todos los archivos CSV con el patrón de nombre
csv_files = glob.glob("captura_*.csv")

# Extraer timestamps desde los nombres de archivo
timestamps = []
for file in csv_files:
    try:
        base = os.path.basename(file)
        ts_str = base.replace("captura_", "").replace(".csv", "")
        ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
        timestamps.append(ts)
    except Exception as e:
        print(f"Error al procesar {file}: {e}")

# Ordenar cronológicamente
timestamps.sort()

# Calcular diferencias entre capturas en segundos
intervalos_ms = []
for i in range(1, len(timestamps)):
    delta = (timestamps[i] - timestamps[i - 1]).total_seconds() 
    intervalos_ms.append(delta)

# Preparar datos para CSV: incluir timestamps y intervalos
datos = {
    'Timestamp': [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps],
    'Intervalo_previo_s': [None] + intervalos_ms  # El primero no tiene intervalo previo
}
df = pd.DataFrame(datos)

# Guardar en CSV
df.to_csv('intervalos_capturas.csv', index=False)
print("Datos guardados en 'intervalos_capturas.csv'")

# Graficar los intervalos (solo los que existen)
if intervalos_ms:
    plt.figure(figsize=(12, 4))
    plt.plot(range(1, len(intervalos_ms) + 1), intervalos_ms, marker='o', linestyle='-', color='blue')
    plt.title("Intervalos entre capturas (s)")
    plt.xlabel("Número de disparo")
    plt.ylabel("Tiempo entre capturas (s)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()