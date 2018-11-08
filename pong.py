################################################################################
# GRAFICKA HRA PONG
################################################################################

# importovani knihovny pro praci s grafikou
import pygame
# importovani knihovny pro praci se systemem
import sys
# importovani vsech soucasti pygame.locals
from pygame.locals import *

################################################################################
# Parametry aplikace
################################################################################

rozliseni_okna = (640, 480)
titulek_okna = 'Pong'

barva_pozadi = (255, 255, 255)
barva_palky = (0, 0, 0)

sirka_palky = 15
vyska_palky = 75

pozice_x_palky = 30
pozice_y_palky = rozliseni_okna[1] / 2

################################################################################
# Pomocne podprogramy
################################################################################

def zpracovani_udalosti():
    # prochazeni vsech udalosti, na ktere se da reagovat
    for event in pygame.event.get():
        # pokud je nalezena udalost typu QUIT...
        if event.type == QUIT:
            # okno se zavre
            pygame.quit()
            # aplikace skonci
            sys.exit()

def vykreslovaci_operace():
    # vyplneni okna barvou (pozadi)
    okno.fill(barva_pozadi)
    # vykresleni palky
    x = pozice_x_palky - sirka_palky / 2
    y = pozice_y_palky - vyska_palky / 2
    pygame.draw.rect(okno, barva_palky, (x, y, sirka_palky, vyska_palky))
    
################################################################################
# Inicializace
################################################################################

# inicializace knihovny Pygame
pygame.init()
# nastaveni velikosti okna
okno = pygame.display.set_mode(rozliseni_okna)
# nastaveni titulku okna
pygame.display.set_caption(titulek_okna)

################################################################################
# Nekonecna vykreslovaci smycka
################################################################################

while True:
    zpracovani_udalosti()
    vykreslovaci_operace()

    # prekresleni okna
    pygame.display.update()