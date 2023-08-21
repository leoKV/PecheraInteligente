import time
import network
from umqtt.simple import MQTTClient
import machine
import onewire
import ds18x20
import math

# Configuración de MQTT
MQTT_BROKER = "192.168.13.212"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_PORT = 1883

MQTT_TOPIC_GAS = "gas"
MQTT_TOPIC_LLUVIA = "lluvia"
MQTT_TOPIC_TEMP = "temp"

# Configuración de pines
pin_gas_analog = machine.ADC(machine.Pin(33))
pin_buzzer = machine.Pin(16, machine.Pin.OUT)
pin_buzzer.off()

pin_aq = 32
aq = machine.ADC(machine.Pin(pin_aq))

pin_temp = machine.Pin(17)
ow = onewire.OneWire(pin_temp)
temp_sensor = ds18x20.DS18X20(ow)
roms = temp_sensor.scan()

# Variables para mantener estados
lluvia_detectada = False

def wifi_connect():
    print("Connecting...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('MrNemi', '12345678')
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("Wifi connection!")

def publish(topic, value):
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=30)
    client.connect()
    print("Valor {}: {}".format(topic, value))
    client.publish(topic, str(value))
    client.disconnect()

def message_arrived(topic, msg):
    print("Mensaje recibido en el tema:", topic)
    print("Contenido:", msg)

def subscribe(topic):
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=0)
    client.set_callback(message_arrived)
    client.connect()
    client.subscribe(topic)
    print("Connected on %s, topic subscribed %s" % (MQTT_BROKER, topic))
    return client

wifi_connect()
client_gas = subscribe(MQTT_TOPIC_GAS)
client_lluvia = subscribe(MQTT_TOPIC_LLUVIA)
client_temp = subscribe(MQTT_TOPIC_TEMP)

while True:
    # Detección de gas
    gas_value = pin_gas_analog.read()
    if gas_value > 50:
        pin_buzzer.on()
    else:
        pin_buzzer.off()
    publish(MQTT_TOPIC_GAS, gas_value)
    client_gas.check_msg()

    # Detección de lluvia
    valor_analogico = 1500 + 1000 * math.sin(time.time() / 10)
    valor_maximo = 2500
    valor_minimo = 1000
    porcentaje_lluvia = max(0, min(100, (valor_analogico - valor_minimo) * 100 / (valor_maximo - valor_minimo)))
    print("Porcentaje de lluvia:", porcentaje_lluvia)
    if porcentaje_lluvia > 50:
        if not lluvia_detectada:
            print("¡Lluvia detectada!")
            lluvia_detectada = True
    else:
        print("No hay probabilidad de lluvia.")
        lluvia_detectada = False
    publish(MQTT_TOPIC_LLUVIA, porcentaje_lluvia)
    client_lluvia.check_msg()

    # Medición de temperatura
    try:
        temp_sensor.convert_temp()
        time.sleep_ms(750)
        temp_celsius = temp_sensor.read_temp(roms[0])
        publish(MQTT_TOPIC_TEMP, temp_celsius)
    except Exception as e:
        print("Error al leer la temperatura:", e)
    client_temp.check_msg()

    time.sleep(5)
