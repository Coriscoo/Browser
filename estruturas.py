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
        self.atual = None
        self.cauda = None
        self.tamanho = 0

    def lista(self):
        lista_nos = []
        atual = self.cabeca
        while atual != None:
            lista_nos.append(atual.url)
            atual = atual.proximo
        return lista_nos

    def novo_no(self, valor):
        no = No(valor)
        no.anterior = None
        no.prox = None
        return no

    def is_empty(self):
        return self.cabeca is None

    def inserir_inicio(self, valor):
        no = self.novo_no(valor)
        if self.is_empty():
            self.cabeca = self.cauda = no
        else:
            no.prox = self.cabeca
            self.cabeca.anterior = no
            self.cabeca = no
        self.tamanho += 1

    def inserir_fim(self, valor):
        no = self.novo_no(valor)
        if self.is_empty():
            self.cabeca = self.cauda = no
        else:
            no.anterior = self.cauda
            self.cauda.prox = no
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
        no.prox = atual
        atual.anterior.prox = no
        atual.anterior = no
        self.tamanho += 1

    def remover_inicio(self):
        if self.is_empty():
            raise IndexError("Lista vazia")
        valor = self.cabeca.url
        self.cabeca = self.cabeca.prox
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
            self.cauda.prox = None
        self.tamanho -= 1
        return valor

    def remover(self, valor):
        atual = self.cabeca
        while atual is not None:
            if atual.url == valor:
                if atual.anterior is None:
                    self.cabeca = atual.prox
                else:
                    atual.anterior.prox = atual.prox
                if atual.prox is None:
                    self.cauda = atual.anterior
                else:
                    atual.prox.anterior = atual.anterior
                self.tamanho -= 1
                return True
            atual = atual.prox
        return False

    def buscar(self, valor):
        atual = self.cabeca
        indice = 0
        while atual is not None:
            if atual.url == valor:
                return indice
            atual = atual.prox
            indice += 1
        return -1

    def visitar(self, url):
        if self.atual is None:
            self.inserir_fim(url)
            self.atual = self.cauda
            return
        
        no = self.atual.prox
        while no is not None:
            proximo = no.prox
            no.anterior = None
            no.prox = None
            self.tamanho -= 1
            no = proximo

        self.atual.prox = None
        self.cauda = self.atual

        self.inserir_fim(url)
        self.atual = self.cauda

    def voltar(self):
        if self.atual is None or self.atual.anterior is None:
            return None

        self.atual = self.atual.anterior
        return self.atual.url

    def avancar(self):
        if self.atual is None or self.atual.prox is None:
            return None

        self.atual = self.atual.prox
        return self.atual.url

    def pagina_atual(self):
        if self.atual is None:
            return None

        return self.atual.url

    def historico(self):
        return self.lista() or []

    def no_na_posicao(self, indice):
        if indice < 0:
            indice += self.tamanho
        if not 0 <= indice < self.tamanho:
            raise IndexError("Índice fora da lista")
        if indice < self.tamanho // 2:
            atual = self.cabeca
            for _ in range(indice):
                atual = atual.prox
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
            atual = atual.prox

    def __reversed__(self):
        atual = self.cauda
        while atual is not None:
            yield atual.url
            atual = atual.anterior

    def __repr__(self):
        return "[" + " <-> ".join(str(v) for v in self) + "]"
