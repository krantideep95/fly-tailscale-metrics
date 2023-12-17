# fly-tailscale-metrics-proxy
nginx proxy running in fly.io that forwards prometheus scrape requests to raspberrypi over tailscale

I used this to create my own CO2 monitoring setup using scd41 co2 sensor, and fly.io managed Prometheus & grafana: https://fly.io/docs/reference/metrics

## Raspberry Pi Pico setup
I used these to start monitoring CO2, temperature & humidity:
* https://shop.pimoroni.com/products/raspberry-pi-pico-w?variant=40059369652307
* https://shop.pimoroni.com/products/scd41-co2-sensor-breakout?variant=39652270833747
* https://shop.pimoroni.com/products/pico-breakout-garden-pack?variant=32369506254931

Use `pimoroni-picow-..` MicroPython build from [pimoroni repo](https://github.com/pimoroni/pimoroni-pico/releases)

This is a good tutorial for programming Raspberry Pi Pico: https://www.twilio.com/blog/programming-raspberry-pi-pico-microcontroller-micropython

`main.py` file that I used is [here](./sensor.py).
It connects to Wifi, polls for co2, temperature & humdity measurements every 5 seconds, and then make a POST request to a prometheus pushgateway running on a Raspberry Pi 4 at raspberrypi.local:9091

## Raspberry Pi 4 setup

Nothing special here.
* Uses the official OS with hostname set as: raspberrypi.local.
* Runs tailscale with Expiry disabled, SSH & Exit Node enabled.
* Runs docker and a pushgateway docker image on it:
```bash
docker pull prom/pushgateway

docker run -d -p 9091:9091 prom/pushgateway
```

## Scraping metrics off raspberry pi pushgateway from a cloud prometheus

fly.io has a managed prometheus & grafana https://fly.io/docs/reference/metrics

In your fly.toml, if you add a `[metrics]` block metrics from your app start showing up at https://fly-metrics.net/.
```toml
[metrics]
  port = 9091
  path = "/metrics"
```

To serve these `GET 0.0.0.0:9091/metrics` requests, there's tailscale client running inside the VM, and a nginx proxy which proxies requests to a [machine-names](https://tailscale.com/kb/1098/machine-names):9091 url. This is raspberrypi's url.
