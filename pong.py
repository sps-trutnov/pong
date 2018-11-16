################################################################################
# GRAFICKA HRA PONG
################################################################################

# importovani knihovny pro praci s grafikou
import pygame
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
# Objektova reprezentace hierarchie trid pro praci s predmety ve scene
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

class Pohyblivy_predmet(Predmet):
    def __init__(self, rozmer, pozice, rychlost):
        super().__init__(rozmer, pozice)
        self.rychlost = Vektor(rychlost.x, rychlost.y)
    
    def pohnout(self):
        self.pozice.secist(self.rychlost)

################################################################################
# Objektova reprezentace hraciho micku
################################################################################

class Micek(Pohyblivy_predmet):
    def __init__(self, velikost, pozice_x, pozice_y, rychlost, uhel, okno, barva):
        super().__init__(Vektor(velikost, velikost), Vektor(pozice_x, pozice_y), Vektor(rychlost * math.cos(uhel), rychlost * math.sin(uhel)))
        
        self.okno = okno
        self.barva = barva
        
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary = {'elipsa': Predmet(Vektor(w, h), Vektor(x, y))}
    
    def vykreslit(self, cil):
        barva = self.barva
        
        x = tvary['elipsa'].pozice.x
        y = tvary['elipsa'].pozice.y
        w = tvary['elipsa'].rozmer.x
        h = tvary['elipsa'].rozmer.y
        
        pygame.draw.ellipse(cil, barva, x, y, w, h)

################################################################################
# Objektova reprezentace hracovy palky
################################################################################

class Palka(Pohyblivy_predmet):
    def __init__(self, sirka, vyska, pozice_x, pozice_y, rychlost, klavesa_nahoru, klavesa_dolu, okno, barva):
        super().__init__(Vektor(sirka, vyska), Vektor(pozice_x, pozice_y), Vektor(0, 0))
        
        self.max_rychlost = rychlost
        
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
        
        # posunuti (virtualni) palky
        self.pozice.secist(self.rychlost)
        
        # detekce kolizi s okraji okna
        horni_okraj_okna = 0
        spodni_okraj_okna = self.okno.rozliseni[1]
        horni_okraj_palky = self.pozice.y - self.rozmer.y / 2
        spodni_okraj_palky = self.pozice.y + self.rozmer.y / 2
        
        # korekce pozice palky v pripade kolize s okraji okna
        if horni_okraj_palky < horni_okraj_okna:
            self.pozice.y = self.rozmer.y / 2
        
        if spodni_okraj_palky > spodni_okraj_okna:
            self.pozice.y = self.okno.rozliseni[1] - self.rozmer.y / 2
        
        # nyni je pozice palky finalne znama
        
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
rychlost_palky = 0.5
barva_palky = (0, 0, 0)
offset_palky = 30

velikost_micku = 30
rychlost_micku = 1
barva_micku = (128, 0, 0)

# vytvoreni palek
palky = []
palky.append(Palka(sirka_palky, vyska_palky, offset_palky + sirka_palky / 2, okno.rozliseni[1] / 2, rychlost_palky, pygame.K_w, pygame.K_s, okno, barva_palky))
palky.append(Palka(sirka_palky, vyska_palky, okno.rozliseni[0] - offset_palky - sirka_palky / 2, okno.rozliseni[1] / 2, rychlost_palky, pygame.K_UP, pygame.K_DOWN, okno, barva_palky))

# vytvoreni micku
micky = []
micky.append(Micek(velikost_micku, okno.rozliseni[0], okno.rozliseni[1], rychlost_micku, math.radians(-45), okno, barva_micku))

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
    