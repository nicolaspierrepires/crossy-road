import pygame

# 1. Liga o pygame (sempre a primeira coisa)
pygame.init()

# 2. Cria a janela: largura x altura, em pixels
LARGURA = 800
ALTURA = 600
janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cassino Crossing")

# 3. Relógio: controla a velocidade do jogo
relogio = pygame.time.Clock()

# 4. Loop principal: roda sem parar até o jogador fechar a janela
rodando = True
while rodando:
    # 4a. Eventos: o que o jogador fez (teclado, mouse, fechar a janela)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:   # clicou no X da janela
            rodando = False

    # 4b. Desenho: pinta o fundo de verde (feltro de mesa de cassino)
    janela.fill((20, 110, 60))

    # 4c. Mostra na tela o que foi desenhado
    pygame.display.update()

    # 4d. Limita o jogo a 60 quadros por segundo
    relogio.tick(60)

# 5. Saiu do loop: fecha o pygame
pygame.quit()