from micropython import const
import framebuf

CONTRAST_LEVEL = const(0x81)
DISPLAY_ALL_ON = const(0xA4)
NORMAL_DISPLAY = const(0xA6)
DISPLAY_POWER = const(0xAE)
ADDRESSING_MODE = const(0x20)
COLUMN_ADDRESS = const(0x21)
PAGE_ADDRESS = const(0x22)
START_LINE = const(0x40)
REMAP_COLUMNS = const(0xA0)
MUX_RATIO = const(0xA8)
SCAN_DIRECTION = const(0xC0)
DISPLAY_OFFSET = const(0xD3)
PIN_CONFIGURATION = const(0xDA)
CLK_DIV_RATIO = const(0xD5)
PRECHARGE_PERIOD = const(0xD9)
VCOMH_DESELECT = const(0xDB)
CHARGE_PUMP = const(0x8D)

class OLEDDisplay:
    def __init__(self, width, height, i2c_bus, address=0x3C, external_power=False):
        self.width = width
        self.height = height
        self.i2c = i2c_bus
        self.address = address
        self.external_power = external_power
        self.buffer = bytearray(self.height * self.width // 8)
        self.framebuffer = framebuf.FrameBuffer(
            self.buffer, self.width, self.height, framebuf.MONO_VLSB
        )
        self.initialize()

    def initialize(self):
        self.send_command(DISPLAY_POWER | 0x00)
        self.send_command(ADDRESSING_MODE)
        self.send_command(0x00)
        self.send_command(START_LINE | 0x00)
        self.send_command(REMAP_COLUMNS | 0x01)
        self.send_command(MUX_RATIO)
        self.send_command(self.height - 1)
        self.send_command(SCAN_DIRECTION | 0x08)
        self.send_command(DISPLAY_OFFSET)
        self.send_command(0x00)
        self.send_command(PIN_CONFIGURATION)
        self.send_command(0x02 if self.height == 32 else 0x12)
        self.send_command(CONTRAST_LEVEL)
        self.send_command(0x7F)
        self.send_command(PRECHARGE_PERIOD)
        self.send_command(0x22 if self.external_power else 0xF1)
        self.send_command(VCOMH_DESELECT)
        self.send_command(0x30)
        self.send_command(CHARGE_PUMP)
        self.send_command(0x10 if self.external_power else 0x14)
        self.send_command(DISPLAY_POWER | 0x01)

    def send_command(self, cmd):
        self.i2c.writeto(self.address, b'\x00' + bytearray([cmd]))

    def turn_off(self):
        self.send_command(DISPLAY_POWER | 0x00)

    def turn_on(self):
        self.send_command(DISPLAY_POWER | 0x01)

    def adjust_contrast(self, level):
        self.send_command(CONTRAST_LEVEL)
        self.send_command(level)

    def invert_display(self, invert):
        self.send_command(NORMAL_DISPLAY | (invert & 1))

    def update_display(self):
        self.send_command(COLUMN_ADDRESS)
        self.send_command(0)
        self.send_command(self.width - 1)
        self.send_command(PAGE_ADDRESS)
        self.send_command(0)
        self.send_command(self.height // 8 - 1)
        self.i2c.writeto(self.address, b'\x40' + self.buffer)

    def clear(self, color):
        self.framebuffer.fill(color)

    def draw_pixel(self, x, y, color):
        self.framebuffer.pixel(x, y, color)

    def scroll_display(self, dx, dy):
        self.framebuffer.scroll(dx, dy)

    def write_text(self, text, x, y, color=1, line_height=8):
        max_chars_per_line = self.width // 8
        lines = [text[i:i+max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]
        
        for i, line in enumerate(lines):
            line_y = y + i * line_height
            if line_y + line_height > self.height:
                break
            self.framebuffer.text(line, x, line_y, color)
        self.update_display()