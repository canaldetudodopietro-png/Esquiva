import sys
import os
import time
import random
import struct
import threading

# --- LEITOR DE CONTROLE ROBUSTO PARA R36S ---
input_move = 0
game_running = True

def ler_controles_r36s():
    global input_move, game_running
    caminho_controle = "/dev/input/js0"
    if not os.path.exists(caminho_controle):
        caminho_controle = "/dev/input/event0"
        
    try:
        fd = open(caminho_controle, "rb")
    except Exception:
        return

    while game_running:
        try:
            dados = fd.read(8)
            if not dados:
                break
            _, valor, tipo, numero = struct.unpack("IhBB", dados)
            
            # tipo 2 = Eixo Direcional (D-Pad / Analógico esquerdo)
            if tipo == 2 and numero == 0: 
                if valor < -10000:
                    input_move = -6
                elif valor > 10000:
                    input_move = 6
                else:
                    input_move = 0
            
            # tipo 1 = Pressionar qualquer botão do console
            elif tipo == 1 and valor == 1:
                # Aceita qualquer botão a partir do índice 4 (Ombros, Select, Start, L2, R2) para fechar o jogo com segurança
                if numero >= 4: 
                    game_running = False
        except Exception:
            break
    fd.close()

# Dispara a leitura do controle físico em segundo plano
threading.Thread(target=ler_controles_r36s, daemon=True).start()

# Abre a tela física do R36S diretamente (Framebuffer 0)
try:
    fb = open("/dev/fb0", "wb")
except PermissionError:
    os.system("sudo chmod 666 /dev/fb0")
    fb = open("/dev/fb0", "wb")

LARGURA, ALTURA = 640, 480
BYTES_PER_PIXEL = 4 

COR_FUNDO = b"\x00\x00\x00\x00"     # Preto
COR_JOGADOR = b"\x00\xff\x00\x00"   # Verde
COR_INIMIGO = b"\x00\x00\xff\x00"   # Vermelho

jogador_x = LARGURA // 2
jogador_y = ALTURA - 60
jogador_tam = 40

obs_x = random.randint(0, LARGURA - 40)
obs_y = 0
obs_tam = 40
obs_vel = 8

buffer_limpo = COR_FUNDO * (LARGURA * ALTURA)

while game_running:
    frame = bytearray(buffer_limpo)
    
    jogador_x += input_move
    if jogador_x < 0:
        jogador_x = 0
    elif jogador_x > LARGURA - jogador_tam:
        jogador_x = LARGURA - jogador_tam

    for row in range(int(obs_y), int(obs_y + obs_tam)):
        if 0 <= row < ALTURA:
            inicio = (row * LARGURA + int(obs_x)) * BYTES_PER_PIXEL
            fim = inicio + (obs_tam * BYTES_PER_PIXEL)
            frame[inicio:fim] = COR_INIMIGO * obs_tam

    for row in range(jogador_y, jogador_y + jogador_tam):
        if 0 <= row < ALTURA:
            inicio = (row * LARGURA + jogador_x) * BYTES_PER_PIXEL
            fim = inicio + (jogador_tam * BYTES_PER_PIXEL)
            frame[inicio:fim] = COR_JOGADOR * jogador_tam

    fb.seek(0)
    fb.write(frame)
    fb.flush()

    obs_y += obs_vel
    if obs_y > ALTURA:
        obs_y = 0
        obs_x = random.randint(0, LARGURA - 40)
        obs_vel += 0.5 

    if (obs_y + obs_tam >= jogador_y and obs_y <= jogador_y + jogador_tam and
        obs_x + obs_tam >= jogador_x and obs_x <= jogador_x + jogador_tam):
        obs_y = 0
        obs_x = random.randint(0, LARGURA - 40)
        obs_vel = 8

    time.sleep(0.016)

fb.seek(0)
fb.write(buffer_limpo)
fb.close()
sys.exit(0)
