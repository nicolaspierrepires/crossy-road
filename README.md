# Jogo: Cassino Crossing

## Autores
- Arthur Camêlo
- Nicolas Pierre
- Pedro Brito

## Descrição do projeto
Cassino Crossing é um jogo inspirado no Crossy Road e ambientado em um cassino.

O objetivo é avançar o máximo possível, desviando dos garçons e atravessando rios de caipirinha sobre frutas em movimento. Durante o percurso, o jogador coleta fichas para comprar personagens e poderes na loja. A dificuldade aumenta conforme a pontuação.

O jogo possui loja, diferentes personagens, salto duplo, poder para destruir obstáculos, músicas, animações e sistema de pausa. O progresso é salvo automaticamente.

## Como executar
É necessário ter o Python e a biblioteca Pygame instalados.

Para instalar o Pygame, execute no terminal:

```bash
python -m pip install pygame
```

Depois, abra o terminal na pasta do projeto e execute:

```bash
python jogo.py
```

O arquivo principal que deve ser executado é `jogo.py`.

## Controles

### Durante a partida
- **Setas ou W, A, S, D:** mover o personagem.
- **Shift + direção:** usar o salto duplo, caso tenha cargas.
- **E:** usar o Quebra-Tudo, caso tenha cargas.
- **Espaço:** pausar ou continuar.

### Na loja
- **Setas para os lados ou A e D:** escolher um personagem.
- **Enter:** comprar ou equipar o personagem.
- **1:** comprar uma carga de Salto Duplo.
- **2:** comprar uma carga de Quebra-Tudo.
- **Espaço:** iniciar a partida.

### Após a derrota
- **Espaço:** voltar à loja.

## Link do vídeo do jogo
- https://www.youtube.com/watch?v=MemT-KGIm34