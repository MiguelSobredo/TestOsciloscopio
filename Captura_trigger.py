import pyvisa
import numpy as np
import numpy as np
import pandas as pd
import time
import datetime
 
# Configuración
IP_OSCILOSCOPIO = 'TCPIP::100.0.0.100::INSTR'
CANAL_DATOS = ['CH1', 'CH2', 'CH3','CH4']
NUM_PUNTOS = 250000
TIMEOUT = 5000
 
# Inicializar VISA
rm = pyvisa.ResourceManager('@py')
scope = None
 
def conectar_oscilo():
    global scope
    try:
        scope = rm.open_resource(IP_OSCILOSCOPIO)
        scope.timeout = TIMEOUT
        print(scope.query('*IDN?'))
        scope.write('ACQUIRE:STATE RUN')  # Asegura modo RUN continuo
    except Exception as e:
        print(f"[ERROR] Conexión fallida: {e}")
        scope = None
 
def leer_datos_binarios(canal):
    try:
        scope.write('HEADER OFF')  # Desactiva encabezados
        scope.write(f'DATA:SOURCE {canal}')
        scope.write('DATA:ENCdg RIBinary')
        scope.write('DATA:WIDTH 2')
        scope.write('DATA:START 1')
        scope.write(f'DATA:STOP {NUM_PUNTOS}')
        scope.write('CURVE?')
 
        raw = scope.read_raw()
 
        # Manejo del prefijo tipo #500000
        if raw.startswith(b'#'):
            header_len = int(raw[1:2])
            num_bytes = int(raw[2:2+header_len])
            raw = raw[2+header_len:2+header_len+num_bytes]
 
        valores = np.frombuffer(raw, dtype=np.int16)
        return valores
    except Exception as e:
        print(f"[ERROR] Lectura {canal}: {e}")
        return []
 
def guardar_csv(datos, timestamp):
    try:
        df = pd.DataFrame(datos)
        filename = f'captura_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"[INFO] Guardado: {filename} ({len(df)} filas)")
    except Exception as e:
        print(f"[ERROR] Guardando CSV: {e}")
 
# Conexión inicial
conectar_oscilo()
 
estado_anterior = None
i = 1
 
scope = None
 
def conectar_oscilo():
    global scope
    try:
        scope = rm.open_resource(IP_OSCILOSCOPIO)
        scope.timeout = TIMEOUT
        print(scope.query('*IDN?'))
        scope.write('ACQUIRE:STATE RUN')  # Asegura modo RUN continuo
    except Exception as e:
        print(f"[ERROR] Conexión fallida: {e}")
        scope = None
 
def leer_datos_binarios(canal):
    try:
        scope.write('HEADER OFF')  # Desactiva encabezados
        scope.write(f'DATA:SOURCE {canal}')
        scope.write('DATA:ENCdg RIBinary')
        scope.write('DATA:WIDTH 2')
        scope.write('DATA:START 1')
        scope.write(f'DATA:STOP {NUM_PUNTOS}')
        scope.write('CURVE?')
 
        raw = scope.read_raw()
 
        # Manejo del prefijo tipo #500000
        if raw.startswith(b'#'):
            header_len = int(raw[1:2])
            num_bytes = int(raw[2:2+header_len])
            raw = raw[2+header_len:2+header_len+num_bytes]
 
        valores = np.frombuffer(raw, dtype=np.int16)
        return valores
    except Exception as e:
        print(f"[ERROR] Lectura {canal}: {e}")
        return []
 
def guardar_csv(datos, timestamp):
    try:
        df = pd.DataFrame(datos)
        filename = f'captura_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"[INFO] Guardado: {filename} ({len(df)} filas)")
    except Exception as e:
        print(f"[ERROR] Guardando CSV: {e}")
 
# Conexión inicial
conectar_oscilo()
 
estado_anterior = None
i = 1
 
while True:
    try:
        if scope is None:
            print("[INFO] Reintentando conexión...")
            conectar_oscilo()
            time.sleep(1)
            continue
 
        estado_actual = scope.query('TRIGGER:STATE?').strip()
        print(f"[INFO] Estado trigger: {estado_actual}")
 
        # Detectar transición TRIGGER → READY (después de disparo)
        if estado_anterior == 'TRIGGER' and estado_actual == 'READY':
            print(f"\n[INFO] Captura disparada {i}...")
 
            datos = {}
            longitudes = []
 
            for ch in CANAL_DATOS:
                valores = leer_datos_binarios(ch)
                datos[ch] = valores
                longitudes.append(len(valores))
                print(f"[INFO] {ch}: {len(valores)} muestras")
 
            if len(set(longitudes)) == 1 and longitudes[0] > 0:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                guardar_csv(datos, timestamp)
            else:
                print("[WARN] Longitudes desiguales o vacías. Captura descartada.")
 
            i += 1
 
        estado_anterior = estado_actual
        time.sleep(0.1)  # Ajusta según la velocidad de cambio del trigger
 
    except Exception as e:
        print(f"[ERROR] Iteración {i}: {e}")
        time.sleep(1)
 