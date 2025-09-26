import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt

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

# Graficar los intervalos
plt.figure(figsize=(12, 4))
plt.plot(intervalos_ms, marker='o', linestyle='-', color='blue')
plt.title("Intervalos entre capturas (s)")
plt.xlabel("Número de disparo")
plt.ylabel("Tiempo entre capturas (s)")
plt.grid(True)
plt.tight_layout()
plt.show()