import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000
spi.mode = 0

print("SPI response test")

# Send FROM
message = "FROM"

print("Sending:", message)

# Send command
data = [ord(c) for c in message]
spi.xfer2(data)

# Give Arduino a moment
time.sleep(0.1)

# Clock additional bytes to read Arduino response
response = spi.xfer2([0, 0, 0, 0])

print("Response bytes:", response)

spi.close()
