# ssd1306.py

from micropython import const
import framebuf

# Register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

class SSD1306:
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.external_vcc = external_vcc
        self.buffer = bytearray(self.height * self.width // 8)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        self.write_cmd(SET_DISP | 0x00)  # display off
        self.write_cmd(SET_MEM_ADDR)
        self.write_cmd(0x00)  # horizontal addressing mode
        self.write_cmd(SET_DISP_START_LINE | 0x00)
        self.write_cmd(SET_SEG_REMAP | 0x01)  # column addr 127 mapped to SEG0
        self.write_cmd(SET_MUX_RATIO)
        self.write_cmd(self.height - 1)
        self.write_cmd(SET_COM_OUT_DIR | 0x08)  # scan from COM[N] to COM0
        self.write_cmd(SET_DISP_OFFSET)
        self.write_cmd(0x00)
        self.write_cmd(SET_COM_PIN_CFG)
        if self.height == 32:
            self.write_cmd(0x02)
        elif self.height == 64:
            self.write_cmd(0x12)
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(0x7F)
        self.write_cmd(SET_PRECHARGE)
        self.write_cmd(0x22 if self.external_vcc else 0xF1)
        self.write_cmd(SET_VCOM_DESEL)
        self.write_cmd(0x30)  # 0.83*Vcc
        self.write_cmd(SET_CHARGE_PUMP)
        self.write_cmd(0x10 if self.external_vcc else 0x14)
        self.write_cmd(SET_DISP | 0x01)  # display on

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, b'\x00' + bytearray([cmd]))

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.width - 1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.height // 8 - 1)
        self.i2c.writeto(self.addr, b'\x40' + self.buffer)

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)
