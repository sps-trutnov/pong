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
# Objektova reprezentace dvourozmerneho vektoru
################################################################################

class Vektor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def velikost(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def prepsat(self, vzor):
        self.x = vzor.x
        self.y = vzor.y
    
    def nasobit(self, skalar):
        self.x *= skalar
        self.y *= skalar
    
    def secist(self, vektor):
        self.x += vektor.x
        self.y += vektor.y
    
    def otocit(self, uhel):
        velikost = self.velikost()
        self.uhel = math.atan2(self.y, self.x)
        self.uhel += uhel
        self.x = math.cos(self.uhel) * velikost
        self.y = math.sin(self.uhel) * velikost

################################################################################
# Objektova reprezentace vykreslovaciho okna
################################################################################

class Okno:
    def __init__(self, titulek, rozliseni, barva_pozadi):
        self.titulek = titulek
        self.rozliseni = Vektor(rozliseni[0],rozliseni[1])
        self.barva_pozadi = barva_pozadi
        
        self.objekty = []
        self.displej = None
    
    def vyhodnotit_reakce(self, udalosti):
        # prochazeni vsech udalosti, na ktere muze okno reagovat
        for udalost in udalosti:
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
        
        x = self.pozice.x
        y = self.pozice.y
        
        xo_min = self.okraje_predmetu['min'].x
        yo_min = self.okraje_predmetu['min'].y
        xo_max = self.okraje_predmetu['max'].x
        yo_max = self.okraje_predmetu['max'].y
        
        xh_min = self.hranice_prostredi['min'].x
        yh_min = self.hranice_prostredi['min'].y
        xh_max = self.hranice_prostredi['max'].x
        yh_max = self.hranice_prostredi['max'].y
        
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
        
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary = {'obdelnik': Predmet(Vektor(w, h - w), Vektor(x - w / 2, y - (h - w) / 2)),
                      'horni_elipsa': Predmet(Vektor(w, w), Vektor(x - w / 2, y - h / 2)),
                      'spodni_elipsa': Predmet(Vektor(w, w), Vektor(x - w / 2, y + h / 2 - w))}
        
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
        # nastaveni rychlosti podle smeru pohybu
        self.rychlost = Vektor(0, 0)
        
        if self.pohyb_dolu:
            self.rychlost.secist(Vektor(0, self.max_rychlost))
        
        if self.pohyb_nahoru:
            self.rychlost.secist(Vektor(0, -self.max_rychlost))
        
        # posunuti stredu palky
        super().pohnout(True)
        
        # prepocitani pozice vsech casti palky
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary['obdelnik'].presunout(Vektor(x - w / 2, y - (h - w) / 2))
        self.tvary['horni_elipsa'].presunout(Vektor(x - w / 2, y - h / 2))
        self.tvary['spodni_elipsa'].presunout(Vektor(x - w / 2, y + h / 2 - w))

    def vykreslit(self, cil):
        barva = self.barva
        
        x = self.tvary['obdelnik'].pozice.x
        y = self.tvary['obdelnik'].pozice.y
        w = self.tvary['obdelnik'].rozmer.x
        h = self.tvary['obdelnik'].rozmer.y
        pygame.draw.rect(cil, barva, (x, y, w, h))
        
        x = self.tvary['horni_elipsa'].pozice.x
        y = self.tvary['horni_elipsa'].pozice.y
        w = self.tvary['horni_elipsa'].rozmer.x
        h = self.tvary['horni_elipsa'].rozmer.y
        pygame.draw.ellipse(cil, barva, (x, y, w, h))
        
        x = self.tvary['spodni_elipsa'].pozice.x
        y = self.tvary['spodni_elipsa'].pozice.y
        w = self.tvary['spodni_elipsa'].rozmer.x
        h = self.tvary['spodni_elipsa'].rozmer.y
        pygame.draw.ellipse(cil, barva, (x, y, w, h))

################################################################################
# Objektova reprezentace hraciho micku
################################################################################

class Micek(Pohyblivy_predmet):
    def __init__(self, velikost, pozice_x, pozice_y, rychlost, uhel, okno, barva):
        super().__init__(Vektor(velikost, velikost), Vektor(pozice_x, pozice_y), Vektor(rychlost * math.cos(uhel), rychlost * math.sin(uhel)), Vektor(0, 0), okno.rozliseni)
        
        okno.objekty.append(self)
        self.okno = okno
        self.barva = barva
        
        self.klavesa_cervene = pygame.K_r
        self.klavesa_zelene = pygame.K_g
        self.klavesa_modre = pygame.K_b
        self.klavesy_modifikatoru = [pygame.K_LSHIFT, pygame.K_RSHIFT]
        
        self.cervena_aktivni = False
        self.zelena_aktivni = False
        self.modra_aktivni = False
        self.modifikator_aktivni = False
        
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary = {'elipsa': Predmet(Vektor(w, h), Vektor(x - w / 2, y - h / 2))}
    
    def vyhodnotit_reakce(self, udalosti):
        for udalost in udalosti:
            if udalost.type == pygame.KEYDOWN:
                if udalost.key == self.klavesa_cervene:
                    self.cervena_aktivni = True
                if udalost.key == self.klavesa_zelene:
                    self.zelena_aktivni = True
                if udalost.key == self.klavesa_modre:
                    self.modra_aktivni = True
                if udalost.key in self.klavesy_modifikatoru:
                    self.modifikator_aktivni = True
            
            if udalost.type == pygame.KEYUP:
                if udalost.key == self.klavesa_cervene:
                    self.cervena_aktivni = False
                if udalost.key == self.klavesa_zelene:
                    self.zelena_aktivni = False
                if udalost.key == self.klavesa_modre:
                    self.modra_aktivni = False
                if udalost.key in self.klavesy_modifikatoru:
                    self.modifikator_aktivni = False
        
        r = self.cervena_aktivni
        g = self.zelena_aktivni
        b = self.modra_aktivni
        m = self.modifikator_aktivni
        
        if r and not m:
            self.barva = (self.barva[0] + 1, self.barva[1], self.barva[2])
        if g and not m:
            self.barva = (self.barva[0], self.barva[1] + 1, self.barva[2])
        if b and not m:
            self.barva = (self.barva[0], self.barva[1], self.barva[2] + 1)
        if r and m:
            self.barva = (self.barva[0] - 1, self.barva[1], self.barva[2])
        if g and m:
            self.barva = (self.barva[0], self.barva[1] - 1, self.barva[2])
        if b and m:
            self.barva = (self.barva[0], self.barva[1], self.barva[2] - 1)
        
        if self.barva[0] < 0:
            self.barva = (0, self.barva[1], self.barva[2])
        if self.barva[1] < 0:
            self.barva = (self.barva[0], 0, self.barva[2])
        if self.barva[2] < 0:
            self.barva = (self.barva[0], self.barva[1], 0)
        if self.barva[0] > 255:
            self.barva = (255, self.barva[1], self.barva[2])
        if self.barva[1] > 255:
            self.barva = (self.barva[0], 255, self.barva[2])
        if self.barva[2] > 255:
            self.barva = (self.barva[0], self.barva[1], 255)
    
    def pohnout(self):
        # posunuti stredu micku
        super().pohnout(False)
        
        # prepocitani pozice vsech casti micku
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary['elipsa'].presunout(Vektor(x - w / 2, y - h / 2))
    
    def vykreslit(self, cil):
        barva = self.barva
        
        x = self.tvary['elipsa'].pozice.x
        y = self.tvary['elipsa'].pozice.y
        w = self.tvary['elipsa'].rozmer.x
        h = self.tvary['elipsa'].rozmer.y
        
        pygame.draw.ellipse(cil, barva, (x, y, w, h))

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
okno.displej = pygame.display.set_mode((okno.rozliseni.x, okno.rozliseni.y))

# nastaveni parametru hry
sirka_palek = 15
vyska_palek = 75
rychlost_palek = 0.5
offset_palek = 30

velikost_micku = 30
rychlost_micku = 0.6

# vytvoreni palek
palky = []
palky.append(Palka(sirka_palek, vyska_palek, offset_palek + sirka_palek / 2, okno.rozliseni.y / 2, rychlost_palek, pygame.K_w, pygame.K_s, okno, (0, 0, 0)))
palky.append(Palka(sirka_palek, vyska_palek, okno.rozliseni.x - offset_palek - sirka_palek / 2, okno.rozliseni.y / 2, rychlost_palek, pygame.K_UP, pygame.K_DOWN, okno, (0, 0, 0)))

# vytvoreni micku
micky = []

for i in range(100):
    v = velikost_micku
    
    x = (okno.rozliseni.x - velikost_micku) / 2
    y = (okno.rozliseni.y - velikost_micku) / 2
    y_offset = random.randint(-200, +200)
    
    s = rychlost_micku * random.randint(5, 15) / 10
    u = random.randint(-60, +60) + random.choice((0, 180))
    
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
    
    for micek in micky:
        micek.vyhodnotit_reakce(udalosti)

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
        micek.vykreslit(okno.displej)
    
################################################################################
# Nekonecna vykreslovaci smycka
################################################################################

while True:
    zpracovani_udalosti()
    pohyb_objektu()
    vykreslovaci_operace()

    # prekresleni okna
    pygame.display.update()
    