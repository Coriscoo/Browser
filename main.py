import time
from paginas import pagina_web
from estruturas import Pilha, ListaDuplamenteEncadeada

def main():
    sites = ListaDuplamenteEncadeada()
    db = open("sites_registrados.txt", "r")
    conteudo = db.read()
    registrados = conteudo.splitlines()
    db.close()
    for site in registrados:
        sites.inserir_fim(site)

    print("Forma de Uso:\n" \
    "#show --> Mostra os sites ja registrados\n" \
    "#add --> Registra um site\n" \
    "#pop --> Remove o ultimo site registrado\n" \
    "#pop <url> Remove a url de sites registrados\n"
    "#buscar <url> --> Busca por um site registrado\n" \
    "#exit --> Encerra o programa\n")
    while True:
        try:
            cli = input(">")
            if cli.lower().startswith("#add "):
                domain = cli.lower().removeprefix("#add").removeprefix("http://").removeprefix("https://").strip()
                domain = domain.removeprefix("http://")
                domain = domain.removeprefix("https://").strip()
                if domain not in sites.lista():
                    sites.inserir_fim(domain)
                    db = open("sites_registrados.txt", "a")
                    db.write("\n" + domain)
                    db.close
            elif cli.lower().strip() == "#show":
                mostrar = str(sites).replace("<->", "")
                mostrar = mostrar.lstrip("[").rstrip("]")
                print(mostrar.strip())

            elif cli.lower().startswith("#pop"):
                if cli.lower().strip() == "#pop":
                    sites.remover_fim()
                else:
                    sites.remover(cli.lower().removeprefix("#pop").strip())
                lista_pop = sites.lista()
                db = open("sites_registrados.txt", "w")
                for site in lista_pop:
                    db.write("\n" + site)
                db.close

            elif cli.lower().startswith("#buscar"):
                url = cli.lower().removeprefix("#buscar").strip()
                if url in registrados:
                    url = "https://" + url
                    titulo, elementos, links = pagina_web(url)
                    print(titulo)
                    print(elementos)
                    print(links)
                else:
                    print("Url nao esta registrada.")

            elif cli.lower().strip() == "#exit":
                print("Encerrando Programa...")
                time.sleep(1)
                break
        except KeyboardInterrupt:
            print("\nEncerrando Programa...")
            time.sleep(1)
            break

if __name__ == "__main__":
    main()
    