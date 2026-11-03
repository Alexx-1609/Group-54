from smbus2 import SMBus
from PIL import Image, ImageDraw, ImageFont
import time

OLED_ADDR = 0x3C
WIDTH = 128
HEIGHT = 64

bus = SMBus(1)

def oled_command(cmd):
    bus.write_i2c_block_data(OLED_ADDR, 0x00, [cmd])

def oled_data(data):
    for i in range(0, len(data), 32):
        bus.write_i2c_block_data(OLED_ADDR, 0x40, data[i:i+32])

# Initialize SSD1306
commands = [
    0xAE, 0xD5, 0x80, 0xA8, 0x3F,
    0xD3, 0x00, 0x40, 0x8D, 0x14,
    0x20, 0x00, 0xA1, 0xC8, 0xDA,
    0x12, 0x81, 0xCF, 0xD9, 0xF1,
    0xDB, 0x40, 0xA4, 0xA6, 0xAF
]

for cmd in commands:
    oled_command(cmd)

# Create image
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

draw.text((5, 10), "SPI PROTOTYPE", fill=1)
draw.text((5, 30), "HELLO!", fill=1)

# Convert image to SSD1306 page format
buffer = []

for page in range(8):
    for x in range(WIDTH):
        byte = 0
        for bit in range(8):
            y = page * 8 + bit
            if image.getpixel((x, y)):
                byte |= (1 << bit)
        buffer.append(byte)

# Display
for page in range(8):
    oled_command(0xB0 + page)
    oled_command(0x00)
    oled_command(0x10)
    oled_data(buffer[page * 128:(page + 1) * 128])

time.sleep(10)
bus.close()
