from machine import Pin, I2C, RTC, ADC
import ssd1306
import time
import dht
import math

# --- CLASSE BH1750 (Sensor de Luz) ---
class BH1750:
    def __init__(self, bus, addr=0x23):
        self.bus = bus
        self.addr = addr
    def luminance(self):
        try:
            self.bus.writeto(self.addr, bytes([0x10]))
            time.sleep_ms(150)
            data = self.bus.readfrom(self.addr, 2)
            return (data[0] << 8 | data[1]) / 1.2
        except: return -1

# --- CONFIGURAÇÃO DOS PINOS ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
rtc = RTC()
sensor_dht = dht.DHT22(Pin(4))
lux_sensor = BH1750(i2c)
som_sensor = ADC(Pin(34))
som_sensor.atten(ADC.ATTN_11DB)
som_sensor.width(ADC.WIDTH_12BIT)

buzzer = Pin(18, Pin.OUT)
btn_next = Pin(5, Pin.IN, Pin.PULL_UP)
btn_ok = Pin(19, Pin.IN, Pin.PULL_UP)

# --- FUNÇÕES DE DESENHO (RELÓGIO) ---
def desenhar_digito(n, x, y):
    """ Desenha números de 20x35 pixels com traços limpos """
    e = 4 # Espessura do traço
    w, h = 20, 20
    if n in [0, 2, 3, 5, 6, 7, 8, 9]: oled.fill_rect(x, y, w, e, 1)
    if n in [0, 4, 5, 6, 8, 9]: oled.fill_rect(x, y, e, h//2, 1)
    if n in [0, 1, 2, 3, 4, 7, 8, 9]: oled.fill_rect(x+w-e, y, e, h//2, 1)
    if n in [2, 3, 4, 5, 6, 8, 9]: oled.fill_rect(x, y+h//2-1, w, e, 1)
    if n in [0, 2, 6, 8]: oled.fill_rect(x, y+h//2, e, h//2, 1)
    if n in [0, 1, 3, 4, 5, 6, 7, 8, 9]: oled.fill_rect(x+w-e, y+h//2, e, h//2, 1)
    if n in [0, 2, 3, 5, 6, 8, 9]: oled.fill_rect(x, y+h-e, w, e, 1)

 

def desenhar_relogio_grande(hora_str, x_ini, y_ini):
    desenhar_digito(int(hora_str[0]), x_ini, y_ini)
    desenhar_digito(int(hora_str[1]), x_ini + 25, y_ini)
    oled.fill_rect(x_ini + 48, y_ini + 5, 3, 3, 1) # Pontos
    oled.fill_rect(x_ini + 48, y_ini + 14, 3, 3, 1)
    desenhar_digito(int(hora_str[3]), x_ini + 55, y_ini)
    desenhar_digito(int(hora_str[4]), x_ini + 80, y_ini)

# --- AUXILIARES ---
def ler_amplitude_som(janela_ms=50):
    start_time = time.ticks_ms()
    max_s, min_s = 0, 4095
    while time.ticks_diff(time.ticks_ms(), start_time) < janela_ms:
        s = som_sensor.read()
        if s < 4095:
            if s > max_s: max_s = s
            if s < min_s: min_s = s
    return max_s - min_s

def ler_clique_curto(pin):
    if pin.value() == 0:
        time.sleep(0.05)
        if pin.value() == 0:
            while pin.value() == 0: time.sleep(0.01)
            return True
    return False

# --- CONTROLE ---
estado_atual = "MONITOR"
tela_alternada = "RELOGIO"
ultimo_tempo_troca = time.ticks_ms()
alternancia_pausada = False
item_menu = 0
parte_ajuste = 0 
hora_aj, min_aj = 0, 0

while True:
    c_next = ler_clique_curto(btn_next)
    c_ok = ler_clique_curto(btn_ok)

    if estado_atual == "MONITOR":
        if c_ok: alternancia_pausada = not alternancia_pausada
        if c_next: estado_atual = "MENU"

        if not alternancia_pausada:
            if time.ticks_diff(time.ticks_ms(), ultimo_tempo_troca) > 5000:
                tela_alternada = "DADOS" if tela_alternada == "RELOGIO" else "RELOGIO"
                ultimo_tempo_troca = time.ticks_ms()

        oled.fill(0)
        if tela_alternada == "RELOGIO":
            t = rtc.datetime()
            hora_str = "{:02d}:{:02d}".format(t[4], t[5])
            desenhar_relogio_grande(hora_str, 14, 21)
            if alternancia_pausada: oled.text("P", 120, 0) # P de Pausado
        else:
            try:
                sensor_dht.measure()
                temp, umid = sensor_dht.temperature(), sensor_dht.humidity()
                lux = lux_sensor.luminance()
                amp = ler_amplitude_som(40)
                db = 20 * math.log10(max(1, amp)) + 28
                
                # Exibição dos Dados
                oled.text("Temp: {:.1f} C".format(temp), 0, 0)
                oled.text("Umid: {:.1f} %".format(umid), 0, 12)
                oled.text("Lux : {:.0f} Lx".format(lux), 0, 24)
                oled.text("Som : {:.0f} dB".format(db), 0, 36)
                
                # Barra de Som (dB)
                largura = int(max(0, min(128, (db-40)*1.6)))
                oled.fill_rect(0, 52, largura, 8, 1)
                
                if alternancia_pausada: oled.text("P", 120, 0)
            except:
                oled.text("Erro Sensores", 0, 20)
        oled.show()

    elif estado_atual == "MENU":
        oled.fill(0)
        oled.text("MENU", 45, 0)
        oled.text(" MONITOR", 10, 30)
        oled.text(" AJUSTAR HORA", 10, 45)
        oled.text(">", 0, 30 if item_menu == 0 else 45)
        oled.show()
        if c_next: item_menu = (item_menu + 1) % 2
        if c_ok:
            if item_menu == 0: estado_atual = "MONITOR"
            else:
                estado_atual = "AJUSTE"; parte_ajuste = 0
                temp_t = rtc.datetime()
                hora_aj, min_aj = temp_t[4], temp_t[5]

    elif estado_atual == "AJUSTE":
        oled.fill(0)
        oled.text("SET: " + ("HORA" if parte_ajuste == 0 else "MIN"), 5, 0)
        oled.text("{:02d}:{:02d}".format(hora_aj, min_aj), 44, 30)
        if parte_ajuste == 0: oled.hline(44, 40, 16, 1)
        else: oled.hline(68, 40, 16, 1)
        oled.show()
        if c_next:
            if parte_ajuste == 0: hora_aj = (hora_aj + 1) % 24
            else: min_aj = (min_aj + 1) % 60
        if c_ok:
            if parte_ajuste == 0: parte_ajuste = 1
            else:
                rtc.datetime((2026, 2, 3, 0, hora_aj, min_aj, 0, 0))
                estado_atual = "MONITOR"; item_menu = 0