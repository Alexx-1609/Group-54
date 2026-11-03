import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 100000
spi.mode = 0

print("Waiting for Arduino button events...")

try:
    while True:

        response = spi.xfer2([0])

        if response:
            event = response[0]

            if event == ord('F'):
                print("FROM button")

            elif event == ord('T'):
                print("TO button")

            elif event == ord('P'):
                print("LISTENING PRESSED")

            elif event == ord('p'):
                print("LISTENING RELEASED")

            elif event == ord('R'):
                print("REVERSE button")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    spi.close()
