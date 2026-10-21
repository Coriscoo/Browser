import time
from paginas import pagina_web
from estruturas import Pilha, ListaDuplamenteEncadeada

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
    