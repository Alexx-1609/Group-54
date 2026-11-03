import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 100000
spi.mode = 0

message = "HELLO"

for char in message:
    print("Sending:", char)

    response = spi.xfer2([ord(char), 0])

    print("Response:", response)

    time.sleep(0.1)

spi.close()
