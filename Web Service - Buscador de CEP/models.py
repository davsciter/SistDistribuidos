class CEP:
    def __init__(self, cep, logradouro, bairro, localidade, uf, ibge, ddd, siafi, buscas=0):
        self.cep = cep
        self.logradouro = logradouro
        self.bairro = bairro
        self.localidade = localidade
        self.uf = uf
        self.ibge = ibge
        self.ddd = ddd
        self.siafi = siafi
        self.buscas = buscas
    
    def addBusca(self):
        self.buscas = self.buscas+1
