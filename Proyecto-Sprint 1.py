import dht
import machine
import time
from umqtt.simple import MQTTClient
import network

# Configuración de sensores
dht_pin = machine.Pin(4)  # Pin G4
dht_sensor = dht.DHT11(dht_pin)
# Pin de la fotoresistencia conectada a la ESP32
pin_fotoresistencia = machine.ADC(machine.Pin(34))
# Configuración del pin del LED
pin_led = machine.Pin(12, machine.Pin.OUT)

# Configuración de MQTT
mqtt_broker = "192.168.152.200"
mqtt_user = ""
mqtt_password = ""
mqtt_client_id = ""
mqtt_topic = "temp"
mqtt_topic2= "hum"
mqtt_topic3= "luz"
mqtt_port = 1883

# Función para obtener los datos del sensor DHT11
def read_dht11():
    dht_sensor.measure()
    temp_celsius = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temp_celsius, humidity

# Función para medir el nivel de luz
def medir_nivel_luz():
    # Lee el valor analógico de la fotoresistencia
    valor_analogico = pin_fotoresistencia.read()

    # Convierte el valor analógico en una escala de 0 a 100 (opcional)
    nivel_luz = int((valor_analogico / 4095) * 100)
    return nivel_luz

# Función para conectar a la red WiFi
def wifi_connect():
    print("Connecting...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('MrNemi', '12345678')

    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("Wifi connection!")

# Función de publicación de datos MQTT
def publish_mqtt(temp_celsius,humidity,nivel_luz):
    #mensaje = "Temperatura: {}°C, Humedad: {}%".format(temp_celsius, humidity)
    mensaje = "{}".format(temp_celsius)
    mensaje2 = "{}".format(humidity)
    mensaje3 = "{}".format(nivel_luz)
    mqtt_client = MQTTClient(mqtt_client_id, mqtt_broker, port=mqtt_port, user=mqtt_user, password=mqtt_password, keepalive=30)
    mqtt_client.connect()
    mqtt_client.publish(mqtt_topic, mensaje)
    mqtt_client.publish(mqtt_topic2, mensaje2)
    mqtt_client.publish(mqtt_topic3, mensaje3)
    mqtt_client.disconnect()
    print("Publicado en MQTT: {}".format(mensaje))
    print("Publicado en MQTT: {}".format(mensaje2))
    print("Publicado en MQTT: {}".format(mensaje3))

# Función principal
def main():
    while True:
        #DHT11
        data = read_dht11()
        temperatura = data[0]
        humedad = data[1]
        print("Temperatura: {}°C, Humedad: {}%".format(temperatura, humedad))
        time.sleep(1)  # Leer cada 1 segundo
        #NIVEL DE LUZ
        nivel_luz_actual = medir_nivel_luz()
        print("Nivel de luz:", nivel_luz_actual)
        if nivel_luz_actual < 45:
            pin_led.on()  # Enciende el LED
        else:
            pin_led.off()  # Apaga el LED
        #publish_mqtt(nivel_luz_actual)
        publish_mqtt(temperatura, humedad,nivel_luz_actual)
        time.sleep(1)
# Ejecución del programa principal
wifi_connect()
main()
