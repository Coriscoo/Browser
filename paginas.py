import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console

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