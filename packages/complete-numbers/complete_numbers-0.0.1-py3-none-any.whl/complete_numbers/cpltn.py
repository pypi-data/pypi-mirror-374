class Cpltn:
    '''The basic numerical object we work with'''

    def __init__(self, realpart, imagpart = 0, intangpart = 0, immatpart = 0):
        self.a = realpart
        self.b = imagpart
        self.c = intangpart
        self.d = immatpart

    def __str__(self):
        selfstring = str(self.a)
        if self.b > 0: selfstring += ' + ' + self.b +'i'
        if self.c > 0: selfstring += ' + ' + self.c + 'phi'
        if self.d > 0: selfstring += ' + ' + self.d + 'psi'
        return selfstring

    
