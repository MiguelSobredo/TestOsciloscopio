import pyvisa
import pandas as pd
import time
import datetime

rm = pyvisa.ResourceManager('@py')
scope = rm.open_resource('TCPIP::192.168.1.100::INSTR')
scope.timeout = 10000  # Aumentar timeout a 10 segundos

print(scope.query('*IDN?'))

i = 1
while True:
    print(f"\nEsperando trigger {i}...")

    # Esperar a que el estado sea SAVE (captura completada)
    while True:
        state = scope.query('TRIGger:STATE?').strip()
        if state == 'SAVE':
            print("¡Captura lista!")
            break
        time.sleep(0.2)

    # Leer datos de CH1, CH2 y CH3
    canales = ['CH1', 'CH2', 'CH3']
    datos = {}

    for ch in canales:
        try:
            scope.write(f'DATA:SOURCE {ch}')
            scope.write('DATA:ENCdg ASCii')
            scope.write('DATA:WIDTH 1')
            scope.write('DATA:START 1')
            scope.write('DATA:STOP 250000')  # Asegura que se lean todos los puntos

            raw = scope.query('CURVE?')
            print(f"{ch}: longitud de datos crudos = {len(raw)}")
            print(f"{ch}: primeros datos = {raw[:100]}")

            datos[ch] = [float(v) for v in raw.split(',') if v.strip()]
            print(f"{ch}: muestras leídas = {len(datos[ch])}")

        except Exception as e:
            print(f"Error leyendo {ch}: {e}")
            datos[ch] = []

    # Crear DataFrame y guardar CSV
    df = pd.DataFrame(datos)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'captura_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"Datos guardados en {filename} con {len(df)} filas")

    # Rearmar el osciloscopio
    scope.write('ACQUIRE:STATE OFF')
    scope.write('ACQUIRE:STOPAFTER SEQUENCE')
    scope.write('ACQUIRE:STATE RUN')

    time.sleep(1.5)
    i += 1