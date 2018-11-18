################################################################################
# GRAFICKA HRA PONG
################################################################################

# importovani knihovny pro praci s grafikou
import pygame
# importovani knihovny pro praci s nahodnymi hodnotami
import random
# importovani knihovny s matematickymi funkcemi
import math
# importovani knihovny pro praci se systemem
import sys
# importovani vsech soucasti pygame.locals
from pygame.locals import *
from pygame.event import *

################################################################################
# Parametry aplikace
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
    
    def vykreslit(self):
        self.displej.fill(self.barva_pozadi)

################################################################################
# Objektova reprezentace predmetu ve scene
################################################################################

class Predmet:
    def __init__(self, rozmer, pozice):
        self.rozmer = Vektor(rozmer.x, rozmer.y)
        self.pozice = Vektor(pozice.x, pozice.y)
    
    def presunout(self, pozice):
        self.pozice.prepsat(pozice)
    
    def posunout(self, posun):
        self.pozice.secist(posun)
    
    def skalovat(self, faktor):
        self.rozmer.nasobit(faktor)

################################################################################
# Objektova reprezentace pohybliveho predmetu ve scene
################################################################################

class Pohyblivy_predmet(Predmet):
    def __init__(self, rozmer, pozice, rychlost, xy_min, xy_max):
        super().__init__(rozmer, pozice)
        
        self.rychlost = Vektor(rychlost.x, rychlost.y)
        
        self.hranice_prostredi = {'min': Vektor(xy_min.x, xy_min.y),
                                  'max': Vektor(xy_max.x, xy_max.y)}
        self.okraje_predmetu = {'min': Vektor(-rozmer.x / 2, -rozmer.y / 2),
                                'max': Vektor(rozmer.x / 2, rozmer.y / 2)}
    
    def pohnout(self, pri_kolizi_zastavit):
        self.posunout(self.rychlost)
        
        x = self.pozice_x = pozice_x
        y = self.pozice_y = pozice_y
        w = self.sirka = sirka
        h = self.vyska = vyska
        
        o = {'x': x - w / 2, 'y': y - (h - w) / 2, 'w': w, 'h': h - w}
        e1 = {'x': x - w / 2, 'y': y - h / 2, 'w': w, 'h': w}
        e2 = {'x': x - w / 2, 'y': y + h / 2 - w, 'w': w, 'h': w}
        
        self.tvary = {'obdelnik': o, 'horni_elipsa': e1, 'spodni_elipsa': e2}
        
        nastala_kolize = False
        
        if xh_min != None and xo_min + x < xh_min:
            self.posunout(Vektor(xh_min - (xo_min + x), 0))
            self.rychlost.x *= -1
            nastala_kolize = True
        
        if yh_min != None and yo_min + y < yh_min:
            self.posunout(Vektor(0, yh_min - (yo_min + y)))
            self.rychlost.y *= -1
            nastala_kolize = True
        
        if xh_max != None and xo_max + x > xh_max:
            self.posunout(Vektor(xh_max - (xo_max + x), 0))
            self.rychlost.x *= -1
            nastala_kolize = True
        
        if yh_max != None and yo_max + y > yh_max:
            self.posunout(Vektor(0, yh_max - (yo_max + y)))
            self.rychlost.y *= -1
            nastala_kolize = True
        
        if nastala_kolize and pri_kolizi_zastavit:
            self.rychlost.nasobit(0)

################################################################################
# Objektova reprezentace hracovy palky
################################################################################

class Palka(Pohyblivy_predmet):
    def __init__(self, sirka, vyska, pozice_x, pozice_y, rychlost, klavesa_nahoru, klavesa_dolu, okno, barva):
        super().__init__(Vektor(sirka, vyska), Vektor(pozice_x, pozice_y), Vektor(0, 0), Vektor(0,0), okno.rozliseni)
        
        self.max_rychlost = rychlost
        
        okno.objekty.append(self)
        self.okno = okno
        self.barva = barva
        
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

pozice_x_palky = 30
pozice_y_palky = rozliseni_okna[1] / 2

pohyb_palkou_nahoru = False
pohyb_palkou_dolu = False

rychlost_posunu_palky = 0.5

################################################################################
# Inicializace
################################################################################

# inicializace knihovny Pygame
pygame.init()

# vytvoreni vykreslovaciho okna
okno = Okno('Pong', (800, 600), (255, 255, 255))
# nastaveni titulku okna
pygame.display.set_caption(okno.titulek)
# nastaveni velikosti okna
okno.displej = pygame.display.set_mode(okno.rozliseni)

# nastaveni parametru hry
sirka_palek = 15
vyska_palek = 75
rychlost_palek = 0.5
offset_palek = 30

velikost_micku = 30
rychlost_micku = 0.6

# vytvoreni palek
palky = []
palky.append(Palka(sirka_palek, vyska_palek, offset_palek + sirka_palek / 2, okno.rozliseni[1] / 2, rychlost_palek, pygame.K_w, pygame.K_s, okno, (0, 0, 0)))
palky.append(Palka(sirka_palek, vyska_palek, okno.rozliseni[0] - offset_palek - sirka_palek / 2, okno.rozliseni[1] / 2, rychlost_palek, pygame.K_UP, pygame.K_DOWN, okno, (0, 0, 0)))

# vytvoreni micku
micky = []
#micky.append(Micek(velikost_micku, (okno.rozliseni[0] - velikost_micku) / 2, (okno.rozliseni[1] - velikost_micku) / 2 + 25, rychlost_micku, math.radians(+35), okno, (200, 0, 0)))
#micky.append(Micek(velikost_micku, (okno.rozliseni[0] - velikost_micku) / 2, (okno.rozliseni[1] - velikost_micku) / 2 - 50, rychlost_micku, math.radians(-25), okno, (0, 200, 0)))
#micky.append(Micek(velikost_micku, (okno.rozliseni[0] - velikost_micku) / 2, (okno.rozliseni[1] - velikost_micku) / 2 - 75, rychlost_micku, math.radians(-50), okno, (0, 0, 200)))

for i in range(100):
    v = velikost_micku
    x = (okno.rozliseni[0] - velikost_micku) / 2
    y = (okno.rozliseni[1] - velikost_micku) / 2
    y_offset = random.randint(-200, +200)
    s = rychlost_micku * random.randint(5, 15) / 10
    u = random.randint(0, 360)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    micky.append(Micek(v, x, y + y_offset, s, math.radians(u), okno, (r, g, b)))

################################################################################
# Pomocne podprogramy
################################################################################

def zpracovani_udalosti():
    global okno, palky
    
    udalosti = pygame.event.get()
    
    okno.vyhodnotit_reakce(udalosti)
    
    for palka in palky:
        palka.vyhodnotit_reakce(udalosti)

def pohyb_objektu():
    global palky, micky

    for palka in palky:
        palka.pohnout()
    
    for micek in micky:
        micek.pohnout()
    
def vykreslovaci_operace():
    global okno, palky, micky
    
    okno.vykreslit()
    
    for palka in palky:
        palka.vykreslit(okno.displej)
    
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
    pohyb_objektu()
    vykreslovaci_operace()

    # prekresleni okna
    pygame.display.update()
    