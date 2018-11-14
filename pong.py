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
# Objektova reprezentace vykreslovaciho okna
################################################################################

class Okno:
    def __init__(self, titulek, rozliseni, barva_pozadi):
        self.titulek = titulek
        self.rozliseni = rozliseni
        self.barva_pozadi = barva_pozadi
        self.displej = None
    
    def vyhodnotit_reakce(self, udalosti):
        # prochazeni vsech udalosti, na ktere muze okno reagovat
        for udalost in pygame.event.get():
            # pokud je nalezena udalost typu zavreni okna...
            if udalost.type == pygame.QUIT:
                # okno se zavre
                pygame.quit()
                # aplikace skonci
                sys.exit()
            
            # pokud je nalezena udalost typu stisk klavesy...
            if udalost.type == pygame.KEYDOWN:
                # a pokud jde o klavesu Escape...
                if udalost.key == pygame.K_ESCAPE:
                    # okno se zavre
                    pygame.quit()
                    # aplikace skonci
                    sys.exit()

################################################################################
# Objektova reprezentace hracovy palky
################################################################################

class Palka:
    def __init__(self, okno, pozice_x, pozice_y, sirka, vyska, barva, rychlost, klavesa_nahoru, klavesa_dolu):
        self.okno = okno
        self.barva = barva
        self.rychlost = rychlost
        
        x = self.pozice_x = pozice_x
        y = self.pozice_y = pozice_y
        w = self.sirka = sirka
        h = self.vyska = vyska
        
        o = {'x': x - w / 2, 'y': y - (h - w) / 2, 'w': w, 'h': h - w}
        e1 = {'x': x - w / 2, 'y': y - h / 2, 'w': w, 'h': w}
        e2 = {'x': x - w / 2, 'y': y + h / 2 - w, 'w': w, 'h': w}
        
        self.tvary = {'obdelnik': o, 'horni_elipsa': e1, 'spodni_elipsa': e2}
        
        self.klavesa_nahoru = klavesa_nahoru
        self.klavesa_dolu = klavesa_dolu
        
        self.pohyb_nahoru = False
        self.pohyb_dolu = False
    
    def vyhodnotit_reakce(self, udalosti):
        # zpracovani udalosti
        for udalost in udalosti:
            # udalosti typu stisk klavesy
            if udalost.type == pygame.KEYDOWN:
                if udalost.key == self.klavesa_nahoru:
                    self.pohyb_nahoru = True
                if udalost.key == self.klavesa_dolu:
                    self.pohyb_dolu = True
            
            # udalosti typu pusteni klavesy
            if udalost.type == pygame.KEYUP:
                if udalost.key == self.klavesa_nahoru:
                    self.pohyb_nahoru = False
                if udalost.key == self.klavesa_dolu:
                    self.pohyb_dolu = False
    
    def pohnout(self):
        # posunuti palky
        if self.pohyb_dolu:
            self.pozice_y += self.rychlost
        
        if self.pohyb_nahoru:
            self.pozice_y -= self.rychlost
        
        # detekce kolizi s okraji okna
        horni_okraj_okna = 0
        spodni_okraj_okna = self.okno.rozliseni[1]
        horni_okraj_palky = self.pozice_y - self.vyska / 2
        spodni_okraj_palky = self.pozice_y + self.vyska / 2
        
        # pokud horni okraj palky presahuje horni okraj okna...
        if horni_okraj_palky < horni_okraj_okna:
            # ...presune se palka tak, aby se hornim okrajem dotykala okraje okna
            self.pozice_y = self.vyska / 2
        
        # pokud spodni okraj palky presahuje spodni okraj okna...
        if spodni_okraj_palky > spodni_okraj_okna:
            # ...presune se palka tak, aby se spodnim okrajem dotykala okraje okna
            self.pozice_y = self.okno.rozliseni[1] - self.vyska / 2
        
        # prepocitani pozice vsech casti palky
        x = self.pozice_x
        y = self.pozice_y
        w = self.sirka
        h = self.vyska
        
        self.tvary['obdelnik']['x'] = x - w / 2
        self.tvary['obdelnik']['y'] = y - (h - w) / 2
        
        self.tvary['horni_elipsa']['x'] = x - w / 2
        self.tvary['horni_elipsa']['y'] = y - h / 2
        
        self.tvary['spodni_elipsa']['x'] = x - w / 2
        self.tvary['spodni_elipsa']['y'] = y + h / 2 - w

    def vykreslit(self, cil):
        barva = self.barva
        
        x = self.tvary['obdelnik']['x']
        y = self.tvary['obdelnik']['y']
        w = self.tvary['obdelnik']['w']
        h = self.tvary['obdelnik']['h']
        pygame.draw.rect(cil, barva, (x, y, w, h))
        
        x = self.tvary['horni_elipsa']['x']
        y = self.tvary['horni_elipsa']['y']
        w = self.tvary['horni_elipsa']['w']
        h = self.tvary['horni_elipsa']['h']
        pygame.draw.ellipse(cil, barva, (x, y, w, h))
        
        x = self.tvary['spodni_elipsa']['x']
        y = self.tvary['spodni_elipsa']['y']
        w = self.tvary['spodni_elipsa']['w']
        h = self.tvary['spodni_elipsa']['h']
        pygame.draw.ellipse(cil, barva, (x, y, w, h))

################################################################################
# Objektova reprezentace hraciho micku
################################################################################

class Micek:
    def __init__(self):
        # placeholder pro pozdejsi doplneni
        pass

################################################################################
# Inicializace
################################################################################

# inicializace knihovny Pygame
pygame.init()

# vytvoreni vykreslovaciho okna
okno = Okno('Pong', (640, 480), (255, 255, 255))
# nastaveni titulku okna
pygame.display.set_caption(okno.titulek)
# nastaveni velikosti okna
okno.displej = pygame.display.set_mode(okno.rozliseni)

# nastaveni parametru hry
sirka_palky = 15
vyska_palky = 75
barva_palky = (0, 0, 0)
rychlost_palky = 0.5
offset_palky = 30

# vytvoreni palek
palky = []
palky.append(Palka(okno, offset_palky, okno.rozliseni[1] / 2, sirka_palky, vyska_palky, barva_palky, rychlost_palky, pygame.K_w, pygame.K_s))
palky.append(Palka(okno, okno.rozliseni[0] - offset_palky - sirka_palky, okno.rozliseni[1] / 2, sirka_palky, vyska_palky, barva_palky, rychlost_palky, pygame.K_UP, pygame.K_DOWN))

# vytvoreni micku
micky = []
# TO DO

################################################################################
# Pomocne podprogramy
################################################################################

def zpracovani_udalosti():
    # pouziva promenne definovane vyse
    global okno, palky
    
    # seznam udalosti, na ktere lze reagovat
    udalosti = pygame.event.get()
    
    # nejdrive zpracuje mozne reakce okno
    okno.vyhodnotit_reakce(udalosti)
    
    # kazda palka si svoji reakci vyhodnoti sama
    for palka in palky:
        palka.vyhodnotit_reakce(udalosti)

def vykreslovaci_operace():
    # pouziva promenne definovane vyse
    global okno, palky, micky
    
    # vyplneni okna barvou pozadi
    okno.displej.fill(okno.barva_pozadi)
    
    # vykresleni palek
    for palka in palky:
        palka.vykreslit(okno.displej)
    
    # vykresleni micku
    for micek in micky:
        # TO DO
        pass
    
def pohyb_objektu():
    # pouziva promenne definovane vyse
    global palky, micky

    # kazda palka si svuj pohyb vyhodnoti sama
    for palka in palky:
        palka.pohnout()
    
    # kazdy micek si svuj pohyb vyhodnoti sam
    for micek in micky:
        # TO DO
        pass
    
################################################################################
# Nekonecna vykreslovaci smycka
################################################################################

while True:
    # spusteni pomocnych podprogramu
    zpracovani_udalosti()
    pohyb_objektu()
    vykreslovaci_operace()

    # prekresleni okna
    pygame.display.update()
    