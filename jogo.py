import pygame
import math
import random

pygame.init()

# --- Configurações da tela ---
TAMANHO_CASA = 50              # cada casa tem 50x50 pixels
COLUNAS = 16                   # 16 casas de largura -> 800 px
LINHAS_NA_TELA = 12            # cabem 12 linhas na tela -> 600 px
LARGURA = COLUNAS * TAMANHO_CASA
ALTURA = LINHAS_NA_TELA * TAMANHO_CASA

# --- Configurações do pulo ---
DURACAO_PULO = 0.12            # quanto tempo (segundos) leva um pulo de uma casa
ALTURA_PULO = 18               # quantos pixels o personagem sobe no meio do pulo

# --- Configurações do mundo infinito ---
CHANCE_FAIXA_SEGURA = 0.25     # chance de uma faixa de feltro aparecer entre os garçons
MAX_GARCONS_SEGUIDOS = 5       # nunca mais que 5 faixas de garçom sem descanso
DISTANCIA_DIFICIL = 150        # a partir desses pontos o jogo está no máximo da dificuldade

# Mude para True para ver as caixas de colisão
MOSTRAR_HITBOX = False

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
FUNDO_LOJA = (30, 15, 25)
PAINEL = (55, 30, 45)
DOURADO = (230, 190, 60)
CINZA = (150, 140, 150)
VERMELHO = (220, 50, 60)

# --- Garçons ---
LARGURA_GARCOM = 40

# --- Skin: separada do resto, para trocar fácil no futuro ---
skin_atual = (230, 190, 60)    # por enquanto é só uma cor (dourado)

janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cassino Crossing")
relogio = pygame.time.Clock()

# Fontes para escrever na tela (None = fonte padrão do pygame)
fonte_enorme = pygame.font.Font(None, 110)
fonte_grande = pygame.font.Font(None, 72)
fonte_media = pygame.font.Font(None, 44)
fonte_pequena = pygame.font.Font(None, 32)

# As telas do jogo -> "loja", "jogando" ou "game_over"
estado = "loja"
motivo_derrota = ""            # por que perdeu (aparece no game over)

# Carteira do jogador (as moedas vêm num próximo passo)
moedas = 0

# Pontuação: quantas linhas o jogador avançou
pontos = 0
recorde = 0

# --- O mundo ---
# Agora o mundo não tem fim. As linhas são numeradas a partir do início (linha 0)
# e, igual ao "y" do pygame, IR PARA CIMA DIMINUI o número: -1, -2, -3...
faixas = {}        # dicionário: número da linha -> tipo ("seguro" ou "garcons")
garcons = []       # todos os garçons que existem agora

# Câmera: a posição (em pixels do mundo) do topo da tela
camera_y = 0

# --- Jogador ---
jogador_coluna = COLUNAS // 2
jogador_linha = 0
jogador_x = jogador_coluna * TAMANHO_CASA
jogador_y = jogador_linha * TAMANHO_CASA

# Controle do pulo
pulando = False
tempo_pulo = 0
origem_x, origem_y = jogador_x, jogador_y
destino_x, destino_y = jogador_x, jogador_y


# Dificuldade de 0 (começo) até 1 (máximo), de acordo com os pontos
def dificuldade():
    return min(pontos / DISTANCIA_DIFICIL, 1)


# Cria os garçons de UMA faixa
def criar_garcons_da_faixa(linha):
    d = dificuldade()

    # Quanto mais longe, mais rápidos (e o sentido é sorteado)
    velocidade = random.randint(80, 150) + int(100 * d)
    if random.random() < 0.5:
        velocidade = -velocidade

    # Quanto mais longe, mais garçons por faixa
    if d < 0.3:
        quantidade = random.choice([1, 2, 2])
    elif d < 0.7:
        quantidade = random.choice([2, 2, 3])
    else:
        quantidade = random.choice([2, 3, 3])

    espaco = (LARGURA + LARGURA_GARCOM) / quantidade
    for i in range(quantidade):
        garcons.append({
            "linha": linha,
            "x": i * espaco + random.uniform(0, espaco - 2 * TAMANHO_CASA),
            "velocidade": velocidade,
        })


# Quantas faixas de garçom seguidas existem logo abaixo desta linha?
def garcons_seguidos_abaixo(linha):
    contagem = 0
    while faixas.get(linha + 1 + contagem) == "garcons":
        contagem += 1
    return contagem


# Sorteia o tipo de uma linha nova e cria o que tiver nela
def criar_faixa(linha):
    if linha >= -1:
        tipo = "seguro"                            # área de início: sempre segura
    elif faixas[linha + 1] == "seguro":
        tipo = "garcons"                           # depois de descanso vem perigo
    elif garcons_seguidos_abaixo(linha) >= MAX_GARCONS_SEGUIDOS:
        tipo = "seguro"                            # já teve garçom demais seguido
    elif random.random() < CHANCE_FAIXA_SEGURA:
        tipo = "seguro"
    else:
        tipo = "garcons"

    faixas[linha] = tipo
    if tipo == "garcons":
        criar_garcons_da_faixa(linha)


# Cria linhas novas até chegar na linha "linha_topo"
def gerar_faixas_ate(linha_topo):
    linha = min(faixas) - 1        # a linha logo acima da mais alta que já existe
    while linha >= linha_topo:
        criar_faixa(linha)
        linha -= 1


# Primeira e última linha que aparecem na tela agora
def linha_do_topo_da_tela():
    return math.floor(camera_y / TAMANHO_CASA)


def linha_da_base_da_tela():
    return math.floor((camera_y + ALTURA) / TAMANHO_CASA) - 1


# Caixas de colisão (hitbox) -> em coordenadas do MUNDO
def hitbox_jogador():
    return pygame.Rect(jogador_x + 12, jogador_y + 12, 26, 30)


def hitbox_garcom(garcom):
    return pygame.Rect(garcom["x"] + 8, garcom["linha"] * TAMANHO_CASA + 12, 24, 30)


def desenhar_tabuleiro():
    for linha in range(linha_do_topo_da_tela(), linha_da_base_da_tela() + 2):
        if faixas.get(linha) == "garcons":
            cor = CARPETE if linha % 2 == 0 else CARPETE_ESCURO
        else:
            cor = VERDE_MESA if linha % 2 == 0 else VERDE_MESA_ESCURO
        y_na_tela = linha * TAMANHO_CASA - camera_y
        pygame.draw.rect(janela, cor, (0, y_na_tela, LARGURA, TAMANHO_CASA))


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
    y = garcom["linha"] * TAMANHO_CASA - camera_y     # mundo -> tela

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


# Escreve um texto centralizado na posição (x, y)
def escrever(texto, fonte, cor, x, y):
    imagem = fonte.render(texto, True, cor)
    janela.blit(imagem, imagem.get_rect(center=(x, y)))


# Desenha o jogo inteiro (chão, garçons, jogador, pontos)
def desenhar_jogo(altura_no_ar, esticar):
    desenhar_tabuleiro()
    for garcom in garcons:
        desenhar_garcom(garcom)

    jogador_y_na_tela = jogador_y - camera_y          # mundo -> tela
    if estado == "game_over":
        # Achatado! (esticar negativo deixa o corpo largo e baixinho)
        desenhar_jogador(jogador_x, jogador_y_na_tela, 0, -16)
    else:
        desenhar_jogador(jogador_x, jogador_y_na_tela, altura_no_ar, esticar)

    if MOSTRAR_HITBOX:
        pygame.draw.rect(janela, (0, 255, 255), hitbox_jogador().move(0, -camera_y), 2)
        for garcom in garcons:
            pygame.draw.rect(janela, (255, 0, 255), hitbox_garcom(garcom).move(0, -camera_y), 2)

    # Pontos no canto da tela
    escrever(str(pontos), fonte_grande, BRANCO, 60, 45)


# Película escura por cima do jogo
def escurecer_tela():
    pelicula = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pelicula.fill((0, 0, 0, 170))      # o 4º número é a transparência (0 a 255)
    janela.blit(pelicula, (0, 0))


# Tela de GAME OVER
def desenhar_game_over():
    escurecer_tela()
    escrever("GAME OVER", fonte_enorme, VERMELHO, LARGURA / 2, ALTURA / 2 - 90)
    escrever(motivo_derrota, fonte_media, BRANCO, LARGURA / 2, ALTURA / 2 - 20)
    escrever(f"Pontos: {pontos}    Recorde: {recorde}", fonte_media, DOURADO, LARGURA / 2, ALTURA / 2 + 35)
    escrever("Aperte ESPAÇO para voltar à loja", fonte_pequena, CINZA, LARGURA / 2, ALTURA / 2 + 100)


# Tela da LOJA (por enquanto só a estrutura: as compras vêm nos próximos passos)
def desenhar_loja():
    janela.fill(FUNDO_LOJA)

    escrever("LOJA", fonte_enorme, DOURADO, LARGURA / 2, 70)

    # Carteira: uma moedinha desenhada + quantas moedas o jogador tem
    pygame.draw.circle(janela, DOURADO, (LARGURA / 2 - 60, 140), 14)
    pygame.draw.circle(janela, DOURADO_BEBIDA, (LARGURA / 2 - 60, 140), 9)
    escrever(str(moedas), fonte_media, BRANCO, LARGURA / 2 + 10, 141)

    # Dois painéis: um para skins, outro para poderes
    painel_skins = pygame.Rect(60, 190, 320, 300)
    painel_poderes = pygame.Rect(420, 190, 320, 300)
    for painel, titulo in ((painel_skins, "SKINS"), (painel_poderes, "PODERES")):
        pygame.draw.rect(janela, PAINEL, painel, border_radius=16)
        pygame.draw.rect(janela, DOURADO, painel, 3, border_radius=16)   # borda
        escrever(titulo, fonte_media, DOURADO, painel.centerx, painel.top + 40)
        escrever("em breve...", fonte_pequena, CINZA, painel.centerx, painel.centery + 20)

    escrever("Aperte ESPAÇO para jogar", fonte_media, BRANCO, LARGURA / 2, 545)


rodando = True
while rodando:
    dt = relogio.tick(60) / 1000   # segundos desde o último quadro

    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type != pygame.KEYDOWN:
            continue                   # daqui pra baixo só nos interessam teclas

        # Cada tela responde às teclas de um jeito
        if estado == "loja":
            if evento.key == pygame.K_SPACE:
                # Começa uma rodada nova: jogador no início...
                jogador_coluna = COLUNAS // 2
                jogador_linha = 0
                jogador_x = jogador_coluna * TAMANHO_CASA
                jogador_y = jogador_linha * TAMANHO_CASA
                pulando = False
                pontos = 0

                # ...câmera com o jogador na 4ª linha de baixo para cima...
                camera_y = jogador_y - (LINHAS_NA_TELA - 4) * TAMANHO_CASA

                # ...e um mundo novo, sorteado do zero
                faixas = {linha_da_base_da_tela() + 1: "seguro"}
                garcons = []
                gerar_faixas_ate(linha_do_topo_da_tela() - 2)

                estado = "jogando"

        elif estado == "game_over":
            if evento.key == pygame.K_SPACE:
                estado = "loja"

        elif estado == "jogando" and not pulando:
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

            # Não deixa sair pelos lados, nem voltar para baixo da tela
            nova_coluna = max(0, min(nova_coluna, COLUNAS - 1))
            nova_linha = min(nova_linha, linha_da_base_da_tela())

            # Se a casa mudou, começa um pulo
            if (nova_coluna, nova_linha) != (jogador_coluna, jogador_linha):
                jogador_coluna = nova_coluna
                jogador_linha = nova_linha
                origem_x, origem_y = jogador_x, jogador_y
                destino_x = jogador_coluna * TAMANHO_CASA
                destino_y = jogador_linha * TAMANHO_CASA
                tempo_pulo = 0
                pulando = True

    # --- Atualização (só quando está jogando) ---
    altura_no_ar = 0
    esticar = 0
    if estado == "jogando":
        # Pulo
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

        # Pontos: a linha mais longe que o jogador já chegou
        pontos = max(pontos, -jogador_linha)

        # Câmera: segue o jogador para cima (nunca volta para baixo)
        alvo_camera = jogador_y - (LINHAS_NA_TELA - 4) * TAMANHO_CASA
        if alvo_camera < camera_y:
            camera_y += (alvo_camera - camera_y) * min(6 * dt, 1)   # desliza suave

        # Cria o mundo à frente e apaga o que ficou bem para trás
        gerar_faixas_ate(linha_do_topo_da_tela() - 2)
        limite = linha_da_base_da_tela() + 2
        garcons = [g for g in garcons if g["linha"] <= limite]
        for linha in list(faixas):
            if linha > limite:
                del faixas[linha]

        # Movimento dos garçons
        for garcom in garcons:
            garcom["x"] += garcom["velocidade"] * dt

            # Saiu por um lado? Volta pelo outro
            if garcom["velocidade"] > 0 and garcom["x"] > LARGURA:
                garcom["x"] = -LARGURA_GARCOM
            elif garcom["velocidade"] < 0 and garcom["x"] < -LARGURA_GARCOM:
                garcom["x"] = LARGURA

        # Colisão com os garçons
        for garcom in garcons:
            if hitbox_jogador().colliderect(hitbox_garcom(garcom)):
                estado = "game_over"
                motivo_derrota = "Esbarrou no garçom!"
                pulando = False
                recorde = max(recorde, pontos)

    # --- Desenho: cada tela desenha uma coisa ---
    if estado == "loja":
        desenhar_loja()
    elif estado == "jogando":
        desenhar_jogo(altura_no_ar, esticar)
    elif estado == "game_over":
        desenhar_jogo(0, 0)            # o jogo congelado por trás...
        desenhar_game_over()           # ...e o GAME OVER por cima

    pygame.display.update()

pygame.quit()