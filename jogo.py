import pygame
import math
import random
import json     # para salvar o progresso num arquivo
import os       # para achar a pasta onde o jogo está
pygame.init()
pygame.mixer.init()
# --- Música de fundo estilo arcade ---
import io
import wave
from array import array

def tocar_musica():
    frequencia = 22050
    duracao_nota = 0.15

    # Melodia: cada número representa uma nota musical
    melodia = [
        76, 79, 81, 79, 76, 72, 74, 76,
        77, 81, 84, 81, 77, 74, 72, 74,
        79, 83, 86, 83, 79, 77, 76, 74,
        72, 76, 79, 76, 74, 71, 72, 0,
    ]

    baixos = [48, 53, 55, 48]
    amostras = array("h")
    quantidade = int(frequencia * duracao_nota)

    for indice, nota in enumerate(melodia):
        nota_baixo = baixos[indice // 8]
        freq_baixo = 440 * 2 ** ((nota_baixo - 69) / 12)

        for i in range(quantidade):
            tempo = i / frequencia

            # Suaviza o começo e o fim de cada nota
            envelope = min(
                1,
                i / (frequencia * 0.005),
                (quantidade - 1 - i) / (frequencia * 0.025)
            )

            som = 0
            if nota != 0:
                freq_nota = 440 * 2 ** ((nota - 69) / 12)
                onda = 1 if math.sin(2 * math.pi * freq_nota * tempo) >= 0 else -1
                som += onda * 0.18

            som += math.sin(2 * math.pi * freq_baixo * tempo) * 0.22
            amostras.append(int(som * envelope * 32767))

    # Cria o áudio na memória, sem precisar baixar uma música
    import sys
    if sys.byteorder == "big":
        amostras.byteswap()

    arquivo = io.BytesIO()
    with wave.open(arquivo, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(frequencia)
        audio.writeframes(amostras.tobytes())

    arquivo.seek(0)
    musica = pygame.mixer.Sound(file=arquivo)
    musica.set_volume(0.3)
    musica.play(loops=-1)
    return musica

musica_fundo = tocar_musica()
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
CHANCE_FICHA = 0.3             # chance de aparecer uma ficha numa faixa de chão
CHANCE_FICHA_AZUL = 0.15       # das fichas, quantas são azuis (valem 5)

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
FICHA_VERMELHA = (200, 30, 45)
FICHA_AZUL = (40, 80, 200)
MAQUINA_CORPO = (70, 30, 110)
MAQUINA_LATERAL = (45, 20, 75)
MAQUINA_TELA = (60, 220, 230)
MAQUINA_LETREIRO = (255, 90, 170)
PRETO = (20, 20, 25)
VERDE_OK = (90, 210, 110)
ROXO = (110, 50, 160)

# --- Garçons ---
LARGURA_GARCOM = 40

# --- Raridades (nome que aparece na loja e a cor dela) ---
RARIDADES = {
    "raro":     {"nome": "RARO",     "cor": (70, 140, 255)},    # azul
    "epico":    {"nome": "ÉPICO",    "cor": (170, 80, 230)},    # roxo
    "lendario": {"nome": "LENDÁRIO", "cor": (255, 140, 30)},    # laranja
}

# --- Personagens em pixel art ---
# Cada letra é um "pixel" e cada linha tem 12 letras. O "." é transparente.
# A tabela CORES_PIXEL diz que cor cada letra vira.
CORES_PIXEL = {
    "K": (20, 20, 25),      # contorno preto
    "S": (230, 175, 130),   # pele
    "W": (245, 245, 245),   # branco
    "H": (245, 190, 40),    # cabelo loiro
    "h": (90, 60, 30),      # cabelo castanho (lateral raspada)
    "Y": (250, 215, 40),    # camisa amarela
    "G": (30, 150, 70),     # verde
    "B": (30, 70, 170),     # azul (calção)
    "g": (170, 170, 180),   # cinza claro (chuteira)
    "c": (180, 180, 185),   # cabelo grisalho
    "D": (50, 50, 60),      # cinza escuro (camisa / calça)
    "T": (120, 120, 130),   # gravata
    "P": (230, 110, 160),   # tubo de ensaio rosa
    "N": (35, 40, 75),      # azul-noite (uniforme)
    "V": (120, 50, 160),    # roxo (capa)
    "R": (200, 40, 50),     # vermelho (cinto)
    "O": (250, 200, 60),    # dourado (emblema)
    "M": (115, 70, 40),     # NOVO: cabelo castanho penteado para trás
    "b": (95, 58, 32),      # NOVO: barba
    "L": (190, 215, 240),   # NOVO: camisa azul-clara
    "A": (70, 100, 150),    # NOVO: gravata azul
}

CRAQUE = [
    "...KKKKKK...",
    "..KHHHHHHK..",
    ".KhHHHHHHhK.",
    ".KhSSSSSShK.",
    ".KSSKSSKSSK.",
    ".KSSKSSKSSK.",
    ".KSSSSSSSSK.",
    "..KSSKKSSK..",
    "...KSSSSK...",
    ".KKYYGGYYKK.",
    "KYYYYYYYYYYK",
    "KSKYYGGYYKSK",
    "KSKYYYYYYKSK",
    ".KKBBBBBBKK.",
    "..KWWK.KWWK.",
    ".KgggK.KgggK",
]

PROFESSOR = [
    "...KKKKKK...",
    "..KcSSSScK..",
    ".KcSSSSSScK.",
    ".KSccSScccK.",
    ".KSSKSSKSSK.",
    ".KSSSSSSSSK.",
    "..KSSKKSSK..",
    "...KSSSSK...",
    ".KWWKDTDKWWK",
    "KWWWWDTDWWPK",
    "KWWWWDTDWWPK",
    "KSWWWWWWWWSK",
    ".KWWWWWWWWK.",
    ".KWWWWWWWWK.",
    "..KDDK.KDDK.",
    ".KKKKK.KKKKK",
]

VIGILANTE = [
    "...KKKKKK...",
    "..KNNNNNNK..",
    ".KNNNNNNNNK.",
    ".KNKKKKKKNK.",
    ".KNKWKKWKNK.",
    ".KNSSSSSSNK.",
    "..KSSKKSSK..",
    ".VKNSSSSNKV.",
    "VVKNNONNNKVV",
    "VVNNNNNNNNVV",
    "VVKNRRRRNKVV",
    "VVKNNNNNNKVV",
    "VV.KNNNNK.VV",
    "V..KNK.KNK.V",
    "...KNK.KNK..",
    "..KKKK.KKKK.",
]

# NOVO
MAGNATA = [
    "...KKKKKK...",
    "..KMMMMMMK..",
    ".KMMMMMMMMK.",
    ".KMSSSSSSMK.",
    ".KSSKSSKSSK.",
    ".KSSSSSSSSK.",
    ".KbSSSSSSbK.",
    "..KbbWWbbK..",
    "...KbbbbK...",
    ".KNNLAALNNK.",
    "KNNNLAALNNNK",
    "KNNNNAANNNNK",
    "KSKNNAANNKSK",
    ".KKNNNNNNKK.",
    "..KNNK.KNNK.",
    ".KKKKK.KKKKK",
]

# --- Skins (os personagens que dá para comprar na loja) ---
# Cada skin é desenhada de UM destes jeitos:
#   "tipo"    -> desenhada com formas (veja desenhar_personagem)
#   "desenho" -> pixel art feita com letras (como o CRAQUE ali em cima)
#   "arquivo" -> uma imagem PNG que você mesmo desenhou (na pasta do jogo)
SKINS = [
    {"nome": "Dadinho",        "preco": 0,   "raridade": "raro",     "tipo": "dado"},
    {"nome": "Ás de Copas",    "preco": 20,  "raridade": "raro",     "tipo": "carta"},
    {"nome": "Ficha Maluca",   "preco": 40,  "raridade": "raro",     "tipo": "ficha"},
    {"nome": "Professor",      "preco": 60,  "raridade": "raro",     "desenho": PROFESSOR},
    {"nome": "Barra de Ouro",  "preco": 90,  "raridade": "epico",    "tipo": "ouro"},
    {"nome": "Mágico",         "preco": 120, "raridade": "epico",    "tipo": "magico"},
    {"nome": "Sete da Sorte",  "preco": 150, "raridade": "epico",    "tipo": "sete"},
    {"nome": "Vigilante",      "preco": 200, "raridade": "epico",    "desenho": VIGILANTE},
    {"nome": "Craque",         "preco": 400, "raridade": "lendario", "desenho": CRAQUE},
    {"nome": "Magnata",        "preco": 500, "raridade": "lendario", "desenho": MAGNATA},       # NOVO
    # Exemplo de skin feita por você (desenhe um PNG e tire o # da linha abaixo):
    # {"nome": "Minha Skin", "preco": 300, "raridade": "epico", "arquivo": "minha_skin.png"},
]

# --- NOVO: Poderes (comprados na loja, valem para a PRÓXIMA rodada) ---
PODERES = [
    {"id": "salto",  "nome": "Salto Duplo", "preco": 15, "tecla_compra": "1",
     "descricao": "SHIFT + seta: pula 2 casas"},
    {"id": "quebra", "nome": "Quebra-Tudo", "preco": 25, "tecla_compra": "2",
     "descricao": "E: destrói o que estiver perto"},
]
MAX_CARGAS = 5                 # quantas cargas de cada poder dá para guardar
DURACAO_SALTO_DUPLO = 0.22     # o salto duplo demora mais...
ALTURA_SALTO_DUPLO = 40        # ...e vai mais alto
RAIO_QUEBRA = 2.5 * TAMANHO_CASA   # alcance do Quebra-Tudo (2 casas e meia)
LARANJA = (255, 140, 30)

# Arquivo onde o progresso fica salvo (na mesma pasta do jogo)
PASTA_DO_JOGO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SAVE = os.path.join(PASTA_DO_JOGO, "save.json")

janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cassino Crossing")
relogio = pygame.time.Clock()

# Fontes para escrever na tela (None = fonte padrão do pygame)
fonte_enorme = pygame.font.Font(None, 110)
fonte_grande = pygame.font.Font(None, 72)
fonte_media = pygame.font.Font(None, 44)
fonte_pequena = pygame.font.Font(None, 32)
fonte_ficha = pygame.font.Font(None, 22)       # o número escrito na ficha
fonte_raridade = pygame.font.Font(None, 26)    # RARO / ÉPICO / LENDÁRIO

# As telas do jogo -> "loja", "jogando" ou "game_over"
estado = "loja"
motivo_derrota = ""            # por que perdeu (aparece no game over)
caiu_no_rio = False            # para desenhar o respingo em vez do achatado

# Lê o progresso salvo. Se o arquivo não existe (primeira vez) ou está
# estragado, começa do zero.
def carregar_progresso():
    try:
        with open(ARQUIVO_SAVE, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Grava o progresso no arquivo save.json
def salvar_progresso():
    dados = {
        "carteira": carteira,
        "recorde": recorde,
        "skins_compradas": skins_compradas,
        "skin_em_uso": SKINS[skin_equipada]["nome"],    # salva pelo NOME
        "poderes_guardados": poderes_guardados,         # NOVO
    }
    with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


progresso = carregar_progresso()

# Carteira = todas as fichas que o jogador já juntou (é o dinheiro da loja)
carteira = progresso.get("carteira", 0)            # vem do arquivo salvo
fichas_na_rodada = 0           # quantas fichas pegou só nesta rodada

# Pontuação: quantas linhas o jogador avançou
pontos = 0
recorde = progresso.get("recorde", 0)              # vem do arquivo salvo

# Skins
skins_compradas = progresso.get("skins_compradas", ["Dadinho"])   # nomes das skins que já são suas

# A skin em uso é salva pelo NOME. Assim, se você mudar a ordem da lista
# SKINS ou criar skins novas, o save continua apontando para a skin certa.
skin_equipada = 0                  # posição na lista SKINS
for i, skin in enumerate(SKINS):
    if skin["nome"] == progresso.get("skin_em_uso"):
        skin_equipada = i
skin_na_vitrine = skin_equipada    # qual skin está aparecendo na loja agora

# NOVO: poderes
# poderes_guardados -> cargas compradas na loja, esperando a próxima rodada
# cargas            -> cargas que o jogador pode usar na rodada de agora
poderes_guardados = progresso.get("poderes_guardados", {"salto": 0, "quebra": 0})
cargas = {"salto": 0, "quebra": 0}
explosoes = []                     # efeitos visuais do Quebra-Tudo

# Mensagem rápida da loja ("Comprou!", "Fichas insuficientes"...)
mensagem_loja = ""
tempo_mensagem = 0

# --- O mundo ---
# As linhas são numeradas a partir do início (linha 0) e,
# igual ao "y" do pygame, IR PARA CIMA DIMINUI o número: -1, -2, -3...
faixas = {}        # dicionário: número da linha -> tipo ("seguro", "garcons" ou "caipirinha")
garcons = []       # todos os garçons que existem agora
frutas = []        # todas as frutas boiando nos rios
maquinas = []      # máquinas de fliperama (obstáculos parados)
fichas = []        # fichas de poker no chão, esperando para serem pegas

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
salto_duplo = False                    # NOVO: o pulo de agora é um salto duplo?
duracao_pulo = DURACAO_PULO            # NOVO: duração e altura do pulo de agora
altura_pulo = ALTURA_PULO
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
    if linha % 2 == 0:
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


# Existe uma máquina de fliperama nessa casa?
def tem_maquina(linha, coluna):
    for maquina in maquinas:
        if maquina["linha"] == linha and maquina["coluna"] == coluna:
            return True
    return False


# Coloca máquinas de fliperama numa faixa de feltro
def criar_maquinas_da_faixa(linha):
    if linha >= -1:
        return                                     # área de início (5 primeiras linhas): livre

    quantidade = random.randint(0, 2 + int(2 * dificuldade()))   # até 4 quando difícil

    # random.sample sorteia colunas SEM repetir
    for coluna in random.sample(range(COLUNAS), quantidade):
        maquinas.append({"linha": linha, "coluna": coluna})


# Às vezes coloca uma ficha numa casa livre da faixa
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
        # Depois de descanso vem perigo: rio ou garçons
        if random.random() < CHANCE_RIO:
            tipo = "caipirinha"
        else:
            tipo = "garcons"

    elif anterior == "caipirinha":
        # O rio continua (fica mais largo) ou termina numa margem segura
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
        talvez_criar_ficha(linha)
    elif tipo == "caipirinha":
        criar_frutas_da_faixa(linha)
    else:
        criar_maquinas_da_faixa(linha)
        talvez_criar_ficha(linha)


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


# Transforma uma skin de imagem numa Surface do pygame.
# Guarda o resultado num dicionário, para não refazer a imagem a cada quadro.
imagens_prontas = {}


def imagem_da_skin(skin):
    nome = skin["nome"]
    if nome not in imagens_prontas:
        if "desenho" in skin:
            # Pixel art de letras: pinta um pixel para cada letra
            desenho = skin["desenho"]
            imagem = pygame.Surface((len(desenho[0]), len(desenho)), pygame.SRCALPHA)
            for y, linha in enumerate(desenho):
                for x, letra in enumerate(linha):
                    if letra != ".":
                        imagem.set_at((x, y), CORES_PIXEL[letra])
        elif "arquivo" in skin:
            # PNG feito por você (com fundo transparente), na pasta do jogo
            caminho = os.path.join(PASTA_DO_JOGO, skin["arquivo"])
            imagem = pygame.image.load(caminho).convert_alpha()
        else:
            imagem = None          # skin desenhada com formas (dado, carta...)
        imagens_prontas[nome] = imagem
    return imagens_prontas[nome]


# Desenha QUALQUER personagem, em QUALQUER superfície
#   tela -> onde desenhar (a janela do jogo, ou uma imagem para a vitrine da loja)
#   skin -> um dicionário da lista SKINS
#   cor_sombra -> cor da sombra (na loja ela é preta, no jogo é verde-escura)
def desenhar_personagem(tela, skin, x, y, altura_no_ar, esticar, cor_sombra=SOMBRA):
    # Sombra: fica sempre no chão e diminui quando o personagem sobe
    tamanho_sombra = 34 - altura_no_ar * 0.6
    pygame.draw.ellipse(
        tela, cor_sombra,
        (x + (TAMANHO_CASA - tamanho_sombra) / 2, y + TAMANHO_CASA - 14, tamanho_sombra, 10),
    )

    # Skins de imagem (pixel art ou PNG). A imagem é esticada e achatada
    # do mesmo jeito que o corpo das outras skins.
    imagem = imagem_da_skin(skin)
    if imagem is not None:
        largura = 36 - esticar
        altura = 48 + esticar * 1.3            # personagens de gente são mais altos
        imagem = pygame.transform.scale(imagem, (int(largura), int(altura)))
        tela.blit(imagem, imagem.get_rect(midbottom=(x + TAMANHO_CASA / 2, y + TAMANHO_CASA - 8 - altura_no_ar)))
        return                                 # já desenhou: não precisa fazer o resto

    # Corpo: no ar fica mais alto e mais fino (efeito "elástico")
    largura_corpo = 36 - esticar
    altura_corpo = 36 + esticar
    corpo = pygame.Rect(0, 0, largura_corpo, altura_corpo)
    corpo.midbottom = (x + TAMANHO_CASA / 2, y + TAMANHO_CASA - 8 - altura_no_ar)

    # Pontos de referência dentro do corpo (em fração da largura/altura).
    # Usar frações faz os detalhes esticarem e achatarem junto com o corpo.
    def ponto(fx, fy):
        return (corpo.x + corpo.width * fx, corpo.y + corpo.height * fy)

    tipo = skin["tipo"]

    if tipo == "dado":
        # Dado branco: os "olhos" são as bolinhas da face 2
        pygame.draw.rect(tela, BRANCO, corpo, border_radius=7)
        pygame.draw.rect(tela, CINZA, corpo, 2, border_radius=7)
        pygame.draw.circle(tela, PRETO, ponto(0.3, 0.35), 4)
        pygame.draw.circle(tela, PRETO, ponto(0.7, 0.35), 4)
        pygame.draw.circle(tela, VERMELHO, ponto(0.5, 0.72), 3)      # boquinha

    elif tipo == "carta":
        # Carta de baralho: fundo branco, borda vermelha e um coração no meio
        pygame.draw.rect(tela, BRANCO, corpo, border_radius=4)
        pygame.draw.rect(tela, VERMELHO, corpo.inflate(-6, -6), 2, border_radius=3)
        cx, cy = ponto(0.5, 0.62)
        pygame.draw.circle(tela, VERMELHO, (cx - 4, cy - 3), 5)
        pygame.draw.circle(tela, VERMELHO, (cx + 4, cy - 3), 5)
        pygame.draw.polygon(tela, VERMELHO, [(cx - 9, cy - 1), (cx + 9, cy - 1), (cx, cy + 9)])
        pygame.draw.circle(tela, PRETO, ponto(0.32, 0.25), 3)
        pygame.draw.circle(tela, PRETO, ponto(0.68, 0.25), 3)

    elif tipo == "ficha":
        # Ficha de poker de pé: redonda, com faixas brancas
        pygame.draw.ellipse(tela, FICHA_VERMELHA, corpo)
        pygame.draw.ellipse(tela, BRANCO, corpo.inflate(-12, -12), 3)
        for fx, fy in ((0.5, 0.06), (0.5, 0.94), (0.06, 0.5), (0.94, 0.5)):
            pygame.draw.circle(tela, BRANCO, ponto(fx, fy), 4)
        pygame.draw.circle(tela, BRANCO, ponto(0.37, 0.42), 5)
        pygame.draw.circle(tela, BRANCO, ponto(0.63, 0.42), 5)
        pygame.draw.circle(tela, PRETO, ponto(0.39, 0.44), 2)
        pygame.draw.circle(tela, PRETO, ponto(0.65, 0.44), 2)

    elif tipo == "ouro":
        # Barra de ouro: dourada, com a parte de baixo mais escura e um brilho
        pygame.draw.rect(tela, escurecer(DOURADO, 0.7), corpo, border_radius=5)
        pygame.draw.rect(tela, DOURADO, (corpo.x, corpo.y, corpo.width, corpo.height * 0.7), border_radius=5)
        pygame.draw.line(tela, BRANCO, ponto(0.15, 0.55), ponto(0.45, 0.12), 3)
        pygame.draw.circle(tela, PRETO, ponto(0.62, 0.35), 3)
        pygame.draw.circle(tela, PRETO, ponto(0.84, 0.35), 3)

    elif tipo == "magico":
        # Mágico: corpo roxo, olhos e uma cartola preta com faixa vermelha
        pygame.draw.rect(tela, ROXO, corpo, border_radius=8)
        pygame.draw.circle(tela, BRANCO, ponto(0.33, 0.45), 5)
        pygame.draw.circle(tela, BRANCO, ponto(0.67, 0.45), 5)
        pygame.draw.circle(tela, PRETO, ponto(0.35, 0.47), 2)
        pygame.draw.circle(tela, PRETO, ponto(0.69, 0.47), 2)
        aba = pygame.Rect(0, 0, corpo.width + 8, 5)
        aba.midbottom = (corpo.centerx, corpo.y + 3)
        copa = pygame.Rect(0, 0, corpo.width * 0.6, 16)
        copa.midbottom = aba.midtop
        pygame.draw.rect(tela, PRETO, copa)
        pygame.draw.rect(tela, VERMELHO, (copa.x, copa.bottom - 5, copa.width, 4))
        pygame.draw.rect(tela, PRETO, aba, border_radius=2)

    elif tipo == "sete":
        # Sete da sorte (de caça-níquel): roxo com um 7 dourado
        pygame.draw.rect(tela, MAQUINA_CORPO, corpo, border_radius=8)
        pygame.draw.rect(tela, DOURADO, corpo, 2, border_radius=8)
        pygame.draw.lines(tela, DOURADO, False, [ponto(0.25, 0.4), ponto(0.75, 0.4), ponto(0.42, 0.88)], 5)
        pygame.draw.circle(tela, BRANCO, ponto(0.35, 0.2), 3)
        pygame.draw.circle(tela, BRANCO, ponto(0.65, 0.2), 3)


# Desenha o jogador com a skin que ele está usando
def desenhar_jogador(x, y, altura_no_ar, esticar):
    desenhar_personagem(janela, SKINS[skin_equipada], x, y, altura_no_ar, esticar)


def desenhar_respingo(x, y):
    t = tempo_queda
    progresso = min(t / 0.7, 1)

    # Mantém o efeito visível mesmo se cair pela lateral
    centro_x = max(20, min(x + TAMANHO_CASA / 2, LARGURA - 20))
    centro_y = y + TAMANHO_CASA / 2

    # Personagem encolhendo, descendo e desaparecendo
    if progresso < 1:
        imagem = pygame.Surface((80, 100), pygame.SRCALPHA)
        desenhar_personagem(
            imagem, SKINS[skin_equipada], 15, 30, 0, 0
        )

        escala = 1 - progresso * 0.7
        imagem = pygame.transform.scale(
            imagem,
            (int(80 * escala), int(100 * escala))
        )
        imagem.set_alpha(int(255 * (1 - progresso)))

        posicao = imagem.get_rect(
            center=(centro_x, centro_y + progresso * 20)
        )
        janela.blit(imagem, posicao)

    # Ondas que se espalham e desaparecem
    efeitos = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    for atraso in (0, 0.18, 0.36):
        idade = t - atraso
        if 0 <= idade < 0.7:
            raio = 8 + idade * 65
            alpha = int(220 * (1 - idade / 0.7))
            pygame.draw.ellipse(
                efeitos, (*GELO, alpha),
                (centro_x - raio, centro_y - raio / 3,
                 raio * 2, raio * 2 / 3),
                2
            )

    # Gotinhas subindo e caindo
    if t < 0.65:
        alpha = int(255 * (1 - t / 0.65))

        for i in range(8):
            angulo = i * math.pi / 4
            dx = math.cos(angulo) * 65 * t
            dy = math.sin(angulo) * 30 * t - 120 * t + 220 * t ** 2

            pygame.draw.circle(
                efeitos, (*GELO, alpha),
                (int(centro_x + dx), int(centro_y + dy)),
                max(1, int(4 * (1 - t / 0.65)))
            )

    janela.blit(efeitos, (0, 0))


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


# Máquina de fliperama (mais alta que a casa, para parecer "em pé")
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


# Deixa uma cor mais escura (multiplica o R, G e B por um número menor que 1)
def escurecer(cor, quanto=0.55):
    return (int(cor[0] * quanto), int(cor[1] * quanto), int(cor[2] * quanto))


# Desenha uma ficha de poker de verdade
#   achatar   -> 1 = vista de cima (redonda); menor que 1 = deitada na mesa, vista de lado
#   espessura -> a "grossura" da ficha em pixels (0 = sem grossura)
#   valor     -> número escrito no meio (ou None para não escrever)
def desenhar_ficha_de_poker(cx, cy, raio, cor, achatar=1.0, espessura=0, valor=None):
    meia_altura = raio * achatar           # a ficha deitada vira uma elipse mais baixa
    topo = pygame.Rect(0, 0, raio * 2, meia_altura * 2)
    topo.center = (cx, cy)

    # 1) Lateral (a grossura): uma elipse mais escura um pouco abaixo do topo
    if espessura > 0:
        cor_lateral = escurecer(cor)
        pygame.draw.ellipse(janela, cor_lateral, topo.move(0, espessura))
        pygame.draw.rect(janela, cor_lateral, (cx - raio, cy, raio * 2, espessura))
        # As listras brancas que toda ficha tem na lateral
        for posicao in (-0.65, 0, 0.65):
            base_y = cy + meia_altura * math.sqrt(1 - posicao ** 2)
            pygame.draw.rect(janela, BRANCO, (cx + posicao * raio - 3, base_y - 1, 6, espessura + 1))

    # 2) Topo colorido, com um contorno escuro para destacar de qualquer fundo
    pygame.draw.ellipse(janela, escurecer(cor, 0.3), topo.inflate(4, 4))
    pygame.draw.ellipse(janela, cor, topo)

    # 3) Os 6 "dentes" brancos na borda (a marca registrada da ficha de poker)
    for i in range(6):
        angulo = i * math.pi / 3 + math.pi / 6
        dente = pygame.Rect(0, 0, raio * 0.42, meia_altura * 0.42)
        dente.center = (cx + math.cos(angulo) * raio * 0.78, cy + math.sin(angulo) * meia_altura * 0.78)
        pygame.draw.ellipse(janela, BRANCO, dente)

    # 4) Anel branco por dentro e o miolo colorido
    pygame.draw.ellipse(janela, BRANCO, topo.inflate(-raio * 0.75, -meia_altura * 0.75))
    pygame.draw.ellipse(janela, cor, topo.inflate(-raio * 0.95, -meia_altura * 0.95))

    # 5) Valor no meio, achatado junto com a ficha
    if valor is not None:
        texto = fonte_ficha.render(str(valor), True, BRANCO)
        altura_texto = max(1, int(texto.get_height() * achatar))
        texto = pygame.transform.scale(texto, (texto.get_width(), altura_texto))
        janela.blit(texto, texto.get_rect(center=(cx, cy + 1)))


# Ficha no chão, deitada e flutuando de leve
def desenhar_ficha(ficha):
    tempo = pygame.time.get_ticks() / 1000
    cx = ficha["coluna"] * TAMANHO_CASA + TAMANHO_CASA / 2
    cy = ficha["linha"] * TAMANHO_CASA - camera_y + TAMANHO_CASA / 2
    flutuar = math.sin(tempo * 4 + ficha["coluna"]) * 3        # sobe e desce

    # Sombra fixa no chão
    pygame.draw.ellipse(janela, (0, 0, 0), (cx - 16, cy + 9, 32, 8))

    desenhar_ficha_de_poker(cx, cy - 6 + flutuar, 20, ficha["cor"], achatar=0.55, espessura=6, valor=ficha["valor"])


# Desenha uma ficha vista de cima + número (usado no placar e na loja)
def desenhar_contador_de_fichas(valor, x, y):
    desenhar_ficha_de_poker(x, y, 16, FICHA_VERMELHA)
    imagem = fonte_media.render(str(valor), True, BRANCO)
    janela.blit(imagem, imagem.get_rect(midleft=(x + 24, y + 1)))


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
    desenhar_explosoes()                                        # NOVO

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
    desenhar_hud_poderes()                                      # NOVO


# Caixinha preta meio transparente, para o placar aparecer em qualquer fundo
def desenhar_caixa_placar(x, y, largura, altura):
    caixa = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(caixa, (0, 0, 0, 140), caixa.get_rect(), border_radius=12)
    janela.blit(caixa, (x, y))


# Película escura por cima do jogo
def escurecer_tela():
    pelicula = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pelicula.fill((0, 0, 0, 170))      # o 4º número é a transparência (0 a 255)
    janela.blit(pelicula, (0, 0))


# NOVO: ícone de cada poder (desenhado com formas)
def desenhar_icone_poder(id_poder, cx, cy):
    if id_poder == "salto":
        # Duas setinhas para cima, uma em cima da outra
        for subir in (0, 10):
            pygame.draw.lines(janela, VERDE_OK, False,
                              [(cx - 10, cy + 6 - subir), (cx, cy - 4 - subir), (cx + 10, cy + 6 - subir)], 4)
    else:
        # Uma "explosão": círculo laranja com raios em volta
        for i in range(8):
            angulo = i * math.pi / 4
            ponta = (cx + math.cos(angulo) * 15, cy + math.sin(angulo) * 15)
            pygame.draw.line(janela, DOURADO, (cx, cy), ponta, 3)
        pygame.draw.circle(janela, LARANJA, (cx, cy), 8)


# NOVO: anéis que crescem e somem quando o Quebra-Tudo é usado
def desenhar_explosoes():
    for explosao in explosoes:
        progresso = explosao["tempo"] / 0.4                  # vai de 0 a 1 em 0.4 segundo
        raio = 10 + progresso * RAIO_QUEBRA
        centro = (explosao["x"], explosao["y"] - camera_y)
        pygame.draw.circle(janela, LARANJA, centro, raio, 6)
        pygame.draw.circle(janela, DOURADO, centro, raio * 0.6, 3)


# NOVO: cargas de poder no canto de baixo da tela, durante a rodada
def desenhar_hud_poderes():
    desenhar_caixa_placar(10, ALTURA - 60, 330, 50)
    for i, poder in enumerate(PODERES):
        x = 40 + i * 165
        desenhar_icone_poder(poder["id"], x, ALTURA - 35)
        tecla = "SHIFT" if poder["id"] == "salto" else "E"
        cor = BRANCO if cargas[poder["id"]] > 0 else CINZA    # cinza = acabou
        texto = fonte_pequena.render(f"{tecla}  x{cargas[poder['id']]}", True, cor)
        janela.blit(texto, texto.get_rect(midleft=(x + 22, ALTURA - 34)))


# Tela de GAME OVER
def desenhar_game_over():
    escurecer_tela()
    escrever("GAME OVER", fonte_enorme, VERMELHO, LARGURA / 2, ALTURA / 2 - 110)
    escrever(motivo_derrota, fonte_media, BRANCO, LARGURA / 2, ALTURA / 2 - 40)
    escrever(f"Pontos: {pontos}    Recorde: {recorde}", fonte_media, DOURADO, LARGURA / 2, ALTURA / 2 + 15)
    escrever(f"Fichas nesta rodada: +{fichas_na_rodada}", fonte_media, BRANCO, LARGURA / 2, ALTURA / 2 + 60)
    escrever("Aperte ESPAÇO para voltar à loja", fonte_pequena, CINZA, LARGURA / 2, ALTURA / 2 + 120)


# Painel com moldura e título
def desenhar_painel(painel, titulo, cor_borda=DOURADO):
    pygame.draw.rect(janela, PAINEL, painel, border_radius=16)
    pygame.draw.rect(janela, cor_borda, painel, 3, border_radius=16)   # borda
    escrever(titulo, fonte_media, cor_borda, painel.centerx, painel.top + 35)


# A vitrine de skins (painel da esquerda da loja)
def desenhar_vitrine_de_skins(painel):
    skin = SKINS[skin_na_vitrine]
    raridade = RARIDADES[skin["raridade"]]
    desenhar_painel(painel, "SKINS", raridade["cor"])   # moldura da cor da raridade

    tempo = pygame.time.get_ticks() / 1000
    centro_personagem = (painel.centerx, painel.top + 130)

    # Skin lendária ganha um brilho laranja pulsando atrás dela
    if skin["raridade"] == "lendario":
        brilho = pygame.Surface((180, 180), pygame.SRCALPHA)
        forca = 60 + 40 * math.sin(tempo * 3)           # vai de 20 a 100 (transparência)
        for raio, transparencia in ((85, forca * 0.4), (65, forca * 0.7), (45, forca)):
            pygame.draw.circle(brilho, (*raridade["cor"], int(transparencia)), (90, 90), raio)
        janela.blit(brilho, brilho.get_rect(center=centro_personagem))

    # 1) O personagem, pulando sem parar, desenhado numa imagem pequena e AMPLIADO
    arco = abs(math.sin(tempo * 4))
    imagem = pygame.Surface((TAMANHO_CASA, TAMANHO_CASA + 30), pygame.SRCALPHA)   # fundo transparente
    desenhar_personagem(imagem, skin, 0, 30, arco * 14, arco * 5, cor_sombra=PRETO)
    imagem = pygame.transform.scale(imagem, (imagem.get_width() * 2, imagem.get_height() * 2))
    janela.blit(imagem, imagem.get_rect(center=centro_personagem))

    # 2) Setinhas para os lados
    escrever("<", fonte_grande, DOURADO, painel.left + 35, painel.top + 140)
    escrever(">", fonte_grande, DOURADO, painel.right - 35, painel.top + 140)

    # 3) Nome
    escrever(skin["nome"], fonte_media, BRANCO, painel.centerx, painel.top + 222)

    # 4) Etiqueta da raridade (um retângulo colorido com o nome dentro)
    texto = fonte_raridade.render(raridade["nome"], True, BRANCO)
    etiqueta = texto.get_rect(center=(painel.centerx, painel.top + 252)).inflate(18, 6)
    pygame.draw.rect(janela, raridade["cor"], etiqueta, border_radius=8)
    janela.blit(texto, texto.get_rect(center=etiqueta.center))

    # 5) Situação: em uso / já comprada / preço
    if skin_na_vitrine == skin_equipada:
        escrever("EM USO", fonte_pequena, VERDE_OK, painel.centerx, painel.top + 278)
    elif skin["nome"] in skins_compradas:
        escrever("ENTER para usar", fonte_pequena, BRANCO, painel.centerx, painel.top + 278)
    else:
        cor = DOURADO if carteira >= skin["preco"] else CINZA   # cinza = não dá para comprar
        escrever(f"{skin['preco']} fichas - ENTER compra", fonte_pequena, cor, painel.centerx, painel.top + 278)

    # 6) Bolinhas mostrando em qual skin da lista você está (na cor da raridade de cada uma)
    for i in range(len(SKINS)):
        x = painel.centerx + (i - (len(SKINS) - 1) / 2) * 16
        cor = RARIDADES[SKINS[i]["raridade"]]["cor"]
        pygame.draw.circle(janela, cor, (x, painel.top + 298), 5 if i == skin_na_vitrine else 2)


# NOVO: o painel de poderes (lado direito da loja)
def desenhar_painel_de_poderes(painel):
    desenhar_painel(painel, "PODERES")
    escrever("valem para a próxima rodada", fonte_raridade, CINZA, painel.centerx, painel.top + 63)

    for i, poder in enumerate(PODERES):
        caixa = pygame.Rect(painel.left + 15, painel.top + 85 + i * 108, painel.width - 30, 98)
        pygame.draw.rect(janela, FUNDO_LOJA, caixa, border_radius=10)

        desenhar_icone_poder(poder["id"], caixa.left + 30, caixa.top + 30)
        texto = fonte_pequena.render(poder["nome"], True, BRANCO)
        janela.blit(texto, texto.get_rect(midleft=(caixa.left + 55, caixa.top + 22)))
        texto = fonte_raridade.render(poder["descricao"], True, CINZA)
        janela.blit(texto, texto.get_rect(midleft=(caixa.left + 55, caixa.top + 46)))

        # Quantas cargas já estão guardadas, em bolinhas
        guardadas = poderes_guardados[poder["id"]]
        for carga in range(MAX_CARGAS):
            cor = VERDE_OK if carga < guardadas else PAINEL
            pygame.draw.circle(janela, cor, (caixa.left + 22 + carga * 16, caixa.bottom - 20), 6)

        # Tecla e preço
        if guardadas >= MAX_CARGAS:
            texto = fonte_raridade.render("CHEIO", True, VERDE_OK)
        else:
            cor = DOURADO if carteira >= poder["preco"] else CINZA
            texto = fonte_raridade.render(f"[{poder['tecla_compra']}]  {poder['preco']} fichas", True, cor)
        janela.blit(texto, texto.get_rect(midright=(caixa.right - 12, caixa.bottom - 20)))


# Tela da LOJA
def desenhar_loja():
    janela.fill(FUNDO_LOJA)

    escrever("LOJA", fonte_enorme, DOURADO, LARGURA / 2, 60)

    # Carteira: quantas fichas o jogador tem para gastar
    desenhar_contador_de_fichas(carteira, LARGURA / 2 - 30, 125)

    # Dois painéis: um para skins, outro para poderes
    desenhar_vitrine_de_skins(pygame.Rect(60, 165, 320, 310))
    desenhar_painel_de_poderes(pygame.Rect(420, 165, 320, 310))      # NOVO

    # Mensagem rápida (some sozinha depois de um tempinho)
    if tempo_mensagem > 0:
        escrever(mensagem_loja, fonte_pequena, DOURADO, LARGURA / 2, 498)

    escrever("Aperte ESPAÇO para jogar", fonte_media, BRANCO, LARGURA / 2, 540)
    escrever("<- -> skin    ENTER compra/usa skin    1 / 2 compra poder", fonte_pequena, CINZA, LARGURA / 2, 578)

tempo_queda = 0
rodando = True

while rodando:
    dt = relogio.tick(60) / 1000   # segundos desde o último quadro

    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            salvar_progresso()         # salva antes de fechar
            rodando = False

        if evento.type != pygame.KEYDOWN:
            continue                   # daqui pra baixo só nos interessam teclas

        # Cada tela responde às teclas de um jeito
        if estado == "loja":
            # Setas trocam a skin da vitrine (o % faz dar a volta na lista)
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                skin_na_vitrine = (skin_na_vitrine - 1) % len(SKINS)
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                skin_na_vitrine = (skin_na_vitrine + 1) % len(SKINS)

            # ENTER compra (se ainda não tem) ou passa a usar (se já tem)
            elif evento.key == pygame.K_RETURN:
                skin = SKINS[skin_na_vitrine]
                if skin["nome"] in skins_compradas:
                    skin_equipada = skin_na_vitrine
                    mensagem_loja = f"Usando: {skin['nome']}"
                elif carteira >= skin["preco"]:
                    carteira -= skin["preco"]
                    skins_compradas.append(skin["nome"])
                    skin_equipada = skin_na_vitrine
                    mensagem_loja = f"Comprado: {skin['nome']}!"
                else:
                    falta = skin["preco"] - carteira
                    mensagem_loja = f"Faltam {falta} fichas para comprar essa skin"
                tempo_mensagem = 2             # a mensagem fica 2 segundos na tela
                salvar_progresso()

            # NOVO: teclas 1 e 2 compram uma carga de poder
            elif evento.key in (pygame.K_1, pygame.K_2, pygame.K_KP1, pygame.K_KP2):
                if evento.key in (pygame.K_1, pygame.K_KP1):
                    poder = PODERES[0]
                else:
                    poder = PODERES[1]

                if poderes_guardados[poder["id"]] >= MAX_CARGAS:
                    mensagem_loja = f"Você já tem o máximo de {poder['nome']}"
                elif carteira >= poder["preco"]:
                    carteira -= poder["preco"]
                    poderes_guardados[poder["id"]] += 1
                    mensagem_loja = f"+1 {poder['nome']} para a próxima rodada!"
                else:
                    falta = poder["preco"] - carteira
                    mensagem_loja = f"Faltam {falta} fichas para esse poder"
                tempo_mensagem = 2
                salvar_progresso()

            elif evento.key == pygame.K_SPACE:
                # Começa uma rodada nova: jogador no início...
                jogador_linha = 0
                jogador_x = (COLUNAS // 2) * TAMANHO_CASA
                jogador_y = jogador_linha * TAMANHO_CASA
                pulando = False
                pontos = 0
                fichas_na_rodada = 0
                caiu_no_rio = False
                salto_duplo = False

                # NOVO: os poderes guardados viram as cargas desta rodada
                cargas = dict(poderes_guardados)          # dict(...) faz uma CÓPIA
                poderes_guardados = {"salto": 0, "quebra": 0}
                explosoes = []
                salvar_progresso()

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
                salvar_progresso()     # guarda as fichas e o recorde da rodada
                skin_na_vitrine = skin_equipada
                estado = "loja"

        # NOVO: tecla E usa o Quebra-Tudo (funciona até no meio do pulo)
        elif estado == "jogando" and evento.key == pygame.K_e:
            if cargas["quebra"] > 0:
                cargas["quebra"] -= 1
                centro_x = jogador_x + TAMANHO_CASA / 2
                centro_y = jogador_y + TAMANHO_CASA / 2

                # Mantém só o que está LONGE do jogador (math.dist = distância entre dois pontos)
                garcons = [g for g in garcons
                           if math.dist((g["x"] + LARGURA_GARCOM / 2, g["linha"] * TAMANHO_CASA + TAMANHO_CASA / 2),
                                        (centro_x, centro_y)) > RAIO_QUEBRA]
                maquinas = [m for m in maquinas
                            if math.dist((m["coluna"] * TAMANHO_CASA + TAMANHO_CASA / 2, m["linha"] * TAMANHO_CASA + TAMANHO_CASA / 2),
                                         (centro_x, centro_y)) > RAIO_QUEBRA]
                explosoes.append({"x": centro_x, "y": centro_y, "tempo": 0})

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

            # NOVO: SHIFT apertado + tem carga de Salto Duplo -> anda 2 casas
            shift_apertado = pygame.key.get_mods() & pygame.KMOD_SHIFT
            usando_salto_duplo = shift_apertado and cargas["salto"] > 0 and (dx != 0 or dy != 0)
            if usando_salto_duplo:
                dx *= 2
                dy *= 2

            # Não deixa voltar para baixo da tela
            nova_linha = min(jogador_linha + dy, linha_da_base_da_tela())

            # Onde ele vai cair no eixo x
            if faixas.get(nova_linha) == "caipirinha":
                # No rio: anda uma casa a partir de onde está (sem "encaixar" na coluna)
                novo_x = jogador_x + dx * TAMANHO_CASA
            else:
                # No chão: encaixa na coluna mais próxima
                novo_x = (round(jogador_x / TAMANHO_CASA) + dx) * TAMANHO_CASA

            # Não deixa sair pelos lados
            novo_x = max(0, min(novo_x, (COLUNAS - 1) * TAMANHO_CASA))

            # Tem uma máquina de fliperama lá? Então não pula (fica onde está)
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

                # NOVO: o salto duplo é mais alto e mais demorado (e gasta uma carga)
                salto_duplo = usando_salto_duplo
                if salto_duplo:
                    cargas["salto"] -= 1
                    duracao_pulo = DURACAO_SALTO_DUPLO
                    altura_pulo = ALTURA_SALTO_DUPLO
                else:
                    duracao_pulo = DURACAO_PULO
                    altura_pulo = ALTURA_PULO

    # O relógio da mensagem da loja vai diminuindo até sumir
    tempo_mensagem -= dt

    # --- Atualização (só quando está jogando) ---
    altura_no_ar = 0
    esticar = 0
    if estado == "jogando":
        # Pulo
        if pulando:
            tempo_pulo += dt
            progresso = min(tempo_pulo / duracao_pulo, 1)   # vai de 0 (início) a 1 (fim)

            # Anda da casa de origem até a de destino
            jogador_x = origem_x + (destino_x - origem_x) * progresso
            jogador_y = origem_y + (destino_y - origem_y) * progresso

            # Sobe e desce em arco: sin vai de 0 -> 1 -> 0
            arco = math.sin(progresso * math.pi)
            altura_no_ar = arco * altura_pulo
            esticar = arco * 6

            if progresso >= 1:
                pulando = False
                salto_duplo = False

        # NOVO: as explosões do Quebra-Tudo crescem e somem depois de 0.4 segundo
        for explosao in explosoes:
            explosao["tempo"] += dt
        explosoes = [e for e in explosoes if e["tempo"] < 0.4]

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

        # Pegar fichas (basta passar pela casa dela, até no meio do pulo)
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

        # Colisão com os garçons (NOVO: no salto duplo o jogador passa por cima deles)
        for garcom in garcons:
            if salto_duplo:
                break
            if estado == "jogando" and hitbox_jogador().colliderect(hitbox_garcom(garcom)):
                estado = "game_over"
                motivo_derrota = "Esbarrou no garçom!"
                pulando = False

    # --- Desenho: cada tela desenha uma coisa ---
    if estado != "game_over":
        tempo_queda = 0

    if estado == "loja":
        desenhar_loja()

    elif estado == "jogando":
        desenhar_jogo(altura_no_ar, esticar)

    elif estado == "game_over":
        if caiu_no_rio:
            tempo_queda += dt

        desenhar_jogo(0, 0)

        # Espera a animação terminar para mostrar o game over
        if not caiu_no_rio or tempo_queda >= 1.1:
            desenhar_game_over()
    pygame.display.update()

pygame.quit()