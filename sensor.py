import breakout_scd41
from pimoroni_i2c import PimoroniI2C
from pimoroni import BREAKOUT_GARDEN_I2C_PINS
import time
import network
import urequests
import machine
import gc

ssid = "" # FIXME: wifi ssid goes here
password = "" # FIXME: wifi password

led = machine.Pin("LED", machine.Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
try:
    wlan.connect(ssid, password)
except OSError as error:
    print(f'error is {error}')


max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )


i2c = PimoroniI2C(**BREAKOUT_GARDEN_I2C_PINS)  # or PICO_EXPLORER_I2C_PINS or HEADER_I2C_PINS

breakout_scd41.init(i2c)
breakout_scd41.start()

headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
url = "http://raspberrypi.local:9091/metrics/job/sensor_metrics"

while True:
    if breakout_scd41.ready():
        gc.collect()
        led.on()
        co2, temperature, humidity = breakout_scd41.measure()
        data = "co2 " +str(co2) + "\n temperature " + str(temperature) + "\n humidity " + str(humidity) +"\n"

        led.off()
        try:
          resp = urequests.post(url, headers=headers, data=data)
          value = resp.json()
        except Exception as e: # Here it catches any error.
          if isinstance(e, OSError) and resp: # If the error is an OSError the socket has to be closed.
            resp.close()
          print(f'error is {e}')
        time.sleep(5.0)
