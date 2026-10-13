import requests

class No:
    def __init__(self, url=0, anterior=None):
        self.url = url
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

sites = Pilha()
x = ["www.ifpb.edu.br", "www.google.com", "www.youtube.com"]
for i in x:
    sites.push(i)


def main():
    while True:
        cli = input(">")
        if cli.lower().startswith("#add "):
            sites.push(cli.lower().lstrip("#add "))

        elif cli.lower() == "#show":
            print(str(sites).replace(" -> None", ""))

        elif cli.lower() == "#pop":
            sites.pop()
            print(str(sites.topo).replace(" -> None", ""))

        elif cli.lower().startswith("#buscar "):
            url = cli.lower().lstrip("#buscar ")
            if url in x:
                url = "https://" + url
                saida = requests.get(url)
                print(saida.status_code)

        elif cli.lower() == "#sair":
            break
if __name__ == "__main__":
    main()