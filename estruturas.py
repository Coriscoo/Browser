"""Estruturas de dados do navegador simulado.

- No / Pilha: histórico de navegação (a última página visitada fica no topo).
- ListaDuplamenteEncadeada: lista genérica com ponteiros para os dois lados.
- NoPagina: árvore que representa um site e suas páginas internas.
- ServidorRaiz: "root server" que resolve um domínio para a árvore do site.
"""


class No:
    """Nó encadeado usado pela Pilha e pela ListaDuplamenteEncadeada."""

    def __init__(self, url=0, prox=None, anterior=None):
        self.url = url
        self.prox = prox
        self.anterior = anterior

    def __repr__(self):
        return f"{self.url} -> {self.anterior}"


class Pilha:
    """Pilha encadeada (LIFO). O ponteiro `anterior` de cada nó aponta para o de baixo."""

    def __init__(self):
        self.topo = None
        self._tamanho = 0

    def is_empty(self):
        return self.topo is None

    def push(self, elemento):
        no = No(elemento)
        no.anterior = self.topo
        self.topo = no
        self._tamanho += 1

    def pop(self):
        """Remove e devolve o elemento do topo. Lança IndexError se a pilha estiver vazia."""
        if self.topo is None:
            raise IndexError("Não há histórico")
        valor = self.topo.url
        self.topo = self.topo.anterior
        self._tamanho -= 1
        return valor

    def espiar(self):
        """Devolve o elemento do topo sem removê-lo (None se vazia)."""
        return None if self.topo is None else self.topo.url

    def limpar(self):
        self.topo = None
        self._tamanho = 0

    def __iter__(self):
        """Percorre do topo até a base."""
        atual = self.topo
        while atual is not None:
            yield atual.url
            atual = atual.anterior

    def __repr__(self):
        return "[" + " -> ".join(str(v) for v in self) + "]"

    def __len__(self):
        return self._tamanho


class ListaDuplamenteEncadeada:
    def __init__(self):
        self.cabeca = None
        self.atual = None
        self.cauda = None
        self.tamanho = 0

    def lista(self):
        lista_nos = []
        atual = self.cabeca
        while atual is not None:
            lista_nos.append(atual.url)
            atual = atual.prox
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


class NoPagina:
    """Nó da árvore de um site: cada página aponta para o pai e para até MAX_LINKS filhos.

    A raiz da árvore é o domínio (ex.: www.ifpb.edu.br) e cada filho é uma pasta
    interna (ex.: /tsi). O caminho da raiz até um nó forma a url completa.
    """

    MAX_LINKS = 2

    def __init__(self, nome, pai=None):
        self.nome = nome
        self.pai = pai
        self.filhos = []

    def filho(self, nome):
        """Devolve o filho com esse nome ou None."""
        for f in self.filhos:
            if f.nome == nome:
                return f
        return None

    def tem_espaco(self):
        return len(self.filhos) < self.MAX_LINKS

    def adicionar_filho(self, nome):
        if self.filho(nome) is not None:
            raise ValueError(f"'{nome}' já existe em {self.url()}")
        if not self.tem_espaco():
            raise ValueError(f"{self.url()} já possui o máximo de {self.MAX_LINKS} links internos")
        novo = NoPagina(nome, self)
        self.filhos.append(novo)
        return novo

    def remover_filho(self, no):
        self.filhos.remove(no)
        no.pai = None

    def caminho(self):
        """Lista de nomes da raiz até este nó."""
        nomes = []
        no = self
        while no is not None:
            nomes.append(no.nome)
            no = no.pai
        return nomes[::-1]

    def url(self):
        return "/".join(self.caminho())

    def links(self):
        return ["/" + f.nome for f in self.filhos]

    def pre_ordem(self):
        """Percorre a subárvore em pré-ordem (pai antes dos filhos)."""
        yield self
        for f in self.filhos:
            yield from f.pre_ordem()

    def desenho(self, prefixo=""):
        """Linhas no formato de árvore usado no enunciado (+--- /pasta)."""
        linhas = []
        for i, f in enumerate(self.filhos):
            ultimo = i == len(self.filhos) - 1
            linhas.append(f"{prefixo}+--- /{f.nome}")
            linhas.extend(f.desenho(prefixo + ("     " if ultimo else "|    ")))
        return linhas

    def __repr__(self):
        return f"NoPagina({self.url()!r})"


class ServidorRaiz:
    """Root server simulado: mapeia cada domínio para (endereço IP, árvore do site).

    Usa uma tabela hash (dict) para achar o domínio em O(1), garantindo também que
    não existam duas urls com a mesma raiz de domínio. Dentro do site, a busca segue
    os ponteiros da árvore, pasta por pasta.
    """

    def __init__(self):
        self._dominios = {}
        self._proximo_ip = 1

    def ip(self, dominio):
        entrada = self._dominios.get(dominio)
        return entrada[0] if entrada else None

    def resolver(self, dominio, pastas):
        """Devolve o NoPagina da url ou None (equivale ao 404)."""
        entrada = self._dominios.get(dominio)
        if entrada is None:
            return None
        no = entrada[1]
        for nome in pastas:
            no = no.filho(nome)
            if no is None:
                return None
        return no

    def registrar(self, dominio, pastas):
        """Cadastra a url criando as pastas intermediárias que faltarem.

        Devolve a lista de nós criados (vazia se a url já existia). Lança ValueError
        se alguma página já tiver o limite de links internos.
        """
        criados = []
        entrada = self._dominios.get(dominio)
        if entrada is None:
            ip = f"10.0.0.{self._proximo_ip}"
            self._proximo_ip += 1
            raiz = NoPagina(dominio)
            self._dominios[dominio] = (ip, raiz)
            criados.append(raiz)
        else:
            raiz = entrada[1]

        # Só a primeira pasta inexistente pode esbarrar no limite (as seguintes nascem
        # em nós novos e vazios), então o erro acontece antes de qualquer alteração.
        no = raiz
        for nome in pastas:
            existente = no.filho(nome)
            if existente is None:
                existente = no.adicionar_filho(nome)
                criados.append(existente)
            no = existente
        return criados

    def remover(self, dominio, pastas):
        """Remove a página e todas as suas páginas internas. Devolve as urls removidas."""
        no = self.resolver(dominio, pastas)
        if no is None:
            return []
        removidas = [n.url() for n in no.pre_ordem()]
        if no.pai is None:
            del self._dominios[dominio]
        else:
            no.pai.remover_filho(no)
        return removidas

    def arvores(self):
        """Árvores na ordem em que os domínios foram cadastrados."""
        return [raiz for _, raiz in self._dominios.values()]

    def urls(self):
        """Todas as urls cadastradas, em pré-ordem."""
        return [no.url() for raiz in self.arvores() for no in raiz.pre_ordem()]

    def __contains__(self, dominio):
        return dominio in self._dominios

    def __len__(self):
        return sum(1 for _ in self.urls())
