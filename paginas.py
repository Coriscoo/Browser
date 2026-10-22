import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def pagina_web(url):
    cabecalho = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5851.0 Safari/537.36"}
    blocos = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]

    try:
        saida = requests.get(url, headers=cabecalho, timeout=10)
    except requests.RequestException as erro:
        console.print(Text(f"Erro ao acessar a página: {erro}", style="red"))
        return None

    if saida.status_code >= 400:
        console.print(Text(f"Erro HTTP {saida.status_code} ao acessar {url}", style="red"))
        return None

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


def exibir_pagina(url, titulo, elementos, links):
    console.print(Panel(Text(titulo, style="bold"), subtitle=url, border_style="cyan"))

    for tag, texto in elementos:
        t = Text(texto)  # Text evita que o rich interprete [1], [2] como markup

        if tag == "h1":
            console.print()
            console.print(Text(texto.upper(), style="bold magenta"))
        elif tag in ("h2", "h3"):
            console.print()
            console.print(Text(texto, style="bold yellow"))
        elif tag in ("h4", "h5", "h6"):
            console.print(Text(texto, style="bold"))
        elif tag == "li":
            console.print(Text("  • ") + t)
        elif tag == "blockquote":
            console.print(Panel(t, border_style="dim", padding=(0, 2)))
        elif tag == "pre":
            console.print(Panel(t, border_style="green"))
        else:  # p
            console.print(t)
            console.print()

    if links:
        console.print(Text("\nLinks", style="bold cyan"))
        for i, link in enumerate(links, 1):
            console.print(Text(f"[{i}] {link}"), overflow="fold")