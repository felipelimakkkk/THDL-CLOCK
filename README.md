# THDL CLOCK - Monitor Ambiental com Relógio OLED

IMPORTANTE, LEIA:
Este projeto consiste em uma estação de monitoramento de ambiente utilizando um ESP32. [cite_start]O sistema alterna entre um relógio digital e a leitura em tempo real de sensores de temperatura, umidade, luminosidade e ruído, contando com um menu para ajuste de horas[cite: 2, 3, 4, 5].

## Hardware Necessário
* [cite_start]**Microcontrolador:** ESP32 (MicroPython instalado) [cite: 7]
* [cite_start]**Display:** OLED SSD1306 (128x64) [cite: 8]
* **Sensores:**
    * [cite_start]DHT11: Temperatura e Umidade [cite: 11]
    * [cite_start]BH1750: Intensidade Luminosa [cite: 12]
    * [cite_start]Microfone Analógico (MAX4466): Leitura de intensidade sonora (ADC) [cite: 13]
* [cite_start]**Controles:** 2 Botões (Next e OK) [cite: 14]

## Pinagem (Conexões)

| Componente | GND | Pino de Dados/Sinal | VCC | Outros (Clock/SCL) |
| :--- | :--- | :--- | :--- | :--- |
| **Display OLED** | GND | SDA (D21) | 3V3 | SCL (D22) |
| **DHT11** | GND | SDA (D4) | 3V3 | - |
| **BH1750** | GND | SDA (D21) | 3V3 | SCL (D22) |
| **Sensor Som** | GND | SIG (D34) | 3V3 | - |
| **Botão NEXT** | GND | D5 | - | - |
| **Botão OK** | GND | D19 | - | - |

[cite_start]*[cite: 16]*

## Funcionalidades
1.  [cite_start]**Modo Monitor:** Alterna automaticamente a cada 5 segundos entre o relógio grande e os dados dos sensores[cite: 18].
2.  [cite_start]**Pausa de Tela:** Pressionando OK no modo monitor, a alternância para e aparece um "P" no canto da tela[cite: 19].
3.  [cite_start]**Menu:** Navegação entre "Monitorar" e "Ajustar Hora" com interface visual de seleção[cite: 20].
4.  [cite_start]**Botões:** Auxiliam na navegação, ajuste de hora, selecionar opções e pausar a tela[cite: 21].

## Como Utilizar

### Interface Principal
[cite_start]Ao ligar, o dispositivo inicia no **Modo Monitor**[cite: 43].
* [cite_start]**Alternância:** A tela troca a cada 5 segundos entre Relógio e Dados (Temp, Umidade, Lux, dB)[cite: 44, 45].
* **Botão OK (GPIO 19):** Pressione para **pausar** a tela (aparece um "P"). [cite_start]Pressione novamente para retomar[cite: 46, 47].
* [cite_start]**Botão NEXT (GPIO 5):** Pressione para entrar no **Menu de Configurações**[cite: 48].

### Ajuste de Hora (RTC)
[cite_start]No menu, use NEXT para mover a seta e OK para confirmar[cite: 51]:
1.  Selecione "AJUSTAR HORA".
2.  Um traço aparecerá sob a hora. [cite_start]Use **NEXT** para aumentar e **OK** para confirmar[cite: 54].
3.  O traço vai para os minutos. [cite_start]Use **NEXT** para aumentar e **OK** para salvar[cite: 55].

## Detalhes Técnicos e Estrutura do Código

### Estrutura
* **Inicialização:** Configura I2C para OLED e BH1750. [cite_start]Uma classe específica gerencia a conversão de bits para Lux[cite: 24, 25].
* [cite_start]**Desenho Vetorial:** Utiliza a função `desenhar_digito` para criar números grandes via coordenadas (`fill_rect`), sem depender de fontes prontas[cite: 28, 29].
* [cite_start]**Máquina de Estados:** O fluxo é controlado pela variável `estado_atual` (MONITOR, MENU, AJUSTE)[cite: 31, 32, 33, 34].
* [cite_start]**Tempo Não-Bloqueante:** Uso de `time.ticks_diff` permite ler botões centenas de vezes por segundo enquanto espera a troca de tela[cite: 40].

### Processamento de Som
A função `ler_amplitude_som` realiza uma amostragem em uma janela de 50ms para capturar picos. [cite_start]O valor é convertido para **Decibéis (dB)** usando logaritmos para maior precisão[cite: 37, 38].

## Sensores e Escalas

| Sensor | Unidade | Descrição |
| :--- | :--- | :--- |
| **DHT11** | °C / % | Mede temperatura e umidade. Não obstrua as aberturas. |
| **BH1750** | Lux | Mede intensidade da luz. |
| **MAX4466** | dB | Converte picos de pressão sonora em decibéis. |

[cite_start]*[cite: 59]*

## Autores do Projeto
* Adan Gabriel Serrão Araújo
* Anderson Gonçalves Ferreira
* Felipe Lima Cavalcante
* Gustavo Henrique Dos Santos Pereira
* Pedro Costa Da Silva

[cite_start]*[cite: 71, 72, 73, 74, 75, 76]*