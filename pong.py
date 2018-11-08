# importuji knihovny pro usnadneni prace
import pygame
import sys
# importuji se vsechny soucasti pygame.locals
from pygame.locals import *

# inicializace knihovny Pygame
pygame.init()

# nastaveni rezimu okna
window = pygame.display.set_mode((640, 480))
# nastaveni titulku okna
pygame.display.set_caption('Pong')

# nekonecna vykreslovaci smycka
while True:
    # prochazeni vsech udalosti, na ktere se da reagovat
    for event in pygame.event.get():
        # pokud je nalezena udalost typu QUIT...
        if event.type == QUIT:
            # aplikace konci
            pygame.quit()
            sys.exit()
    
    # zde budou vsechny vykreslovaci operace...
    
    # vyplneni okna barvou pozadi
    window.fill((255, 255, 255))
    
    # prekresleni okna
    pygame.display.update()