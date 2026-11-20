"""Interface Pygame para Campo Minado de Cálculo.

Controles: clique esquerdo abre/responde; clique direito marca bandeira;
teclado na questão; Enter confirma; Esc volta ao menu.
"""
import sys
import pygame

from game_logic import DIFICULDADES, JogoCalculo, NOMES_TOPICO, TOPICOS, Estado

pygame.init()
pygame.display.set_caption("Campo Minado de Cálculo")
W, H = 900, 720
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
clock = pygame.time.Clock()

BG = (25, 29, 47)
PANEL = (39, 45, 69)
INK = (247, 240, 230)
MUTED = (183, 192, 211)
PINK = (255, 142, 180)
GOLD = (255, 211, 105)
MINT = (137, 230, 195)
RED = (255, 112, 126)
CELL = (80, 95, 132)
OPEN = (225, 228, 239)
NUMCOL = [(0,0,0), (70,115,220), (35,145,83), (222,74,76), (113,75,179), (173,94,49), (35,157,165), (54,59,70), (100,100,100)]
font = pygame.font.SysFont("dejavusans", 22, bold=True)
small = pygame.font.SysFont("dejavusans", 16)
big = pygame.font.SysFont("dejavusans", 40, bold=True)

TOPIC_OPTIONS = [("Misto", "misto"), ("Funções", "funcao"), ("Limites", "limite"), ("Derivadas", "derivada"), ("Integrais", "integral")]
DIFF_OPTIONS = [("Fácil", "1"), ("Médio", "2"), ("Difícil", "3")]
screen_mode = "menu"
topic_i = 0
diff_i = 0
game = None
question_pos = None
answer = ""
notice = ""
notice_until = 0

def label(text, x, y, f=font, color=INK, center=False):
    surf = f.render(str(text), True, color)
    rect = surf.get_rect(center=(x,y)) if center else surf.get_rect(topleft=(x,y))
    screen.blit(surf, rect)
    return rect

def rounded(rect, color, radius=14, outline=None, width=2):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    if outline:
        pygame.draw.rect(screen, outline, rect, width, border_radius=radius)

def button(rect, text, selected=False):
    rounded(rect, PINK if selected else PANEL, 16, GOLD if selected else None, 3 if selected else 0)
    label(text, rect.centerx, rect.centery, font, BG if selected else INK, True)

def start_game():
    global game, screen_mode
    _, rows, cols, mines = DIFICULDADES[DIFF_OPTIONS[diff_i][1]]
    game = JogoCalculo(rows, cols, mines, TOPIC_OPTIONS[topic_i][1])
    screen_mode = "game"

def board_rect():
    return pygame.Rect(30, 150, W-60, H-190)

def draw_menu():
    label("✦", 80, 58, big, GOLD)
    label("CAMPO MINADO", W//2, 102, big, INK, True)
    label("de cálculo", W//2, 147, font, PINK, True)
    label("Escolha um tema", W//2, 218, font, MUTED, True)
    bw, gap = min(150, (W-80)//5), 12
    total = bw*5+gap*4
    x0 = (W-total)//2
    for i,(name,_) in enumerate(TOPIC_OPTIONS):
        button(pygame.Rect(x0+i*(bw+gap), 250, bw, 54), name, i==topic_i)
    label("Dificuldade", W//2, 360, font, MUTED, True)
    for i,(name,_) in enumerate(DIFF_OPTIONS):
        button(pygame.Rect(W//2-240+i*165, 390, 150, 54), name, i==diff_i)
    button(pygame.Rect(W//2-130, 500, 260, 68), "JOGAR  ▶", True)
    label("Clique numa casa para abrir · botão direito para bandeira", W//2, 610, small, MUTED, True)

def draw_board():
    rounded(pygame.Rect(20, 18, W-40, 112), PANEL, 22)
    label("CAMPO MINADO", 42, 35, font, PINK)
    label(f"♥ {max(game.vidas,0)}   ⚑ {game.campo.minas_restantes}   ✓ {game.acertos}", 42, 77, font, INK)
    label(f"{TOPIC_OPTIONS[topic_i][0]} · {DIFF_OPTIONS[diff_i][0]}", W-42, 58, small, MUTED)
    area = board_rect()
    cols, rows = game.campo.colunas, game.campo.linhas
    cell = min((area.width-20)//cols, (area.height-20)//rows, 58)
    gap = 5
    totalw = cols*cell+(cols-1)*gap
    totalh = rows*cell+(rows-1)*gap
    x0, y0 = (W-totalw)//2, 145+(H-190-totalh)//2
    for r in range(rows):
        for c in range(cols):
            x,y=x0+c*(cell+gap),y0+r*(cell+gap)
            cel=game.campo.tabuleiro[r][c]
            opened=cel.aberta
            rounded(pygame.Rect(x,y,cell,cell), OPEN if opened else CELL, max(5,cell//5), (255,255,255,35) if not opened else None, 1)
            sym=game.simbolo(r,c)
            if sym=="F":
                label("⚑", x+cell//2,y+cell//2,font, PINK,True)
            elif sym=="*":
                label("✹", x+cell//2,y+cell//2,font, RED,True)
            elif sym in ("?",) or sym.isdigit():
                color=GOLD if sym=="?" else NUMCOL[min(int(sym),8)]
                label(sym,x+cell//2,y+cell//2,font,color if sym=="?" else color,True)
    if game.terminou:
        rounded(pygame.Rect(W//2-205,H//2-86,410,172),PANEL,24,GOLD,3)
        won=game.estado==Estado.VITORIA
        label("VOCÊ CONSEGUIU!" if won else "FIM DE JOGO", W//2,H//2-34,big,MINT if won else RED,True)
        label("Clique para voltar ao início",W//2,H//2+27,small,MUTED,True)

def draw_question():
    draw_board()
    r,c=question_pos
    q=game.pergunta(r,c)
    rect=pygame.Rect(70,H//2-130,W-140,260)
    rounded(rect,PANEL,24,GOLD,3)
    label(NOMES_TOPICO[q.topico],W//2,rect.y+38,font,PINK,True)
    words=q.enunciado.split()
    lines=[]; line=""
    for word in words:
        if font.size(line+" "+word)[0]>W-210 and line:
            lines.append(line); line=word
        else: line=(line+" "+word).strip()
    if line: lines.append(line)
    for i,s in enumerate(lines[:3]): label(s,W//2,rect.y+84+i*31,small,INK,True)
    pygame.draw.rect(screen,(25,29,47),pygame.Rect(W//2-150,rect.y+170,300,48),border_radius=12)
    label(answer or "Resposta...",W//2,rect.y+194,font, GOLD if answer else MUTED,True)
    label("Digite e pressione Enter  ·  Esc cancela",W//2,rect.bottom-18,small,MUTED,True)

def tell(text):
    global notice,notice_until
    notice=text; notice_until=pygame.time.get_ticks()+2200

running=True
while running:
    W,H=screen.get_size()
    screen.fill(BG)
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        elif screen_mode=="menu":
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                x,y=event.pos
                bw=min(150,(W-80)//5); gap=12; x0=(W-(bw*5+gap*4))//2
                if 250<=y<=304:
                    for i in range(5):
                        if x0+i*(bw+gap)<=x<=x0+i*(bw+gap)+bw: topic_i=i
                elif 390<=y<=444:
                    for i in range(3):
                        if W//2-240+i*165<=x<=W//2-90+i*165: diff_i=i
                elif W//2-130<=x<=W//2+130 and 500<=y<=568: start_game()
            elif event.type==pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN,pygame.K_SPACE): start_game()
                elif event.key==pygame.K_LEFT: topic_i=(topic_i-1)%5
                elif event.key==pygame.K_RIGHT: topic_i=(topic_i+1)%5
        elif screen_mode=="game":
            if question_pos:
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE: question_pos=None; answer=""
                    elif event.key==pygame.K_RETURN:
                        ok,q=game.responder(*question_pos,answer)
                        tell("Resposta certa!" if ok else f"Resposta: {q.resposta} · {q.passos.replace(chr(10),' ')}")
                        question_pos=None; answer=""
                    elif event.key==pygame.K_BACKSPACE: answer=answer[:-1]
                    elif event.unicode and (event.unicode.isdigit() or event.unicode in ".,-/") and len(answer)<16: answer+=event.unicode
            elif event.type==pygame.MOUSEBUTTONDOWN:
                if game.terminou:
                    screen_mode="menu"
                else:
                    area=board_rect(); rows,cols=game.campo.linhas,game.campo.colunas
                    cell=min((area.width-20)//cols,(area.height-20)//rows,58); gap=5
                    x0=(W-(cols*cell+(cols-1)*gap))//2; y0=145+(H-190-(rows*cell+(rows-1)*gap))//2
                    c=(event.pos[0]-x0)//(cell+gap); r=(event.pos[1]-y0)//(cell+gap)
                    if 0<=r<rows and 0<=c<cols and 0<=event.pos[0]-x0<cols*(cell+gap) and 0<=event.pos[1]-y0<rows*(cell+gap):
                        if event.button==3: game.marcar(r,c)
                        elif event.button==1:
                            if game.pendente(r,c): question_pos=(r,c); answer=""
                            elif not game.campo.tabuleiro[r][c].aberta:
                                game.abrir(r,c)
                                pend=game.pendentes()
                                if pend: question_pos=pend[0]; answer=""
        
    if screen_mode=="menu": draw_menu()
    else:
        draw_question() if question_pos else draw_board()
    if notice and pygame.time.get_ticks()<notice_until:
        rounded(pygame.Rect(24,H-48,W-48,34),PANEL,10)
        label(notice[:110],W//2,H-31,small,GOLD,True)
    pygame.display.flip(); clock.tick(60)
pygame.quit(); sys.exit()
