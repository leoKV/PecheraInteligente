# Importación de módulos necesarios
import time
import network
from umqtt.simple import MQTTClient
import machine
import onewire
import ds18x20
import math

# Configuración de parámetros MQTT
MQTT_BROKER = "192.168.13.212"  # Dirección IP del broker MQTT
MQTT_USER = ""  # Usuario para autenticación en el broker (si es necesario)
MQTT_PASSWORD = ""  # Contraseña para autenticación en el broker (si es necesario)
MQTT_CLIENT_ID = ""  # Identificador único del cliente MQTT
MQTT_PORT = 1883  # Puerto del broker MQTT

# Definición de tópicos MQTT
MQTT_TOPIC_GAS = "gas"
MQTT_TOPIC_LLUVIA = "lluvia"
MQTT_TOPIC_TEMP = "temp"

# Configuración de pines
pin_gas_analog = machine.ADC(machine.Pin(33))  # Pin para la lectura del sensor de gas (entrada analógica)
pin_buzzer = machine.Pin(16, machine.Pin.OUT)  # Pin para el control del zumbador
pin_buzzer.off()  # Apagar el zumbador inicialmente

pin_aq = 32  # Pin para la lectura del sensor de calidad del aire (entrada analógica)
aq = machine.ADC(machine.Pin(pin_aq))  # Configurar el pin como entrada analógica

pin_temp = machine.Pin(17)  # Pin para la lectura del sensor de temperatura (OneWire)
ow = onewire.OneWire(pin_temp)  # Configurar el pin como bus OneWire
temp_sensor = ds18x20.DS18X20(ow)  # Inicializar el sensor DS18X20 en el bus OneWire
roms = temp_sensor.scan()  # Escanear y obtener las direcciones de los sensores DS18X20 conectados

# Variables para mantener estados
lluvia_detectada = False  # Estado de detección de lluvia

# Función para establecer conexión WiFi
def wifi_connect():
    print("Connecting...", end="")
    sta_if = network.WLAN(network.STA_IF)  # Interfaz de estación (cliente) WiFi
    sta_if.active(True)  # Activar la interfaz WiFi
    sta_if.connect('MrNemi', '12345678')  # Conectar a la red WiFi con el nombre y contraseña
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("Wifi connection!")

# Función para publicar mensajes en un tópico MQTT
def publish(topic, value):
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=30)
    client.connect()  # Conectar al broker MQTT
    print("Value {}: {}".format(topic, value))
    client.publish(topic, str(value))  # Publicar el valor en el tópico
    client.disconnect()  # Desconectar

# Función para manejar mensajes recibidos en tópicos MQTT
def message_arrived(topic, msg):
    print("Mensaje recibido en el tópico:", topic)
    print("Contenido:", msg)

# Función para suscribirse a un tópico MQTT
def subscribe(topic):
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=0)
    client.set_callback(message_arrived)  # Configurar la función de manejo de mensajes recibidos
    client.connect()  # Conectar al broker MQTT
    client.subscribe(topic)  # Suscribirse al tópico especificado
    print("Connected on %s, topic subscribed %s" % (MQTT_BROKER, topic))
    return client

# Establecer conexión WiFi al inicio del programa
wifi_connect()

# Suscripción a los tópicos MQTT de interés
client_gas = subscribe(MQTT_TOPIC_GAS)
client_lluvia = subscribe(MQTT_TOPIC_LLUVIA)
client_temp = subscribe(MQTT_TOPIC_TEMP)

while True:
    # Detección de gas
    gas_value = pin_gas_analog.read()  # Lectura del valor analógico del sensor de gas
    if gas_value > 50:
        pin_buzzer.on()  # Encender el zumbador si se detecta gas
    else:
        pin_buzzer.off()  # Apagar el zumbador si no se detecta gas
    publish(MQTT_TOPIC_GAS, gas_value)  # Publicar el valor en el tópico correspondiente
    client_gas.check_msg()  # Verificar si hay mensajes MQTT recibidos

    # Detección de lluvia
    valor_analogico = 1500 + 1000 * math.sin(time.time() / 10)  # Generar un valor analógico simulado
    valor_maximo = 2500
    valor_minimo = 1000
    porcentaje_lluvia = max(0, min(100, (valor_analogico - valor_minimo) * 100 / (valor_maximo - valor_minimo)))  # Calcular el porcentaje de lluvia simulado
    print("Porcentaje de lluvia:", porcentaje_lluvia)
    if porcentaje_lluvia > 50:
        if not lluvia_detectada:
            print("¡Lluvia detectada!")
            lluvia_detectada = True
    else:
        print("No hay probabilidad de lluvia.")
        lluvia_detectada = False
    publish(MQTT_TOPIC_LLUVIA, porcentaje_lluvia)  # Publicar el valor en el tópico correspondiente
    client_lluvia.check_msg()  # Verificar si hay mensajes MQTT recibidos

    # Medición de temperatura
    try:
        temp_sensor.convert_temp()  # Iniciar la conversión de temperatura en el sensor
        time.sleep_ms(750)  # Esperar el tiempo necesario para la conversión
        temp_celsius = temp_sensor.read_temp(roms[0])  # Leer la temperatura convertida
        publish(MQTT_TOPIC_TEMP, temp_celsius)  # Publicar el valor en el tópico correspondiente
    except Exception as e:
        print("Error al leer la temperatura:", e)
    client_temp.check_msg()  # Verificar si hay mensajes MQTT recibidos

    time.sleep(5)  # Esperar 5 segundos antes de repetir el ciclo
