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
        self.rozliseni = rozliseni
        self.barva_pozadi = barva_pozadi

        self.objekty = []
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
# Objektova reprezentace hracovy palky
################################################################################

class Palka(Pohyblivy_predmet):
    def __init__(self, sirka, vyska, pozice_x, pozice_y, rychlost, klavesa_nahoru, klavesa_dolu, okno, barva):
        super().__init__(Vektor(sirka, vyska), Vektor(pozice_x, pozice_y), Vektor(0, 0))
        
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
        
        # posunuti (virtualni) palky
        super().pohnout()
        
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
# Objektova reprezentace hraciho micku
################################################################################

class Micek(Pohyblivy_predmet):
    def __init__(self, velikost, pozice_x, pozice_y, rychlost, uhel, okno, barva):
        super().__init__(Vektor(velikost, velikost), Vektor(pozice_x, pozice_y), Vektor(rychlost * math.cos(uhel), rychlost * math.sin(uhel)))
        
        okno.objekty.append(self)
        self.okno = okno
        self.barva = barva
        
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary = {'elipsa': Predmet(Vektor(w, h), Vektor(x - w / 2, y - h / 2))}
    
    def pohnout(self):
        # posunuti (virtualniho) micku
        super().pohnout()
        
        # detekce kolizi s okraji okna
        levy_okraj_okna = 0
        pravy_okraj_okna = self.okno.rozliseni[0]
        horni_okraj_okna = 0
        spodni_okraj_okna = self.okno.rozliseni[1]
        
        levy_okraj_micku = self.pozice.x - self.rozmer.x / 2
        pravy_okraj_micku = self.pozice.x + self.rozmer.x / 2
        horni_okraj_micku = self.pozice.y - self.rozmer.y / 2
        spodni_okraj_micku = self.pozice.y + self.rozmer.y / 2
        
        # korekce pozice a rychlosti micku v pripade kolize s okraji okna
        if levy_okraj_micku < levy_okraj_okna:
            self.pozice.x = self.rozmer.x / 2
            self.rychlost.x *= -1
        
        if pravy_okraj_micku > pravy_okraj_okna:
            self.pozice.x = self.okno.rozliseni[0] - self.rozmer.x / 2
            self.rychlost.x *= -1
        
        if horni_okraj_micku < horni_okraj_okna:
            self.pozice.y = self.rozmer.y / 2
            self.rychlost.y *= -1
        
        if spodni_okraj_micku > spodni_okraj_okna:
            self.pozice.y = self.okno.rozliseni[1] - self.rozmer.y / 2
            self.rychlost.y *= -1
        
        # nyni je pozice micku finalne znama
        
        # prepocitani pozice vsech casti palky
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
    # pouziva promenne definovane vyse
    global okno, palky
    
    # seznam udalosti, na ktere lze reagovat
    udalosti = pygame.event.get()
    
    # nejdrive zpracuje mozne reakce okno
    okno.vyhodnotit_reakce(udalosti)
    
    # kazda palka si svoji reakci vyhodnoti sama
    for palka in palky:
        palka.vyhodnotit_reakce(udalosti)

def pohyb_objektu():
    # pouziva promenne definovane vyse
    global palky, micky

    # kazda palka si svuj pohyb vyhodnoti sama
    for palka in palky:
        palka.pohnout()
    
    # kazdy micek si svuj pohyb vyhodnoti sam
    for micek in micky:
        micek.pohnout()
    
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
        micek.vykreslit(okno.displej)
    
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
    