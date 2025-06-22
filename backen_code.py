from machine import Pin, SPI
import micropython

spi = SPI(
    0,
    baudrate = 25_000_000,
    polarity = 0,
    phase = 0,
    bits = 8,
    firstbit = SPI.MSB,
    sck = Pin(2),
    mosi = Pin(3),
    miso = Pin(4),
)
cs = Pin(5, Pin.OUT, value = 1)

NUM_DEVICES = 16 


@micropython.native
def _pack_10bit_words(words):
    bitbuf = 0
    bitcnt = 0
    out = bytearray()

    for w in words:
        bitbuf = (bitbuf << 10) | (w & 0x3FF)
        bitcnt += 10
        while bitcnt >= 8:
            bitcnt -= 8
            out.append((bitbuf >> bitcnt) & 0xFF)

    return out

# make ane batch (addr is 0 to 3, values list of values from #16 ... #1)
def make_frame(addr, values):
    if isinstance(values, int):
        values = [values] * NUM_DEVICES
    elif len(values) != NUM_DEVICES:
        raise ValueError("Need 16 wiper values")

    words = []
    for v in values: # MSB first, far device first
        words.append((addr << 8) | (v & 0xFF))
        
    return _pack_10bit_words(words)


def spi_xfer(frame):
    cs(0)
    spi.write(frame)
    cs(1)

def set_all_channels_high():
    for addr in (0b00, 0b01, 0b10, 0b11): 
        frame = make_frame(addr, 0xFF)      
        print_bits(frame, True) 
        spi_xfer(frame)
        
def set_all_channels_mid():
    for addr in (0b00, 0b01, 0b10, 0b11):
        frame = make_frame(addr, 0x80)
        print_bits(frame, True) 
        spi_xfer(frame)
        
def set_all_channels_low():
    for addr in (0b00, 0b01, 0b10, 0b11):
        frame = make_frame(addr, 0x00)
        print_bits(frame, True) 
        spi_xfer(frame)

# debug
def print_bits(buf, per_device=False):
    bits = ''.join('{:08b}'.format(b) for b in buf)

    if not per_device:
        print(bits)
        return
    print("Device : A1A0 D7-D0")
    for n in range(NUM_DEVICES):
        word = bits[n*10:(n+1)*10]
        print(f"D{NUM_DEVICES-n:02}    : {word[:2]} {word[2:]}")

# 3) blink fast from low to high
frame_lo = make_frame(addr=0b11, values=0)
frame_hi = make_frame(addr=0b11, values=255)


set_all_channels_high()
#set_all_channels_mid()
#set_all_channels_low()

@micropython.native
def blink_forever():
    while True:
        spi_xfer(frame_lo)
        spi_xfer(frame_hi)

#blink_forever()       #  to run, uncomment
