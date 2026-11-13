import pygame
import math
import random

pygame.init()

# --- Configurações do tabuleiro ---
TAMANHO_CASA = 50              # cada casa tem 50x50 pixels
COLUNAS = 16                   # 16 casas de largura -> 800 px
LINHAS = 12                    # 12 casas de altura  -> 600 px
LARGURA = COLUNAS * TAMANHO_CASA
ALTURA = LINHAS * TAMANHO_CASA

# --- Configurações do pulo ---
DURACAO_PULO = 0.12            # quanto tempo (segundos) leva um pulo de uma casa
ALTURA_PULO = 18               # quantos pixels o personagem sobe no meio do pulo

# --- Cores (R, G, B) ---
VERDE_MESA = (20, 110, 60)
VERDE_MESA_ESCURO = (15, 90, 50)
SOMBRA = (10, 60, 30)
CARPETE = (120, 25, 40)
CARPETE_ESCURO = (100, 20, 35)
SOMBRA_CARPETE = (70, 10, 20)
PRETO_TERNO = (25, 25, 30)
BRANCO = (240, 240, 240)
PELE = (225, 180, 140)
PRATA = (190, 190, 200)
DOURADO_BEBIDA = (240, 200, 80)

# --- Mapa da fase: o tipo de cada linha (linha 0 = topo da tela) ---
# "seguro"  -> feltro verde, ninguém passa
# "garcons" -> carpete vermelho, com garçons andando
MAPA = [
    "seguro",    # 0  (chegada)
    "garcons",   # 1
    "garcons",   # 2
    "seguro",    # 3
    "garcons",   # 4
    "garcons",   # 5
    "garcons",   # 6
    "seguro",    # 7
    "garcons",   # 8
    "garcons",   # 9
    "seguro",    # 10
    "seguro",    # 11 (início)
]

# --- Garçons ---
LARGURA_GARCOM = 40

# --- Skin: separada do resto, para trocar fácil no futuro ---
skin_atual = (230, 190, 60)    # por enquanto é só uma cor (dourado)

janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cassino Crossing")
relogio = pygame.time.Clock()

# --- Jogador ---
# Posição LÓGICA: em qual casa ele está (é o que vale para o jogo)
jogador_coluna = COLUNAS // 2
jogador_linha = LINHAS - 1

# Posição VISUAL: onde ele está sendo desenhado, em pixels (é o que anima)
jogador_x = jogador_coluna * TAMANHO_CASA
jogador_y = jogador_linha * TAMANHO_CASA

# Controle do pulo
pulando = False
tempo_pulo = 0
origem_x, origem_y = jogador_x, jogador_y
destino_x, destino_y = jogador_x, jogador_y

# --- Cria os garçons ---
# Cada garçom é um dicionário: em que linha anda, posição x (pixels) e velocidade
garcons = []
for linha in range(LINHAS):
    if MAPA[linha] != "garcons":
        continue                       # pula as linhas que não são de garçom

    velocidade = random.randint(90, 180)
    if linha % 2 == 0:
        velocidade = -velocidade       # linhas pares andam para a esquerda

    quantidade = random.choice([2, 3])
    espaco = (LARGURA + LARGURA_GARCOM) / quantidade
    for i in range(quantidade):
        garcons.append({
            "linha": linha,
            "x": i * espaco + random.uniform(0, espaco - 2 * TAMANHO_CASA),
            "velocidade": velocidade,
        })


def desenhar_tabuleiro():
    for linha in range(LINHAS):
        if MAPA[linha] == "garcons":
            cor = CARPETE if linha % 2 == 0 else CARPETE_ESCURO
        else:
            cor = VERDE_MESA if linha % 2 == 0 else VERDE_MESA_ESCURO
        pygame.draw.rect(janela, cor, (0, linha * TAMANHO_CASA, LARGURA, TAMANHO_CASA))


def desenhar_jogador(x, y, altura_no_ar, esticar):
    # Sombra: fica sempre no chão e diminui quando o personagem sobe
    tamanho_sombra = 34 - altura_no_ar * 0.6
    pygame.draw.ellipse(
        janela, SOMBRA,
        (x + (TAMANHO_CASA - tamanho_sombra) / 2, y + TAMANHO_CASA - 14, tamanho_sombra, 10),
    )

    # Corpo: no ar fica mais alto e mais fino (efeito "elástico")
    largura_corpo = 36 - esticar
    altura_corpo = 36 + esticar
    corpo_x = x + (TAMANHO_CASA - largura_corpo) / 2
    corpo_y = y + TAMANHO_CASA - 8 - altura_corpo - altura_no_ar
    pygame.draw.rect(janela, skin_atual, (corpo_x, corpo_y, largura_corpo, altura_corpo), border_radius=6)


def desenhar_garcom(garcom):
    x = garcom["x"]
    y = garcom["linha"] * TAMANHO_CASA

    # Sombra no chão
    pygame.draw.ellipse(janela, SOMBRA_CARPETE, (x + 2, y + TAMANHO_CASA - 14, LARGURA_GARCOM - 4, 10))
    # Terno
    pygame.draw.rect(janela, PRETO_TERNO, (x + 8, y + 12, 24, 30), border_radius=5)
    # Camisa
    pygame.draw.rect(janela, BRANCO, (x + 16, y + 14, 8, 16))
    # Cabeça
    pygame.draw.circle(janela, PELE, (x + 20, y + 6), 8)

    # Bandeja com um copo, sempre na frente (no sentido em que ele anda)
    if garcom["velocidade"] > 0:
        bandeja_x = x + 28
    else:
        bandeja_x = x - 8
    pygame.draw.rect(janela, DOURADO_BEBIDA, (bandeja_x + 7, y + 8, 6, 9))
    pygame.draw.ellipse(janela, PRATA, (bandeja_x, y + 16, 20, 6))


rodando = True
while rodando:
    dt = relogio.tick(60) / 1000   # segundos desde o último quadro

    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        # Só aceita um novo movimento quando o pulo anterior terminou
        if evento.type == pygame.KEYDOWN and not pulando:
            nova_coluna = jogador_coluna
            nova_linha = jogador_linha

            if evento.key in (pygame.K_UP, pygame.K_w):
                nova_linha -= 1        # frente
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                nova_linha += 1        # trás
            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                nova_coluna -= 1       # esquerda
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                nova_coluna += 1       # direita

            # Não deixa sair do tabuleiro
            nova_coluna = max(0, min(nova_coluna, COLUNAS - 1))
            nova_linha = max(0, min(nova_linha, LINHAS - 1))

            # Se a casa mudou, começa um pulo
            if (nova_coluna, nova_linha) != (jogador_coluna, jogador_linha):
                jogador_coluna = nova_coluna
                jogador_linha = nova_linha
                origem_x, origem_y = jogador_x, jogador_y
                destino_x = jogador_coluna * TAMANHO_CASA
                destino_y = jogador_linha * TAMANHO_CASA
                tempo_pulo = 0
                pulando = True

    # --- Atualização do pulo ---
    altura_no_ar = 0
    esticar = 0
    if pulando:
        tempo_pulo += dt
        progresso = min(tempo_pulo / DURACAO_PULO, 1)   # vai de 0 (início) a 1 (fim)

        # Anda da casa de origem até a de destino
        jogador_x = origem_x + (destino_x - origem_x) * progresso
        jogador_y = origem_y + (destino_y - origem_y) * progresso

        # Sobe e desce em arco: sin vai de 0 -> 1 -> 0
        arco = math.sin(progresso * math.pi)
        altura_no_ar = arco * ALTURA_PULO
        esticar = arco * 6

        if progresso >= 1:
            pulando = False

    # --- Movimento dos garçons ---
    for garcom in garcons:
        garcom["x"] += garcom["velocidade"] * dt

        # Saiu por um lado? Volta pelo outro
        if garcom["velocidade"] > 0 and garcom["x"] > LARGURA:
            garcom["x"] = -LARGURA_GARCOM
        elif garcom["velocidade"] < 0 and garcom["x"] < -LARGURA_GARCOM:
            garcom["x"] = LARGURA

    # --- Desenho ---
    desenhar_tabuleiro()
    for garcom in garcons:
        desenhar_garcom(garcom)
    desenhar_jogador(jogador_x, jogador_y, altura_no_ar, esticar)
    pygame.display.update()

pygame.quit()