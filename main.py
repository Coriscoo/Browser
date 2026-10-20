import requests, time
from bs4 import BeautifulSoup

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
db = open("sites_registrados.txt", "r")
conteudo = db.read()
registrados = conteudo.splitlines()
db.close()
for site in registrados:
    sites.push(site)

def main():
    while True:
        cli = input(">")
        if cli.lower().startswith("#add "):
            sites.push(cli.lower().lstrip("#add "))
            db = open("sites_registrados.txt", "a")
            db.write("\n" + cli.lower().lstrip("#add "))
            db.close

        elif cli.lower().strip() == "#show":
            print(str(sites).replace(" -> None", ""))

        elif cli.lower() == "#pop":
            sites.pop()
            print(str(sites.topo).replace(" -> None", ""))

        elif cli.lower().startswith("#buscar "):
            url = cli.lower().lstrip("#buscar ")
            if url in registrados:
                url = "https://" + url
                saida = requests.get(url)
                print(saida.status_code)

        elif cli.lower().strip() == "#exit":
            print("Encerrando Programa...")
            time.sleep(1)
            break

if __name__ == "__main__":
    main()