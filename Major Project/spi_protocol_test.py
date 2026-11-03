import spidev

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 100000
spi.mode = 0

command = "FROM\n"

print("Sending:", repr(command))

data = [ord(c) for c in command]

response = spi.xfer2(data)

print("SPI response:", response)

spi.close()
