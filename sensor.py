import breakout_scd41
from pimoroni_i2c import PimoroniI2C
from pimoroni import BREAKOUT_GARDEN_I2C_PINS
import time
import network
import urequests
import machine
import gc

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0 and not wlan.isconnected():
        time.sleep(1)
        max_wait -= 1

    if not wlan.isconnected():
        raise RuntimeError('Failed to connect to WiFi')
    else:
        print('Connected to WiFi')
        return wlan.ifconfig()[0]

def read_sensor_data():
    if breakout_scd41.ready():
        return breakout_scd41.measure()
    return None, None, None

def post_data(url, headers, data):
    try:
        resp = urequests.post(url, headers=headers, data=data)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if resp:
            resp.close()

# FIXME: Replace with your actual SSID and Password
ssid = "your_wifi_ssid"
password = "your_wifi_password"

led = machine.Pin("LED", machine.Pin.OUT)
i2c = PimoroniI2C(**BREAKOUT_GARDEN_I2C_PINS)
breakout_scd41.init(i2c)
breakout_scd41.start()

headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
url = "http://raspberrypi.local:9091/metrics/job/sensor_metrics"

while True:
    led.on()  # Turn on the LED to indicate data reading
    co2, temperature, humidity = read_sensor_data()
    if co2 is not None:
        data = f"co2 {co2}\n temperature {temperature}\n humidity {humidity}\n"
        post_data(url, headers, data)
    led.off()  # Turn off the LED after data posting
    time.sleep(5.0)
