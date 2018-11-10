################################################################################
# GRAFICKA HRA PONG
################################################################################

# importovani knihovny pro praci s grafikou
import pygame
# importovani knihovny pro praci se systemem
import sys
# importovani vsech soucasti pygame.locals
from pygame.locals import *
from pygame.event import *

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

pohyb_palkou_nahoru = False
pohyb_palkou_dolu = False

pohyb_palkou_doprava = False
pohyb_palkou_doleva = False

rychlost_posunu_palky = 0.5

################################################################################
# Pomocne podprogramy
################################################################################

def zpracovani_udalosti():
    # podprogram pouziva promenne definovane vyse
    global pohyb_palkou_dolu, pohyb_palkou_nahoru
    global pohyb_palkou_doleva, pohyb_palkou_doprava
    
    # prochazeni vsech udalosti, na ktere se da reagovat
    for udalost in pygame.event.get():
        
        # pokud je nalezena udalost zavreni okna...
        if udalost.type == pygame.QUIT:
            # okno se zavre
            pygame.quit()
            # aplikace skonci
            sys.exit()
        
        # pokud je nalezena udalost stisku klavesy...
        if udalost.type == pygame.KEYDOWN:
            # pokud jde o sipku nahoru...
            if udalost.key == pygame.K_UP:
                pohyb_palkou_nahoru = True
            # pokud jde o sipku dolu...
            if udalost.key == pygame.K_DOWN:
                pohyb_palkou_dolu = True
            if udalost.key == pygame.K_LEFT:
                pohyb_palkou_doleva = True
            if udalost.key == pygame.K_RIGHT:
                pohyb_palkou_doprava = True
            
            # pokud jde o klavesu Escape...
            if udalost.key == pygame.K_ESCAPE:
                # okno se zavre
                pygame.quit()
                # aplikace skonci
                sys.exit()
                
        # pokud je nalezena udalost pusteni klavesy...
        if udalost.type == pygame.KEYUP:
            # pokud jde o sipku nahoru...
            if udalost.key == pygame.K_UP:
                pohyb_palkou_nahoru = False
            # pokud jde o sipku dolu...
            if udalost.key == pygame.K_DOWN:
                pohyb_palkou_dolu = False
            if udalost.key == pygame.K_LEFT:
                pohyb_palkou_doleva = False
            if udalost.key == pygame.K_RIGHT:
                pohyb_palkou_doprava = False

def vykreslovaci_operace():
    # vyplneni okna barvou (pozadi)
    okno.fill(barva_pozadi)
    
    # vykresleni palky
    x = pozice_x_palky - sirka_palky / 2
    y = pozice_y_palky - vyska_palky / 2
    pygame.draw.rect(okno, barva_palky, (x, y, sirka_palky, vyska_palky))
    
def pohyb_palky():
    # pouziva promennou definovanou vyse
    global pozice_y_palky, pozice_x_palky

    # pokud byl detekovan pohyb palkou dolu...
    if pohyb_palkou_dolu:
        # ...posune se palka smerem od horniho okraje
        pozice_y_palky += rychlost_posunu_palky
    
    # pokud byl detekovan pohyb palkou nahoru...
    if pohyb_palkou_nahoru:
        # ...posune se palka smerem k hornimu okraji
        pozice_y_palky -= rychlost_posunu_palky
    
    if pohyb_palkou_doprava:
        pozice_x_palky += rychlost_posunu_palky
    
    if pohyb_palkou_doleva:
        pozice_x_palky -= rychlost_posunu_palky
    
    # vypocty kolizi palky s okraji okna
    horni_okraj_okna = 0
    spodni_okraj_okna = rozliseni_okna[1]
    horni_okraj_palky = pozice_y_palky - vyska_palky / 2
    spodni_okraj_palky = pozice_y_palky + vyska_palky / 2
    
    # pokud horni okraj palky presahuje horni okraj okna...
    if horni_okraj_palky < horni_okraj_okna:
        # ...presune se palka tak, aby se hornim okrajem dotykala okraje okna
        pozice_y_palky = vyska_palky / 2
    
    # pokud spodni okraj palky presahuje spodni okraj okna...
    if spodni_okraj_palky > spodni_okraj_okna:
        # ...presune se palka tak, aby se spodnim okrajem dotykala okraje okna
        pozice_y_palky = rozliseni_okna[1] - vyska_palky / 2
    
    levy_okraj_okna = 0
    pravy_okraj_okna = rozliseni_okna[0]
    levy_okraj_palky = pozice_x_palky - sirka_palky / 2
    pravy_okraj_palky = pozice_x_palky + sirka_palky / 2
    
    if levy_okraj_palky < levy_okraj_okna:
        pozice_x_palky = levy_okraj_okna + sirka_palky / 2
    
    if pravy_okraj_palky > pravy_okraj_okna:
        pozice_x_palky = pravy_okraj_okna - sirka_palky / 2
    
def pohyb_micku():
    # placeholder pro pozdejsi doplneni
    pass
    
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
    # spusteni pomocnych podprogramu
    zpracovani_udalosti()
    pohyb_palky()
    pohyb_micku()
    vykreslovaci_operace()

    # prekresleni okna
    pygame.display.update()
    