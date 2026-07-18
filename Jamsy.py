from machine import Pin, SPI, I2C, Timer
import time, random, ustruct, gc

SCK=18; MOSI=23; MISO=19; CE=4; CSN=[5,17,16,15]
OLED_SDA=21; OLED_SCL=22
BTN_S=Pin(13,Pin.IN,Pin.PULL_UP); BTN_M=Pin(14,Pin.IN,Pin.PULL_UP)

class NRF:
    def __init__(self, cs):
        self.spi=SPI(2, baudrate=10000000, sck=Pin(SCK), mosi=Pin(MOSI), miso=Pin(MISO))
        self.cs=Pin(cs, Pin.OUT); self.ce=Pin(CE, Pin.OUT)
        self.cs(1); self.ce(0)
        self._w(0x00,0x0E); self._w(0x01,0x00); self._w(0x02,0x00)
        self._w(0x03,0x03); self._w(0x04,0x00); self._w(0x06,0x0F)
        self._w(0x1C,0x00); self._w(0x1D,0x00)
        self.addr=b'\xE7\xE7\xE7\xE7\xE7'
        self._w(0x10,self.addr); self._w(0x0A,self.addr); self._w(0x11,32)
        self.flush(); self.ce(1); time.sleep_ms(1); self.ce(0)
        self._w(0x00,0x0E)

    def _r(self,r,l=1):
        self.cs(0); self.spi.write(bytes([r&0x1F])); d=self.spi.read(l); self.cs(1); return d
    def _w(self,r,d):
        self.cs(0)
        if isinstance(d,int): self.spi.write(bytes([r|0x20,d]))
        else: self.spi.write(bytes([r|0x20])+d)
        self.cs(1)
    def flush(self):
        self.cs(0); self.spi.write(b'\xE1'); self.cs(1)
        self.cs(0); self.spi.write(b'\xE2'); self.cs(1)
    def ch(self,c): self._w(0x05,c&0x7F)
    def tx(self,p):
        self.cs(0); self.spi.write(b'\xA0'); self.spi.write(p); self.cs(1)
        self.ce(1); time.sleep_us(15); self.ce(0)
        if self._r(0x07)[0]&0x20: self.flush()

n1=NRF(CSN[0]); n2=NRF(CSN[1]); n3=NRF(CSN[2]); n4=NRF(CSN[3])
modos=('WIFI','BT','HYBRID'); modo=0; activo=False; tmr=Timer(0)
pkt=bytearray(32); [setattr(pkt,i,random.getrandbits(8)) for i in range(32)]
cnt=0; last_oled=0

class OLED:
    def __init__(s):
        s.i2c=I2C(0,scl=Pin(OLED_SCL),sda=Pin(OLED_SDA),freq=400000)
        s.addr=0x3C
        for c in [0xAE,0xD5,0x80,0xA8,0x3F,0xD3,0x00,0x40,0x8D,0x14,0x20,0x00,0xA1,0xC8,0xDA,0x12,0x81,0xCF,0xD9,0xF1,0xDB,0x40,0xA4,0xA6,0x2E,0xAF]:
            s.i2c.writeto(s.addr, bytes([0x00,c]))
        s.clear()
    def cmd(s,*a): s.i2c.writeto(s.addr, b'\x00'+bytes(a))
    def dat(s,d): s.i2c.writeto(s.addr, b'\x40'+d)
    def clear(s):
        for p in range(8):
            s.cmd(0xB0+p,0x00,0x10); s.dat(b'\x00'*128)
    def text(s,t,x,y):
        s.cmd(0xB0+y,0x00+(x&0x0F),0x10+((x>>4)&0x0F))
        for ch in t:
            if ch=='\n': y+=1; s.cmd(0xB0+y,0x00,0x10); continue
            s.dat(FONT.get(ch, FONT['?']))

FONT={}
for k,v in [(' ',b'\x00\x00\x00\x00\x00'),('!',b'\x00\x00\x5F\x00\x00'),('"',b'\x00\x07\x00\x07\x00'),('#',b'\x14\x7F\x14\x7F\x14'),('$',b'\x24\x2A\x7F\x2A\x12'),('%',b'\x23\x13\x08\x64\x62'),('&',b'\x36\x49\x55\x22\x50'),("'",b'\x00\x05\x03\x00\x00'),('(',b'\x00\x1C\x22\x41\x00'),(')',b'\x00\x41\x22\x1C\x00'),('*',b'\x08\x2A\x1C\x2A\x08'),('+',b'\x08\x08\x3E\x08\x08'),(',',b'\x00\x50\x30\x00\x00'),('-',b'\x08\x08\x08\x08\x08'),('.',b'\x00\x60\x60\x00\x00'),('/',b'\x20\x10\x08\x04\x02'),('0',b'\x3E\x51\x49\x45\x3E'),('1',b'\x00\x42\x7F\x40\x00'),('2',b'\x42\x61\x51\x49\x46'),('3',b'\x21\x41\x45\x4B\x31'),('4',b'\x18\x14\x12\x7F\x10'),('5',b'\x27\x45\x45\x45\x39'),('6',b'\x3C\x4A\x49\x49\x30'),('7',b'\x01\x71\x09\x05\x03'),('8',b'\x36\x49\x49\x49\x36'),('9',b'\x06\x49\x49\x29\x1E'),(':',b'\x00\x36\x36\x00\x00'),(';',b'\x00\x56\x36\x00\x00'),('<',b'\x08\x14\x22\x41\x00'),('=',b'\x14\x14\x14\x14\x14'),('>',b'\x00\x41\x22\x14\x08'),('?',b'\x02\x01\x51\x09\x06'),('@',b'\x32\x49\x79\x41\x3E'),('A',b'\x7E\x09\x09\x09\x7E'),('B',b'\x7F\x49\x49\x49\x36'),('C',b'\x3E\x41\x41\x41\x22'),('D',b'\x7F\x41\x41\x41\x3E'),('E',b'\x7F\x49\x49\x49\x41'),('F',b'\x7F\x09\x09\x09\x01'),('G',b'\x3E\x41\x49\x49\x3A'),('H',b'\x7F\x08\x08\x08\x7F'),('I',b'\x00\x41\x7F\x41\x00'),('J',b'\x20\x40\x41\x3F\x01'),('K',b'\x7F\x08\x14\x22\x41'),('L',b'\x7F\x40\x40\x40\x40'),('M',b'\x7F\x02\x0C\x02\x7F'),('N',b'\x7F\x04\x08\x10\x7F'),('O',b'\x3E\x41\x41\x41\x3E'),('P',b'\x7F\x09\x09\x09\x06'),('Q',b'\x3E\x41\x51\x21\x5E'),('R',b'\x7F\x09\x19\x29\x46'),('S',b'\x46\x49\x49\x49\x31'),('T',b'\x01\x01\x7F\x01\x01'),('U',b'\x3F\x40\x40\x40\x3F'),('V',b'\x1F\x20\x40\x20\x1F'),('W',b'\x3F\x40\x38\x40\x3F'),('X',b'\x63\x14\x08\x14\x63'),('Y',b'\x07\x08\x70\x08\x07'),('Z',b'\x61\x51\x49\x45\x43'),('[',b'\x00\x7F\x41\x41\x00'),('\\',b'\x02\x04\x08\x10\x20'),(']',b'\x00\x41\x41\x7F\x00'),('^',b'\x04\x02\x01\x02\x04'),('_',b'\x40\x40\x40\x40\x40'),('`',b'\x00\x01\x02\x04\x00'),('a',b'\x20\x54\x54\x54\x78'),('b',b'\x7F\x48\x44\x44\x38'),('c',b'\x38\x44\x44\x44\x20'),('d',b'\x38\x44\x44\x48\x7F'),('e',b'\x38\x54\x54\x54\x18'),('f',b'\x08\x7E\x09\x01\x02'),('g',b'\x18\xA4\xA4\xA4\x7C'),('h',b'\x7F\x08\x04\x04\x78'),('i',b'\x00\x44\x7D\x40\x00'),('j',b'\x20\x40\x44\x3D\x00'),('k',b'\x7F\x10\x28\x44\x00'),('l',b'\x00\x41\x7F\x40\x00'),('m',b'\x7C\x04\x18\x04\x78'),('n',b'\x7C\x08\x04\x04\x78'),('o',b'\x38\x44\x44\x44\x38'),('p',b'\xFC\x24\x24\x24\x18'),('q',b'\x18\x24\x24\x24\xFC'),('r',b'\x7C\x08\x04\x04\x08'),('s',b'\x48\x54\x54\x54\x24'),('t',b'\x04\x04\x3E\x44\x24'),('u',b'\x3C\x40\x40\x40\x3C'),('v',b'\x1C\x20\x40\x20\x1C'),('w',b'\x3C\x40\x30\x40\x3C'),('x',b'\x44\x28\x10\x28\x44'),('y',b'\x1C\xA0\xA0\xA0\x7C'),('z',b'\x44\x64\x54\x4C\x44'),('{',b'\x00\x08\x36\x41\x00'),('|',b'\x00\x00\x7F\x00\x00'),('}',b'\x00\x41\x36\x08\x00'),('~',b'\x02\x01\x02\x01\x00')]: FONT[k]=v

oled=OLED()
def render():
    oled.clear()
    oled.text('M:'+modos[modo],0,0)
    oled.text('S:'+('ON' if activo else 'OFF'),0,1)
    if activo:
        oled.text('CH:'+str(n1._r(0x05)[0])+' '+str(n2._r(0x05)[0])+' '+str(n3._r(0x05)[0])+' '+str(n4._r(0x05)[0]),0,2)
    else: oled.text('CH: --- --- --- ---',0,2)

last_b=time.ticks_ms()
def debounce(p):
    global last_b
    if time.ticks_diff(time.ticks_ms(), last_b)<300: return
    last_b=time.ticks_ms()
    return True

def toggle_s(p):
    global activo
    if not debounce(p): return
    activo=not activo
    if activo: tmr.init(period=5, mode=Timer.PERIODIC, callback=loop)
    else: tmr.deinit()
    render()
def toggle_m(p):
    global modo
    if not debounce(p): return
    modo=(modo+1)%3
    render()

BTN_S.irq(trigger=Pin.IRQ_FALLING, handler=toggle_s)
BTN_M.irq(trigger=Pin.IRQ_FALLING, handler=toggle_m)

addr_pool=[b'\xE7\xE7\xE7\xE7\xE7',b'\xC2\xC2\xC2\xC2\xC2',b'\xA3\xA3\xA3\xA3\xA3',b'\x5A\x5A\x5A\x5A\x5A']
addr_idx=0

def loop(t):
    global addr_idx
    if not activo: return
    addr_idx=(addr_idx+1)&3
    if addr_idx==0:
        a1=addr_pool[random.randint(0,3)]; a2=addr_pool[random.randint(0,3)]; a3=addr_pool[random.randint(0,3)]; a4=addr_pool[random.randint(0,3)]
        n1._w(0x10,a1); n1._w(0x0A,a1); n2._w(0x10,a2); n2._w(0x0A,a2); n3._w(0x10,a3); n3._w(0x0A,a3); n4._w(0x10,a4); n4._w(0x0A,a4)
    if modo==0:
        ch=[1,6,11,13]
    elif modo==1:
        ch=[random.randint(0,78) for _ in range(4)]
    else:
        ch=[1,6,11,13]
        for i in range(4):
            if random.randint(0,1): ch[i]=random.randint(0,78)
    n1.ch(ch[0]); n2.ch(ch[1]); n3.ch(ch[2]); n4.ch(ch[3])
    for _ in range(15):
        n1.tx(pkt); n2.tx(pkt); n3.tx(pkt); n4.tx(pkt)
    if time.ticks_diff(time.ticks_ms(), last_oled)>500:
        render()

render()
while True: time.sleep(1)
