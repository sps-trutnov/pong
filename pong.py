# ------------------------------------------------------------------------------
# GRAFICKA HRA PONG © 2018-2019 Jakub Senkyr
# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------
# Objektova reprezentace dvourozmerneho vektoru
# ------------------------------------------------------------------------------

class Vektor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def velikost(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def uhel(self):
        return math.atan2(self.y, self.x)
    
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

# ------------------------------------------------------------------------------
# Objektova reprezentace vykreslovaciho okna
# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------
# Objektova reprezentace predmetu ve scene
# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------
# Objektova reprezentace pohybliveho predmetu ve scene
# ------------------------------------------------------------------------------

class Pohyblivy_predmet(Predmet):
    def __init__(self, okno, rozmer, pozice, rychlost):
        super().__init__(rozmer, pozice)
        
        self.rychlost = Vektor(rychlost.x, rychlost.y)
        
        self.okraje_okna = {'min': Vektor(0, 0),
                            'max': Vektor(okno.rozliseni.x, okno.rozliseni.y)}
        
        self.okraje_predmetu = {'min': Vektor(-rozmer.x / 2, -rozmer.y / 2),
                                'max': Vektor(rozmer.x / 2, rozmer.y / 2)}
    
    def pohnout(self, pri_kolizi_zastavit):
        self.posunout(self.rychlost)
        
        x = self.pozice.x
        y = self.pozice.y
        
        xp_min = self.okraje_predmetu['min'].x
        yp_min = self.okraje_predmetu['min'].y
        xp_max = self.okraje_predmetu['max'].x
        yp_max = self.okraje_predmetu['max'].y
        
        xo_min = self.okraje_okna['min'].x
        yo_min = self.okraje_okna['min'].y
        xo_max = self.okraje_okna['max'].x
        yo_max = self.okraje_okna['max'].y
        
        nastala_kolize = False
        
        if xo_min != None and xp_min + x < xo_min:
            #self.posunout(Vektor(2 * (xo_min - (xp_min + x)), 0))
            self.rychlost.x *= -1
            nastala_kolize = True
        
        if yo_min != None and yp_min + y < yo_min:
            #self.posunout(Vektor(0, 2 * (yo_min - (yp_min + y))))
            self.rychlost.y *= -1
            nastala_kolize = True
        
        if xo_max != None and xp_max + x > xo_max:
            #self.posunout(Vektor(2 * (xo_max - (xp_max + x)), 0))
            self.rychlost.x *= -1
            nastala_kolize = True
        
        if yo_max != None and yp_max + y > yo_max:
            #self.posunout(Vektor(0, 2 * (yo_max - (yp_max + y))))
            self.rychlost.y *= -1
            nastala_kolize = True
        
        if nastala_kolize and pri_kolizi_zastavit:
            self.rychlost.nasobit(0)

# ------------------------------------------------------------------------------
# Objektova reprezentace hracovy palky
# ------------------------------------------------------------------------------

class Palka(Pohyblivy_predmet):
    def __init__(self, okno, rozmer, pozice, modul_rychlosti, klavesa_nahoru, klavesa_dolu, barva):
        super().__init__(okno, Vektor(rozmer.x, rozmer.y), Vektor(pozice.x, pozice.y), Vektor(0, 0))
        
        self.modul_rychlosti = modul_rychlosti
        
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
        
        self.tvary = {'obdelnik': Predmet(Vektor(w, h - w), Vektor(x - w / 2, y + (h - w) / 2)),
                      'horni_elipsa': Predmet(Vektor(w, w), Vektor(x - w / 2, y + h / 2)),
                      'spodni_elipsa': Predmet(Vektor(w, w), Vektor(x - w / 2, y - h / 2 + w))}
        
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
            self.rychlost.secist(Vektor(0, -self.modul_rychlosti))
        
        if self.pohyb_nahoru:
            self.rychlost.secist(Vektor(0, self.modul_rychlosti))
        
        # posunuti stredu palky
        super().pohnout(True)
        
        # prepocitani pozice vsech casti palky
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary['obdelnik'].presunout(Vektor(x - w / 2, y + (h - w) / 2))
        self.tvary['horni_elipsa'].presunout(Vektor(x - w / 2, y + h / 2))
        self.tvary['spodni_elipsa'].presunout(Vektor(x - w / 2, y - h / 2 + w))

    def vykreslit(self, cil):
        barva = self.barva
        
        x = self.tvary['obdelnik'].pozice.x
        y = self.tvary['obdelnik'].pozice.y
        w = self.tvary['obdelnik'].rozmer.x
        h = self.tvary['obdelnik'].rozmer.y
        pygame.draw.rect(cil, barva, (x, self.okraje_okna['max'].y - y, w, h))
        
        x = self.tvary['horni_elipsa'].pozice.x
        y = self.tvary['horni_elipsa'].pozice.y
        w = self.tvary['horni_elipsa'].rozmer.x
        h = self.tvary['horni_elipsa'].rozmer.y
        pygame.draw.ellipse(cil, barva, (x, self.okraje_okna['max'].y - y, w, h))
        
        x = self.tvary['spodni_elipsa'].pozice.x
        y = self.tvary['spodni_elipsa'].pozice.y
        w = self.tvary['spodni_elipsa'].rozmer.x
        h = self.tvary['spodni_elipsa'].rozmer.y
        pygame.draw.ellipse(cil, barva, (x, self.okraje_okna['max'].y - y, w, h))

# ------------------------------------------------------------------------------
# Objektova reprezentace hraciho micku
# ------------------------------------------------------------------------------

class Micek(Pohyblivy_predmet):
    def __init__(self, okno, velikost, pozice, modul_rychlosti, uhel_rychlosti, barva):
        super().__init__(okno, Vektor(velikost, velikost), Vektor(pozice.x, pozice.y), Vektor(modul_rychlosti * math.cos(uhel_rychlosti), modul_rychlosti * math.sin(uhel_rychlosti)))
        
        okno.objekty.append(self)
        self.okno = okno
        self.barva = barva
        self.puvodni_barva = barva
        
        self.klavesa_cervene = pygame.K_r
        self.klavesa_zelene = pygame.K_g
        self.klavesa_modre = pygame.K_b
        self.klavesa_resetu = pygame.K_SPACE
        self.klavesy_modifikatoru = [pygame.K_LSHIFT, pygame.K_RSHIFT]
        
        self.cervena_aktivni = False
        self.zelena_aktivni = False
        self.modra_aktivni = False
        self.reset_aktivni = False
        self.modifikator_aktivni = False
        
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary = {'elipsa': Predmet(Vektor(w, h), Vektor(x - w / 2, y + h / 2))}
    
    def vyhodnotit_reakce(self, udalosti):
        for udalost in udalosti:
            if udalost.type == pygame.KEYDOWN:
                if udalost.key == self.klavesa_cervene:
                    self.cervena_aktivni = True
                if udalost.key == self.klavesa_zelene:
                    self.zelena_aktivni = True
                if udalost.key == self.klavesa_modre:
                    self.modra_aktivni = True
                if udalost.key == self.klavesa_resetu:
                    self.reset_aktivni = True
                if udalost.key in self.klavesy_modifikatoru:
                    self.modifikator_aktivni = True
            
            if udalost.type == pygame.KEYUP:
                if udalost.key == self.klavesa_cervene:
                    self.cervena_aktivni = False
                if udalost.key == self.klavesa_zelene:
                    self.zelena_aktivni = False
                if udalost.key == self.klavesa_modre:
                    self.modra_aktivni = False
                if udalost.key == self.klavesa_resetu:
                    self.reset_aktivni = False
                if udalost.key in self.klavesy_modifikatoru:
                    self.modifikator_aktivni = False
        
        r = self.cervena_aktivni
        g = self.zelena_aktivni
        b = self.modra_aktivni
        m = self.modifikator_aktivni
        
        # prebarveni micku
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
        
        # ochrana pred pretecenim z rozsahu 0-255
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
        
        # pripadne obnoveni puvodni barvy micku
        if self.reset_aktivni:
            self.barva = self.puvodni_barva
    
    def pohnout(self):
        # posunuti stredu micku
        super().pohnout(False)
        
        # prepocitani pozice vsech casti micku
        x = self.pozice.x
        y = self.pozice.y
        w = self.rozmer.x
        h = self.rozmer.y
        
        self.tvary['elipsa'].presunout(Vektor(x - w / 2, y + h / 2))
    
    def vykreslit(self, cil):
        barva = self.barva
        
        x = self.tvary['elipsa'].pozice.x
        y = self.tvary['elipsa'].pozice.y
        w = self.tvary['elipsa'].rozmer.x
        h = self.tvary['elipsa'].rozmer.y
        
        pygame.draw.ellipse(cil, barva, (x, self.okraje_okna['max'].y - y, w, h))

# ------------------------------------------------------------------------------
# Inicializace
# ------------------------------------------------------------------------------

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
rychlost_palek = 0.25
offset_palek = 30

velikost_micku = 50
rychlost_micku = 0.25

# vytvoreni palek
palky = []
palky.append(Palka(okno, Vektor(sirka_palek, vyska_palek), Vektor(offset_palek + sirka_palek / 2, okno.rozliseni.y / 2), rychlost_palek, pygame.K_w, pygame.K_s, (0, 0, 0)))
palky.append(Palka(okno, Vektor(sirka_palek, vyska_palek), Vektor(okno.rozliseni.x - offset_palek - sirka_palek / 2, okno.rozliseni.y / 2), rychlost_palek, pygame.K_UP, pygame.K_DOWN, (0, 0, 0)))

# vytvoreni micku
necitlivost = 1000
micky = []

for i in range(25):
    v = velikost_micku
    
    x = (okno.rozliseni.x - velikost_micku) / 2
    y = (okno.rozliseni.y - velikost_micku) / 2
    x_offset = random.randint(-100, +100)
    y_offset = random.randint(-100, +100)
    
    s = rychlost_micku * random.randint(5, 15) / 10
    u = random.randint(-60, +60) + random.choice((0, 180))
    
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    micky.append(Micek(okno, v, Vektor(x + x_offset, y + y_offset), s, math.radians(u), (r, g, b)))
    micky[-1].elasticky = False
    micky[-1].kolidoval = False

# ------------------------------------------------------------------------------
# Pomocne podprogramy
# ------------------------------------------------------------------------------

def zpracovani_udalosti():
    global okno, palky, micky
    
    udalosti = pygame.event.get()
    
    okno.vyhodnotit_reakce(udalosti)
    
    for palka in palky:
        palka.vyhodnotit_reakce(udalosti)
    
    for micek in micky:
        micek.vyhodnotit_reakce(udalosti)

def pohyb_objektu():
    global palky, micky, necitlivost

    for palka in palky:
        palka.pohnout()
    
    for micek in micky:
        micek.pohnout()
    
    # kolize mezi micky
    for orientacni_micek in micky:
        for kolizni_micek in micky:
            # micek se nemuze srazit sam se sebou, i kdyz sam sebou pronika
            if kolizni_micek == orientacni_micek:
                continue
            # micek se nemuze srazit s necim, co dosud neni pripravene se srazet
            if not kolizni_micek.elasticky:
                continue
            # micek se nebude srazet vicekrat nez jednou za frame (pozdeji odstranit)
            if kolizni_micek.kolidoval:
                continue
            
            x1 = orientacni_micek.pozice.x
            y1 = orientacni_micek.pozice.y
            x2 = kolizni_micek.pozice.x
            y2 = kolizni_micek.pozice.y
            
            d1 = orientacni_micek.rozmer.x
            d2 = kolizni_micek.rozmer.x

            vzdalenost_micku = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
            kriticka_vzdalenost = (d1 + d2) / 2
            
            if vzdalenost_micku < kriticka_vzdalenost:
                # pri kolizi se zabranuje zrcadlove kolizi pred dokoncenim pruchodu pole
                orientacni_micek.kolidoval = True
                
                if orientacni_micek.elasticky and kolizni_micek.elasticky:
                    # pri pruniku se preventivne zabranuje dalsimu srazeni
                    orientacni_micek.elasticky = False
                    kolizni_micek.elasticky = False
                    # neelasticke micky se indikuji jinou barvou
                    orientacni_micek.barva = (100, 100, 100)
                    kolizni_micek.barva = (100, 100, 100)
                    # micky se pri kolizi zastavi
                    #orientacni_micek.rychlost = Vektor(0, 0)
                    #kolizni_micek.rychlost = Vektor(0, 0)
                    
                    # hybnost paru pred kolizi
                    old_momentum = orientacni_micek.rychlost.velikost() + kolizni_micek.rychlost.velikost()
                    
                    # vzorec pro kolizi (Wikipedie)
                    old_v1 = Vektor(orientacni_micek.rychlost.x, orientacni_micek.rychlost.y)
                    old_v2 = Vektor(kolizni_micek.rychlost.x, kolizni_micek.rychlost.y)
                    
                    phi_angle = Vektor(kolizni_micek.pozice.x - orientacni_micek.pozice.x, kolizni_micek.pozice.y - orientacni_micek.pozice.y).uhel()
                    
                    new_v1x = old_v2.velikost() * math.cos(old_v2.uhel() - phi_angle) * math.cos(phi_angle) + old_v1.velikost() * math.sin(old_v1.uhel() - phi_angle) * math.sin(-phi_angle)
                    new_v1y = old_v2.velikost() * math.cos(old_v2.uhel() - phi_angle) * math.sin(phi_angle) + old_v1.velikost() * math.sin(old_v1.uhel() - phi_angle) * math.cos(-phi_angle)
                    
                    new_v2x = old_v1.velikost() * math.cos(old_v1.uhel() - phi_angle) * math.cos(phi_angle) + old_v2.velikost() * math.sin(old_v2.uhel() - phi_angle) * math.sin(-phi_angle)
                    new_v2y = old_v1.velikost() * math.cos(old_v1.uhel() - phi_angle) * math.sin(phi_angle) + old_v2.velikost() * math.sin(old_v2.uhel() - phi_angle) * math.cos(-phi_angle)
                    
                    orientacni_micek.rychlost = Vektor(new_v1x, new_v1y)
                    kolizni_micek.rychlost = Vektor(new_v2x, new_v2y)
                    
                    # hybnost paru po kolizi
                    new_momentum = orientacni_micek.rychlost.velikost() + kolizni_micek.rychlost.velikost()
                    
                    # korekce hybnosti
                    korekce = old_momentum / new_momentum
                    
                    orientacni_micek.rychlost.x *= korekce
                    orientacni_micek.rychlost.y *= korekce

                    kolizni_micek.rychlost.x *= korekce
                    kolizni_micek.rychlost.y *= korekce
        else:
            # pokud s nicim behem tohoto framu nekolidoval
            if not orientacni_micek.kolidoval and not orientacni_micek.elasticky:
                orientacni_micek.elasticky = True
                orientacni_micek.barva = (0, 0, 0)
    else:
        # reset priznaku kolizi pro novy frame
        for micek in micky:
            micek.kolidoval = False
    
def vykreslovaci_operace():
    global okno, palky, micky
    
    okno.vykreslit()
    
    for palka in palky:
        palka.vykreslit(okno.displej)
    
    for micek in micky:
        micek.vykreslit(okno.displej)

# ------------------------------------------------------------------------------
# Nekonecna vykreslovaci smycka
# ------------------------------------------------------------------------------

while True:
    zpracovani_udalosti()
    pohyb_objektu()
    vykreslovaci_operace()
    
    # prekresleni okna
    pygame.display.update()
    