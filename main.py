import requests, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console

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

def pagina_web(url):
    cabecalho = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5851.0 Safari/537.36"}
    blocos = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]
    saida = requests.get(url, headers=cabecalho)
    if saida.status_code >= 404:
        print(saida.status_code)
    else:
        saida.encoding = saida.apparent_encoding
        
        soup = BeautifulSoup(saida.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()

        if soup.title:
            titulo = soup.title.get_text(strip=True) 
        else:
            titulo = url

        links = []
        for a in soup.find_all("a", href=True):
            texto_link = a.get_text(" ", strip=True) or "link"
            links.append(urljoin(url, a["href"]))
            a.replace_with(f"{texto_link} [{len(links)}]")

        corpo = soup.body or soup

        elementos = []
        for tag in corpo.find_all(blocos):
            if tag.find_parent(blocos):
                continue
            if tag.name == "pre":
                texto = tag.get_text().strip("\n")
            else:
                texto = tag.get_text(" ", strip=True)
            
            if texto:
                elementos.append((tag.name, texto))
            
        if not elementos:
            for linha in corpo.get_text("\n", strip=True).splitlines():
                elementos.append(("p", linha))

        return titulo, elementos, links

def main():
    sites = Pilha()
    db = open("sites_registrados.txt", "r")
    conteudo = db.read()
    registrados = conteudo.splitlines()
    db.close()
    for site in registrados:
        sites.push(site)

    print("Forma de Uso:\n" \
    "#show --> Mostra os sites ja registrados\n" \
    "#add --> Registra um site\n" \
    "#pop --> Remove o ultimo site registrado\n" \
    "#buscar <url> --> Busca por um site registrado\n" \
    "#exit --> Encerra o programa\n")
    while True:
        cli = input(">")
        if cli.lower().startswith("#add "):
            sites.push(cli.lower().removeprefix("#add "))
            db = open("sites_registrados.txt", "a")
            db.write("\n" + cli.lower().removeprefix("#add "))
            db.close

        elif cli.lower().strip() == "#show":
            print(str(sites).replace(" -> None", ""))

        elif cli.lower() == "#pop":
            sites.pop()
            print(str(sites.topo).replace(" -> None", ""))

        elif cli.lower().startswith("#buscar "):
            url = cli.lower().removeprefix("#buscar ")
            if url in registrados:
                url = "https://" + url
                titulo, elementos, links = pagina_web(url)
                print(titulo)
                print(elementos)
                print(links)

        elif cli.lower().strip() == "#exit":
            print("Encerrando Programa...")
            time.sleep(1)
            break

if __name__ == "__main__":
    main()