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
CHANCE_RIO = 0.35              # depois de uma faixa segura, chance de vir um rio
CHANCE_RIO_CONTINUAR = 0.6     # chance do rio ficar mais largo (mais uma faixa)
MAX_RIO_SEGUIDO = 3            # o rio tem no máximo 3 faixas de largura
DISTANCIA_DIFICIL = 150        # a partir desses pontos o jogo está no máximo da dificuldade
CHANCE_FICHA = 0.3             # NOVO: chance de aparecer uma ficha numa faixa de chão
CHANCE_FICHA_AZUL = 0.15       # NOVO: das fichas, quantas são azuis (valem 5)

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
CAIPIRINHA = (185, 215, 110)
CAIPIRINHA_ESCURA = (165, 200, 95)
GELO = (225, 245, 220)
LIMAO_CASCA = (70, 160, 40)
LIMAO_POLPA = (215, 240, 130)
MORANGO = (210, 35, 55)
MORANGO_FOLHA = (40, 140, 50)
SEMENTE = (250, 220, 120)
FICHA_VERMELHA = (200, 30, 45)         # NOVO
FICHA_AZUL = (40, 80, 200)             # NOVO
MAQUINA_CORPO = (70, 30, 110)          # NOVO
MAQUINA_LATERAL = (45, 20, 75)         # NOVO
MAQUINA_TELA = (60, 220, 230)          # NOVO
MAQUINA_LETREIRO = (255, 90, 170)      # NOVO

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
caiu_no_rio = False            # para desenhar o respingo em vez do achatado

# NOVO: carteira = todas as fichas que o jogador já juntou (é o dinheiro da loja)
carteira = 0
fichas_na_rodada = 0           # NOVO: quantas fichas pegou só nesta rodada

# Pontuação: quantas linhas o jogador avançou
pontos = 0
recorde = 0

# --- O mundo ---
# As linhas são numeradas a partir do início (linha 0) e,
# igual ao "y" do pygame, IR PARA CIMA DIMINUI o número: -1, -2, -3...
faixas = {}        # dicionário: número da linha -> tipo ("seguro", "garcons" ou "caipirinha")
garcons = []       # todos os garçons que existem agora
frutas = []        # todas as frutas boiando nos rios
maquinas = []      # NOVO: máquinas de fliperama (obstáculos parados)
fichas = []        # NOVO: fichas de poker no chão, esperando para serem pegas

# Câmera: a posição (em pixels do mundo) do topo da tela
camera_y = 0

# --- Jogador ---
# No rio a fruta carrega o jogador para o lado, então ele pode ficar
# "entre" duas colunas. Por isso guardamos o x em pixels.
jogador_linha = 0
jogador_x = (COLUNAS // 2) * TAMANHO_CASA
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


# Cria as frutas de UMA faixa de rio
# Cada "fruta" é uma fileira de 1 a 3 limões OU morangos boiando juntos
def criar_frutas_da_faixa(linha):
    d = dificuldade()

    # Frutas andam mais devagar que garçons
    velocidade = random.randint(50, 100) + int(50 * d)
    if random.random() < 0.5:
        velocidade = -velocidade

    # Quanto mais longe, fileiras menores (mais difícil de acertar o pulo)
    if d < 0.5:
        tamanhos = [2, 3, 3]
    else:
        tamanhos = [1, 2, 2, 3]

    # 3 fileiras espalhadas pelo "circuito" (a tela + 3 casas escondidas fora dela)
    quantidade = 3
    espaco = (LARGURA + 3 * TAMANHO_CASA) / quantidade
    for i in range(quantidade):
        tamanho = random.choice(tamanhos)
        largura = tamanho * TAMANHO_CASA
        frutas.append({
            "linha": linha,
            "x": i * espaco + random.uniform(0, espaco - largura - TAMANHO_CASA),
            "largura": largura,
            "velocidade": velocidade,
            "tipo": random.choice(["limao", "morango"]),
        })


# NOVO: existe uma máquina de fliperama nessa casa?
def tem_maquina(linha, coluna):
    for maquina in maquinas:
        if maquina["linha"] == linha and maquina["coluna"] == coluna:
            return True
    return False


# NOVO: coloca máquinas de fliperama numa faixa de feltro
def criar_maquinas_da_faixa(linha):
    if linha > 0:
        quantidade = random.randint(2, 5)          # atrás do início: só enfeite
    elif linha >= -1:
        return                                     # área de início: livre
    else:
        quantidade = random.randint(0, 2 + int(2 * dificuldade()))   # até 4 quando difícil

    # random.sample sorteia colunas SEM repetir
    for coluna in random.sample(range(COLUNAS), quantidade):
        maquinas.append({"linha": linha, "coluna": coluna})


# NOVO: às vezes coloca uma ficha numa casa livre da faixa
def talvez_criar_ficha(linha):
    if linha >= -1 or random.random() >= CHANCE_FICHA:
        return

    coluna = random.randrange(COLUNAS)
    if tem_maquina(linha, coluna):
        return                                     # casa ocupada: fica sem ficha

    if random.random() < CHANCE_FICHA_AZUL:
        fichas.append({"linha": linha, "coluna": coluna, "valor": 5, "cor": FICHA_AZUL})
    else:
        fichas.append({"linha": linha, "coluna": coluna, "valor": 1, "cor": FICHA_VERMELHA})


# Quantas faixas de um tipo existem seguidas logo abaixo desta linha?
def seguidas_abaixo(linha, tipo):
    contagem = 0
    while faixas.get(linha + 1 + contagem) == tipo:
        contagem += 1
    return contagem


# Sorteia o tipo de uma linha nova e cria o que tiver nela
def criar_faixa(linha):
    anterior = faixas[linha + 1]               # a faixa logo abaixo

    if linha >= -1:
        tipo = "seguro"                        # área de início: sempre segura

    elif anterior == "seguro":
        # depois de descanso vem perigo: rio ou garçons
        if random.random() < CHANCE_RIO:
            tipo = "caipirinha"
        else:
            tipo = "garcons"

    elif anterior == "caipirinha":
        # o rio continua (fica mais largo) ou termina numa margem segura
        if seguidas_abaixo(linha, "caipirinha") < MAX_RIO_SEGUIDO and random.random() < CHANCE_RIO_CONTINUAR:
            tipo = "caipirinha"
        else:
            tipo = "seguro"

    else:  # anterior == "garcons"
        if seguidas_abaixo(linha, "garcons") >= MAX_GARCONS_SEGUIDOS:
            tipo = "seguro"
        elif random.random() < CHANCE_FAIXA_SEGURA:
            tipo = "seguro"
        else:
            tipo = "garcons"

    faixas[linha] = tipo
    if tipo == "garcons":
        criar_garcons_da_faixa(linha)
        talvez_criar_ficha(linha)              # NOVO
    elif tipo == "caipirinha":
        criar_frutas_da_faixa(linha)
    else:
        criar_maquinas_da_faixa(linha)         # NOVO
        talvez_criar_ficha(linha)              # NOVO


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


# A fruta que está debaixo do jogador (ou None se ele está no líquido)
def fruta_debaixo_do_jogador():
    centro = jogador_x + TAMANHO_CASA / 2      # o "pé" do jogador é o meio dele
    for fruta in frutas:
        if fruta["linha"] == jogador_linha and fruta["x"] <= centro <= fruta["x"] + fruta["largura"]:
            return fruta
    return None


# Caixas de colisão (hitbox) -> em coordenadas do MUNDO
def hitbox_jogador():
    return pygame.Rect(jogador_x + 12, jogador_y + 12, 26, 30)


def hitbox_garcom(garcom):
    return pygame.Rect(garcom["x"] + 8, garcom["linha"] * TAMANHO_CASA + 12, 24, 30)


def desenhar_tabuleiro():
    for linha in range(linha_do_topo_da_tela(), linha_da_base_da_tela() + 2):
        tipo = faixas.get(linha)
        y_na_tela = linha * TAMANHO_CASA - camera_y

        if tipo == "garcons":
            cor = CARPETE if linha % 2 == 0 else CARPETE_ESCURO
        elif tipo == "caipirinha":
            cor = CAIPIRINHA if linha % 2 == 0 else CAIPIRINHA_ESCURA
        else:
            cor = VERDE_MESA if linha % 2 == 0 else VERDE_MESA_ESCURO
        pygame.draw.rect(janela, cor, (0, y_na_tela, LARGURA, TAMANHO_CASA))

        # Cubos de gelo boiando na caipirinha (enfeite)
        if tipo == "caipirinha":
            for i in range(3):
                gelo_x = (linha * 137 + i * 281) % LARGURA   # "aleatório", mas fixo para cada linha
                pygame.draw.rect(janela, GELO, (gelo_x, y_na_tela + 15 + i * 7, 14, 14), border_radius=3)


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


# Respingo quando o jogador cai na caipirinha
def desenhar_respingo(x, y):
    centro = (x + TAMANHO_CASA / 2, y + TAMANHO_CASA / 2)
    pygame.draw.circle(janela, GELO, centro, 22, 4)
    pygame.draw.circle(janela, BRANCO, centro, 12, 3)
    for dx, dy in ((-24, -16), (22, -18), (-14, -26), (16, -28)):
        pygame.draw.circle(janela, GELO, (centro[0] + dx, centro[1] + dy), 4)


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


# Desenha uma fileira de limões ou morangos
def desenhar_fruta(fruta):
    y = fruta["linha"] * TAMANHO_CASA - camera_y     # mundo -> tela
    quantidade = fruta["largura"] // TAMANHO_CASA
    cy = y + TAMANHO_CASA / 2

    for i in range(quantidade):
        cx = fruta["x"] + i * TAMANHO_CASA + TAMANHO_CASA / 2

        if fruta["tipo"] == "limao":
            # Rodela de limão: casca verde, polpa clara e os "gomos"
            pygame.draw.circle(janela, LIMAO_CASCA, (cx, cy), 22)
            pygame.draw.circle(janela, LIMAO_POLPA, (cx, cy), 18)
            for gomo in range(6):
                angulo = gomo * math.pi / 3
                ponta = (cx + math.cos(angulo) * 17, cy + math.sin(angulo) * 17)
                pygame.draw.line(janela, LIMAO_CASCA, (cx, cy), ponta, 2)
        else:
            # Morango: corpo vermelho, sementes e folhinhas em cima
            pygame.draw.ellipse(janela, MORANGO, (cx - 19, cy - 15, 38, 34))
            for sx, sy in ((-8, -2), (6, -4), (-2, 6), (9, 7), (-10, 9), (1, -9)):
                pygame.draw.circle(janela, SEMENTE, (cx + sx, cy + sy), 2)
            pygame.draw.ellipse(janela, MORANGO_FOLHA, (cx - 14, cy - 20, 14, 9))
            pygame.draw.ellipse(janela, MORANGO_FOLHA, (cx, cy - 20, 14, 9))


# NOVO: máquina de fliperama (mais alta que a casa, para parecer "em pé")
def desenhar_maquina(maquina):
    x = maquina["coluna"] * TAMANHO_CASA
    y = maquina["linha"] * TAMANHO_CASA - camera_y     # mundo -> tela

    # Sombra no chão
    pygame.draw.ellipse(janela, SOMBRA, (x + 4, y + TAMANHO_CASA - 12, TAMANHO_CASA - 8, 10))
    # Gabinete (a lateral mais escura dá a ideia de profundidade)
    pygame.draw.rect(janela, MAQUINA_LATERAL, (x + 6, y - 16, 38, 60), border_radius=4)
    pygame.draw.rect(janela, MAQUINA_CORPO, (x + 9, y - 16, 32, 60), border_radius=4)
    # Letreiro em cima
    pygame.draw.rect(janela, MAQUINA_LETREIRO, (x + 11, y - 13, 28, 8), border_radius=2)
    # Tela brilhando
    pygame.draw.rect(janela, MAQUINA_TELA, (x + 13, y - 2, 24, 18), border_radius=2)
    # Painel com joystick e botões
    pygame.draw.rect(janela, PRETO_TERNO, (x + 10, y + 20, 30, 8))
    pygame.draw.circle(janela, VERMELHO, (x + 17, y + 20), 3)
    pygame.draw.circle(janela, DOURADO, (x + 27, y + 24), 2)
    pygame.draw.circle(janela, MAQUINA_TELA, (x + 33, y + 24), 2)


# NOVO: ficha de poker girando e flutuando
def desenhar_ficha(ficha):
    tempo = pygame.time.get_ticks() / 1000
    cx = ficha["coluna"] * TAMANHO_CASA + TAMANHO_CASA / 2
    cy = ficha["linha"] * TAMANHO_CASA - camera_y + TAMANHO_CASA / 2
    flutuar = math.sin(tempo * 4 + ficha["coluna"]) * 3        # sobe e desce
    largura = abs(math.cos(tempo * 3 + ficha["linha"])) * 30 + 6  # "gira" afinando

    # Sombra fixa no chão
    pygame.draw.ellipse(janela, (0, 0, 0), (cx - 12, cy + 12, 24, 6))

    # Ficha: borda branca, centro colorido e um anel branco no meio
    area = pygame.Rect(0, 0, largura, 30)
    area.center = (cx, cy - 4 + flutuar)
    pygame.draw.ellipse(janela, BRANCO, area)
    pygame.draw.ellipse(janela, ficha["cor"], area.inflate(-6, -6))
    if largura > 18:
        pygame.draw.ellipse(janela, BRANCO, area.inflate(-16, -16), 2)


# NOVO: desenha uma ficha pequena + número (usado no placar e na loja)
def desenhar_contador_de_fichas(valor, x, y):
    pygame.draw.circle(janela, BRANCO, (x, y), 14)
    pygame.draw.circle(janela, FICHA_VERMELHA, (x, y), 11)
    pygame.draw.circle(janela, BRANCO, (x, y), 6, 2)
    imagem = fonte_media.render(str(valor), True, BRANCO)
    janela.blit(imagem, imagem.get_rect(midleft=(x + 22, y + 1)))


# Escreve um texto centralizado na posição (x, y)
def escrever(texto, fonte, cor, x, y):
    imagem = fonte.render(texto, True, cor)
    janela.blit(imagem, imagem.get_rect(center=(x, y)))


# Desenha o jogo inteiro (chão, frutas, fichas, máquinas, garçons, jogador, placar)
def desenhar_jogo(altura_no_ar, esticar):
    desenhar_tabuleiro()
    for fruta in frutas:
        desenhar_fruta(fruta)
    for ficha in fichas:
        desenhar_ficha(ficha)
    for maquina in maquinas:
        desenhar_maquina(maquina)
    for garcom in garcons:
        desenhar_garcom(garcom)

    jogador_y_na_tela = jogador_y - camera_y          # mundo -> tela
    if estado == "game_over" and caiu_no_rio:
        desenhar_respingo(jogador_x, jogador_y_na_tela)
    elif estado == "game_over":
        # Achatado! (esticar negativo deixa o corpo largo e baixinho)
        desenhar_jogador(jogador_x, jogador_y_na_tela, 0, -16)
    else:
        desenhar_jogador(jogador_x, jogador_y_na_tela, altura_no_ar, esticar)

    if MOSTRAR_HITBOX:
        pygame.draw.rect(janela, (0, 255, 255), hitbox_jogador().move(0, -camera_y), 2)
        for garcom in garcons:
            pygame.draw.rect(janela, (255, 0, 255), hitbox_garcom(garcom).move(0, -camera_y), 2)
        for fruta in frutas:
            area = (fruta["x"], fruta["linha"] * TAMANHO_CASA - camera_y, fruta["largura"], TAMANHO_CASA)
            pygame.draw.rect(janela, (255, 255, 0), area, 2)

    # Placar: pontos à esquerda, fichas da rodada à direita (com uma caixa escura atrás)
    desenhar_caixa_placar(10, 10, 110, 64)
    escrever(str(pontos), fonte_grande, BRANCO, 65, 44)
    desenhar_caixa_placar(LARGURA - 150, 10, 140, 60)
    desenhar_contador_de_fichas(fichas_na_rodada, LARGURA - 120, 40)


# NOVO: caixinha preta meio transparente, para o placar aparecer em qualquer fundo
def desenhar_caixa_placar(x, y, largura, altura):
    caixa = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(caixa, (0, 0, 0, 140), caixa.get_rect(), border_radius=12)
    janela.blit(caixa, (x, y))


# Película escura por cima do jogo
def escurecer_tela():
    pelicula = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pelicula.fill((0, 0, 0, 170))      # o 4º número é a transparência (0 a 255)
    janela.blit(pelicula, (0, 0))


# Tela de GAME OVER
def desenhar_game_over():
    escurecer_tela()
    escrever("GAME OVER", fonte_enorme, VERMELHO, LARGURA / 2, ALTURA / 2 - 110)
    escrever(motivo_derrota, fonte_media, BRANCO, LARGURA / 2, ALTURA / 2 - 40)
    escrever(f"Pontos: {pontos}    Recorde: {recorde}", fonte_media, DOURADO, LARGURA / 2, ALTURA / 2 + 15)
    escrever(f"Fichas nesta rodada: +{fichas_na_rodada}", fonte_media, BRANCO, LARGURA / 2, ALTURA / 2 + 60)
    escrever("Aperte ESPAÇO para voltar à loja", fonte_pequena, CINZA, LARGURA / 2, ALTURA / 2 + 120)


# Tela da LOJA (por enquanto só a estrutura: as compras vêm nos próximos passos)
def desenhar_loja():
    janela.fill(FUNDO_LOJA)

    escrever("LOJA", fonte_enorme, DOURADO, LARGURA / 2, 70)

    # Carteira: quantas fichas o jogador tem para gastar
    desenhar_contador_de_fichas(carteira, LARGURA / 2 - 30, 140)

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
                jogador_linha = 0
                jogador_x = (COLUNAS // 2) * TAMANHO_CASA
                jogador_y = jogador_linha * TAMANHO_CASA
                pulando = False
                pontos = 0
                fichas_na_rodada = 0
                caiu_no_rio = False

                # ...câmera com o jogador na 4ª linha de baixo para cima...
                camera_y = jogador_y - (LINHAS_NA_TELA - 4) * TAMANHO_CASA

                # ...e um mundo novo, sorteado do zero
                faixas = {linha_da_base_da_tela() + 1: "seguro"}
                garcons = []
                frutas = []
                maquinas = []
                fichas = []
                gerar_faixas_ate(linha_do_topo_da_tela() - 2)

                estado = "jogando"

        elif estado == "game_over":
            if evento.key == pygame.K_SPACE:
                estado = "loja"

        elif estado == "jogando" and not pulando:
            # Para que lado andar: dx = colunas, dy = linhas
            dx, dy = 0, 0
            if evento.key in (pygame.K_UP, pygame.K_w):
                dy = -1        # frente
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                dy = 1         # trás
            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                dx = -1        # esquerda
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                dx = 1         # direita

            # Não deixa voltar para baixo da tela
            nova_linha = min(jogador_linha + dy, linha_da_base_da_tela())

            # Onde ele vai cair no eixo x
            if faixas.get(nova_linha) == "caipirinha":
                # no rio: anda uma casa a partir de onde está (sem "encaixar" na coluna)
                novo_x = jogador_x + dx * TAMANHO_CASA
            else:
                # no chão: encaixa na coluna mais próxima
                novo_x = (round(jogador_x / TAMANHO_CASA) + dx) * TAMANHO_CASA

            # Não deixa sair pelos lados
            novo_x = max(0, min(novo_x, (COLUNAS - 1) * TAMANHO_CASA))

            # NOVO: tem uma máquina de fliperama lá? Então não pula (fica onde está)
            if tem_maquina(nova_linha, round(novo_x / TAMANHO_CASA)):
                continue

            # Se o lugar mudou, começa um pulo
            if (novo_x, nova_linha) != (jogador_x, jogador_linha):
                jogador_linha = nova_linha
                origem_x, origem_y = jogador_x, jogador_y
                destino_x = novo_x
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
        recorde = max(recorde, pontos)

        # Câmera: segue o jogador para cima (nunca volta para baixo)
        alvo_camera = jogador_y - (LINHAS_NA_TELA - 4) * TAMANHO_CASA
        if alvo_camera < camera_y:
            camera_y += (alvo_camera - camera_y) * min(6 * dt, 1)   # desliza suave

        # Cria o mundo à frente e apaga o que ficou bem para trás
        gerar_faixas_ate(linha_do_topo_da_tela() - 2)
        limite = linha_da_base_da_tela() + 2
        garcons = [g for g in garcons if g["linha"] <= limite]
        frutas = [f for f in frutas if f["linha"] <= limite]
        maquinas = [m for m in maquinas if m["linha"] <= limite]
        fichas = [f for f in fichas if f["linha"] <= limite]
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

        # Movimento das frutas
        # Todas dão a volta pelo mesmo "circuito" (a tela + 3 casas escondidas),
        # assim fileiras de tamanhos diferentes nunca se encavalam
        circuito = LARGURA + 3 * TAMANHO_CASA
        for fruta in frutas:
            fruta["x"] += fruta["velocidade"] * dt

            if fruta["velocidade"] > 0 and fruta["x"] > LARGURA:
                fruta["x"] -= circuito
            elif fruta["velocidade"] < 0 and fruta["x"] < -3 * TAMANHO_CASA:
                fruta["x"] += circuito

        # NOVO: pegar fichas (basta passar pela casa dela, até no meio do pulo)
        for ficha in fichas[:]:            # [:] = uma cópia, para poder remover da original
            perto_x = abs(jogador_x - ficha["coluna"] * TAMANHO_CASA) < TAMANHO_CASA / 2
            perto_y = abs(jogador_y - ficha["linha"] * TAMANHO_CASA) < TAMANHO_CASA / 2
            if perto_x and perto_y:
                fichas.remove(ficha)
                fichas_na_rodada += ficha["valor"]
                carteira += ficha["valor"]

        # O rio de caipirinha (só vale quando o jogador já pousou)
        if faixas.get(jogador_linha) == "caipirinha" and not pulando:
            fruta = fruta_debaixo_do_jogador()
            if fruta is None:
                estado = "game_over"
                motivo_derrota = "Caiu na caipirinha!"
                caiu_no_rio = True
            else:
                # Em cima da fruta: ela leva o jogador junto
                jogador_x += fruta["velocidade"] * dt

                # A fruta levou o jogador para fora da tela?
                centro = jogador_x + TAMANHO_CASA / 2
                if centro < 0 or centro > LARGURA:
                    estado = "game_over"
                    motivo_derrota = "A fruta te levou embora!"
                    caiu_no_rio = True

        # Colisão com os garçons
        for garcom in garcons:
            if estado == "jogando" and hitbox_jogador().colliderect(hitbox_garcom(garcom)):
                estado = "game_over"
                motivo_derrota = "Esbarrou no garçom!"
                pulando = False

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