from machine import Pin, I2C
import ssd1306
import time
import dht

# --- CONFIGURAÇÃO DO HARDWARE ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

sensor = dht.DHT22(Pin(4))
botao = Pin(5, Pin.IN, Pin.PULL_UP)

# Variáveis de Estado
estado_atual = "MENU" # Estados: MENU, PROGRAMA, OPCOES
item_selecionado = 0  # 0 para Iniciar, 1 para Opções

# --- LIMITES DO CLIMA ---
LIMITE_SENSACAO = 37.0  # Alerta de mormaço (acima disso)
LIMITE_UMIDADE = 70.0   # Umidade para mormaço

# --- LIMITES HIDRATAÇÃO (Novos ajustes) ---
LIMITE_HIDRAT_UMID = 40.0 # Abaixo de 40%
HIDRAT_SENS_MIN = 32.0    # Acima de 32 graus
HIDRAT_SENS_MAX = 37.0    # Abaixo de 37 graus

# Controle do aviso de água
aviso_agua_ativo = False
aviso_agua_ignorado = False

def calcular_sensacao(t, h):
    c1, c2, c3 = -8.78469475556, 1.61139411, 2.33854883889
    c4, c5, c6 = -0.14611605, -0.012308094, -0.0164248277778
    c7, c8, c9 = 0.002211732, 0.00072546, -0.000003582
    hi = (c1 + (c2 * t) + (c3 * h) + (c4 * t * h) + (c5 * t**2) + 
          (c6 * h**2) + (c7 * t**2 * h) + (c8 * t * h**2) + (c9 * t**2 * h**2))
    return hi

def mostrar_menu():
    oled.fill(0)
    oled.text("--- MENU ---", 20, 5)
    oled.text("INICIAR", 30, 25)
    oled.text("OPCOES", 30, 40)
    pos_y = 25 if item_selecionado == 0 else 40
    oled.text(">", 15, pos_y)
    oled.show()

# Inicialização
oled.fill(0)
oled.text("THDL CLOCK", 20, 25)
oled.show()
time.sleep(1.5)

while True:
    # --- LÓGICA DO BOTÃO ---
    if botao.value() == 0:
        pressionado_inicio = time.ticks_ms()
        while botao.value() == 0:
            tempo = time.ticks_diff(time.ticks_ms(), pressionado_inicio)
            
            # CLIQUE LONGO (> 2s)
            if tempo > 2000: 
                if estado_atual == "MENU":
                    estado_atual = "PROGRAMA" if item_selecionado == 0 else "OPCOES"
                else:
                    estado_atual = "MENU" 
                    aviso_agua_ignorado = False 
                
                while botao.value() == 0: pass 
                break
        else: 
            # CLIQUE CURTO (< 2s)
            if estado_atual == "MENU":
                item_selecionado = 1 if item_selecionado == 0 else 0
            
            elif estado_atual == "PROGRAMA":
                # Se tiver aviso na tela, o clique limpa
                if aviso_agua_ativo:
                    aviso_agua_ignorado = True
                    oled.fill(0) 
            
            time.sleep(0.2) 

    # --- GERENCIAMENTO DE TELAS ---
    if estado_atual == "MENU":
        mostrar_menu()

    elif estado_atual == "OPCOES":
        oled.fill(0)
        oled.text("MODO OPCOES", 20, 5)
        oled.text("(Vazio por enq.)", 0, 30)
        oled.text("Segure p/ Voltar", 0, 50)
        oled.show()

    elif estado_atual == "PROGRAMA":
        try:
            sensor.measure()
            temp = sensor.temperature()
            umid = sensor.humidity()
            sensacao = calcular_sensacao(temp, umid)
            
            # 1. Checa Mormaço (Prioridade alta, acima de 37 + úmido)
            mormaco_detectado = (sensacao > LIMITE_SENSACAO and umid > LIMITE_UMIDADE)
            
            # 2. Checa Hidratação (Faixa específica: 32 < ST < 37 e Seco)
            if (umid < LIMITE_HIDRAT_UMID) or (sensacao > HIDRAT_SENS_MIN and sensacao < HIDRAT_SENS_MAX):
                aviso_agua_ativo = True
            else:
                # Se sair da faixa de perigo, reseta o estado para poder avisar de novo depois
                aviso_agua_ativo = False
                aviso_agua_ignorado = False
            
            oled.fill(0)

            # --- DECISÃO DO DISPLAY ---
            # Mostra aviso de água se ativo e NÃO ignorado pelo usuário
            if aviso_agua_ativo and not aviso_agua_ignorado:
                oled.text("!!! ATENCAO !!!", 5, 0)
                oled.text("BEBER AGUA", 25, 25)
                oled.text("Seco ou Quente!", 10, 45)
            else:
                # Tela padrão de monitoramento
                if mormaco_detectado:
                    oled.text("!CLIMA EXTREMO!", 5, 0)
                else:
                    oled.text("THDL - Belem", 15, 0)
                
                oled.text("T: {:.1f} C".format(temp), 0, 20)
                oled.text("U: {:.1f} %".format(umid), 0, 35)
                oled.text("ST: {:.1f} C".format(sensacao), 0, 50)
            
            oled.show()
            
        except OSError:
            oled.fill(0)
            oled.text("Erro no Sensor", 0, 20)
            oled.show()

    time.sleep(0.1)