import pygame
import math
import random
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA, ALTURA = 1000, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Arremesso Oblíquo com Alvo")
relogio = pygame.time.Clock()

# Cores (RGB)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
AMARELO = (255, 215, 0)

# Constantes da Física do Jogo
GRAVIDADE = 0.5  

# --- NOVAS VARIÁVEIS PARA A RESISTÊNCIA DO AR ---
resistencia_ativada = True
FATOR_ARRASTO = 0.005  # Controla a força do ar (valores menores = menos resistência)

# Variáveis do Canhão
canhon_x = 50
canhon_y = ALTURA - 50

# Parâmetros de Lançamento Iniciais
angulo = 45        
velocidade = 15     

# Estado da Bola
bola_x = canhon_x
bola_y = canhon_y
vel_x = 0
vel_y = 0
em_movimento = False
trajetoria = []  

# --- VARIÁVEIS: ALVO E PONTUAÇÃO ---
alvo_largura = 40
alvo_altura = 15
# Reposiciona o alvo aleatoriamente na metade direita da tela, em cima do chão
alvo_x = random.randint(400, LARGURA - alvo_largura)
alvo_y = ALTURA - 50  # Alinhado com o topo do chão
pontos = 0

fonte = pygame.font.SysFont("Arial", 20)
fonte_placar = pygame.font.SysFont("Arial", 24, bold=True)

# Loop Principal do Jogo
rodando = True
while rodando:
    tela.fill(BRANCO)
    
    # Desenha o Chão
    pygame.draw.rect(tela, VERDE, (0, ALTURA - 50, LARGURA, 50))
    
    # Captura de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            pygame.quit()
            sys.exit()
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not em_movimento:
                angulo_rad = math.radians(angulo)
                vel_x = velocidade * math.cos(angulo_rad)
                vel_y = -velocidade * math.sin(angulo_rad) 
                em_movimento = True
                trajetoria = []
            
            # --- INTERRUPTOR DA RESISTÊNCIA DO AR ---
            if evento.key == pygame.K_r:
                resistencia_ativada = not resistencia_ativada

    # Ajustes de ângulo e força
    teclas = pygame.key.get_pressed()
    if not em_movimento:
        if teclas[pygame.K_UP] and angulo < 90:
            angulo += 1
        if teclas[pygame.K_DOWN] and angulo > 0:
            angulo -= 1
        if teclas[pygame.K_RIGHT] and velocidade < 30:
            velocidade += 0.2
        if teclas[pygame.K_LEFT] and velocidade > 5:
            velocidade -= 0.2

    # Atualização da Física e Detecção de Colisão
    if em_movimento:
        # --- CÁLCULO DA RESISTÊNCIA DO AR ---
        if resistencia_ativada:
            # Velocidade total atual da bola (vetor)
            vel_total = math.sqrt(vel_x**2 + vel_y**2)
            
            # Força de arrasto proporcional ao quadrado da velocidade
            forca_arrasto = 0.5 * FATOR_ARRASTO * (vel_total**2)
            
            # Evita divisão por zero caso a bola pare no ar
            if vel_total != 0:
                # Aplica a perda de velocidade de forma contrária ao movimento atual
                vel_x -= (vel_x / vel_total) * forca_arrasto
                vel_y -= (vel_y / vel_total) * forca_arrasto

        # Física padrão (Gravidade e Posição)
        bola_x += vel_x
        vel_y += GRAVIDADE
        bola_y += vel_y
        trajetoria.append((int(bola_x), int(bola_y)))
        
        # 1. DETECÇÃO DE ACERTO NO ALVO (Colisão da Bola com o Retângulo do Alvo)
        if (alvo_x <= bola_x <= alvo_x + alvo_largura) and (alvo_y - 10 <= bola_y <= alvo_y + alvo_altura):
            pontos += 1
            # Sorteia uma nova posição para o alvo
            alvo_x = random.randint(300, LARGURA - alvo_largura)
            # Reseta a bola
            em_movimento = False
            bola_x = canhon_x
            bola_y = canhon_y
            trajetoria = []
            
        # 2. Condição de parada padrão (se errar o alvo e tocar no chão/sair da tela)
        elif bola_y >= ALTURA - 50 or bola_x > LARGURA or bola_x < 0:
            em_movimento = False
            bola_x = canhon_x
            bola_y = canhon_y

    # --- RENDERIZAÇÃO ---
    
    # Desenha o Alvo
    pygame.draw.rect(tela, VERMELHO, (alvo_x, alvo_y, alvo_largura, alvo_altura))
    pygame.draw.rect(tela, AMARELO, (alvo_x + 10, alvo_y, alvo_largura - 20, alvo_altura))
    
    # Desenha a Trajetória anterior
    for ponto in trajetoria:
        pygame.draw.circle(tela, PRETO, ponto, 2)
        
    # Desenha a Linha de Mira
    mira_x = canhon_x + 40 * math.cos(math.radians(angulo))
    mira_y = canhon_y - 40 * math.sin(math.radians(angulo))
    pygame.draw.line(tela, VERMELHO, (canhon_x, canhon_y), (mira_x, mira_y), 5)
    
    # Desenha a Bola
    if em_movimento:
        pygame.draw.circle(tela, AZUL, (int(bola_x), int(bola_y)), 10)
    else:
        pygame.draw.circle(tela, AZUL, (canhon_x, canhon_y), 10)
        
    # Textos da Interface
    txt_angulo = fonte.render(f"Ângulo: {angulo}° (Setas Cima/Baixo)", True, PRETO)
    txt_velocidade = fonte.render(f"Velocidade: {velocidade:.1f} (Setas Esq/Dir)", True, PRETO)
    txt_instrucoes = fonte.render("ESPAÇO: Atirar", True, PRETO)
    
    # --- TEXTO DO STATUS DA RESISTÊNCIA ---
    status_ar = "ATIVADA" if resistencia_ativada else "DESATIVADA"
    cor_status = VERDE if resistencia_ativada else VERMELHO
    txt_resistencia = fonte.render(f"Resistência do Ar [Tecla R]: {status_ar}", True, cor_status)
    
    # Exibe o Placar de Pontos
    txt_placar = fonte_placar.render(f"PONTOS: {pontos}", True, AZUL)
    
    tela.blit(txt_angulo, (20, 20))
    tela.blit(txt_velocidade, (20, 50))
    tela.blit(txt_instrucoes, (20, 80))
    tela.blit(txt_resistencia, (20, 110)) # Nova linha de texto
    tela.blit(txt_placar, (LARGURA - 160, 20)) 
    
    pygame.display.flip()
    relogio.tick(60)
