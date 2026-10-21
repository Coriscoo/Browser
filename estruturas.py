class No:
    def __init__(self, url=0, proximo=None, anterior=None):
        self.url = url
        self.proximo = proximo
        self.anterior = anterior

    def __repr__(self):
        return f"{self.url} -> {self.anterior}"

class Pilha:
    def __init__(self):
        self.topo = None

    def is_empty(self):
        return self.topo is None

    def push(self, elemento):
        no = No(elemento)
        no.anterior = self.topo
        self.topo = no

    def pop(self):
        assert self.topo != None, "Não há histórico"
        self.topo = self.topo.anterior

    def __repr__(self):
        return "[" + str(self.topo) + "]"

    def __len__(self):
        atual = self.topo
        c = 0
        while atual is not None:
            c += 1
            atual = atual.anterior
        return c

class ListaDuplamenteEncadeada:
    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0

    def lista(self):
        if self.cabeca == None:
            return
        lista_nos = []
        atual = self.cabeca
        while atual != None:
            lista_nos.append(atual.url)
            atual = atual.proximo
        return lista_nos

    def novo_no(self, valor):
        no = No(valor)
        no.anterior = None
        no.proximo = None
        return no

    def is_empty(self):
        return self.cabeca is None

    def inserir_inicio(self, valor):
        no = self.novo_no(valor)
        if self.is_empty():
            self.cabeca = self.cauda = no
        else:
            no.proximo = self.cabeca
            self.cabeca.anterior = no
            self.cabeca = no
        self.tamanho += 1

    def inserir_fim(self, valor):
        no = self.novo_no(valor)
        if self.is_empty():
            self.cabeca = self.cauda = no
        else:
            no.anterior = self.cauda
            self.cauda.proximo = no
            self.cauda = no
        self.tamanho += 1

    def inserir_posicao(self, indice, valor):
        if indice <= 0:
            return self.inserir_inicio(valor)
        if indice >= self.tamanho:
            return self.inserir_fim(valor)
        atual = self.no_na_posicao(indice)
        no = self.novo_no(valor)
        no.anterior = atual.anterior
        no.proximo = atual
        atual.anterior.proximo = no
        atual.anterior = no
        self.tamanho += 1

    def remover_inicio(self):
        if self.is_empty():
            raise IndexError("Lista vazia")
        valor = self.cabeca.url
        self.cabeca = self.cabeca.proximo
        if self.cabeca is None:
            self.cauda = None
        else:
            self.cabeca.anterior = None
        self.tamanho -= 1
        return valor

    def remover_fim(self):
        if self.is_empty():
            raise IndexError("Lista vazia")
        valor = self.cauda.url
        self.cauda = self.cauda.anterior
        if self.cauda is None:
            self.cabeca = None
        else:
            self.cauda.proximo = None
        self.tamanho -= 1
        return valor

    def remover(self, valor):
        atual = self.cabeca
        while atual is not None:
            if atual.url == valor:
                if atual.anterior is None:
                    self.cabeca = atual.proximo
                else:
                    atual.anterior.proximo = atual.proximo
                if atual.proximo is None:
                    self.cauda = atual.anterior
                else:
                    atual.proximo.anterior = atual.anterior
                self.tamanho -= 1
                return True
            atual = atual.proximo
        return False

    def buscar(self, valor):
        atual = self.cabeca
        indice = 0
        while atual is not None:
            if atual.url == valor:
                return indice
            atual = atual.proximo
            indice += 1
        return -1

    def no_na_posicao(self, indice):
        if indice < 0:
            indice += self.tamanho
        if not 0 <= indice < self.tamanho:
            raise IndexError("Índice fora da lista")
        if indice < self.tamanho // 2:
            atual = self.cabeca
            for _ in range(indice):
                atual = atual.proximo
        else:
            atual = self.cauda
            for _ in range(self.tamanho - 1 - indice):
                atual = atual.anterior
        return atual

    def __getitem__(self, indice):
        return self.no_na_posicao(indice).url

    def __contains__(self, valor):
        return self.buscar(valor) != -1

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        atual = self.cabeca
        while atual is not None:
            yield atual.url
            atual = atual.proximo

    def __reversed__(self):
        atual = self.cauda
        while atual is not None:
            yield atual.url
            atual = atual.anterior

    def __repr__(self):
        return "[" + " <-> ".join(str(v) for v in self) + "]"
