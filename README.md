# THDL CLOCK - Monitor Ambiental com Relógio OLED

Este projeto consiste em uma estação de monitoramento de ambiente utilizando um ESP32. O sistema alterna entre um relógio digital e a leitura em tempo real de sensores de temperatura, umidade, luminosidade e ruído, contando com um menu para ajuste de horas.
O software usado para as simulações foi o Wokwi
## Hardware Necessário
* **Microcontrolador:** ESP32 (MicroPython instalado)
* **Display:** OLED SSD1306 (128x64)
* **Sensores:**
    * DHT11: Temperatura e Umidade
    * BH1750: Intensidade Luminosa
    * Microfone Analógico (MAX4466): Leitura de intensidade sonora (ADC)
* **Controles:** 2 Botões (Next e OK)

## Pinagem (Conexões)

| Componente | GND | Pino de Dados/Sinal | VCC | Outros (Clock/SCL) |
| :--- | :--- | :--- | :--- | :--- |
| **Display OLED** | GND | SDA (D21) | 3V3 | SCL (D22) |
| **DHT11** | GND | SDA (D4) | 3V3 | - |
| **BH1750** | GND | SDA (D21) | 3V3 | SCL (D22) |
| **Sensor Som** | GND | SIG (D34) | 3V3 | - |
| **Botão NEXT** | GND | D5 | - | - |
| **Botão OK** | GND | D19 | - | - |

## Funcionalidades
1.  **Modo Monitor:** Alterna automaticamente a cada 5 segundos entre o relógio grande e os dados dos sensores.
2.  **Pausa de Tela:** Pressionando OK no modo monitor, a alternância para e aparece um "P" no canto da tela.
3.  **Menu:** Navegação entre "Monitorar" e "Ajustar Hora" com interface visual de seleção.
4.  **Botões:** Auxiliam na navegação, ajuste de hora, selecionar opções e pausar a tela.

## Como Utilizar

### Interface Principal
Ao ligar, o dispositivo inicia no **Modo Monitor**.
* **Alternância:** A tela troca a cada 5 segundos entre Relógio e Dados (Temp, Umidade, Lux, dB).
* **Botão OK (GPIO 19):** Pressione para **pausar** a tela (aparece um "P"). Pressione novamente para retomar.
* **Botão NEXT (GPIO 5):** Pressione para entrar no **Menu de Configurações**.

### Ajuste de Hora (RTC)
No menu, use NEXT para mover a seta e OK para confirmar:
1.  Selecione "AJUSTAR HORA".
2.  Um traço aparecerá sob a hora. Use **NEXT** para aumentar e **OK** para confirmar.
3.  O traço vai para os minutos. Use **NEXT** para aumentar e **OK** para salvar.

## Detalhes Técnicos e Estrutura do Código

### Estrutura
* **Inicialização:** Configura I2C para OLED e BH1750. Uma classe específica gerencia a conversão de bits para Lux.
* **Desenho Vetorial:** Utiliza a função `desenhar_digito` para criar números grandes via coordenadas (`fill_rect`), sem depender de fontes prontas.
* **Máquina de Estados:** O fluxo é controlado pela variável `estado_atual` (MONITOR, MENU, AJUSTE).
* **Tempo Não-Bloqueante:** Uso de `time.ticks_diff` permite ler botões centenas de vezes por segundo enquanto espera a troca de tela.

### Processamento de Som
A função `ler_amplitude_som` realiza uma amostragem em uma janela de 50ms para capturar picos. O valor é convertido para **Decibéis (dB)** usando logaritmos para maior precisão.

## Sensores e Escalas

| Sensor | Unidade | Descrição |
| :--- | :--- | :--- |
| **DHT11** | °C / % | Mede temperatura e umidade. Não obstrua as aberturas. |
| **BH1750** | Lux | Mede intensidade da luz. |
| **MAX4466** | dB | Converte picos de pressão sonora em decibéis. |

## Autores do Projeto
* Adan Gabriel Serrão Araújo
* Anderson Gonçalves Ferreira
* Felipe Lima Cavalcante
* Gustavo Henrique Dos Santos Pereira
* Pedro Costa Da Silva