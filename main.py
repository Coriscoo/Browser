import time
from paginas import pagina_web
from estruturas import Pilha, ListaDuplamenteEncadeada

def main():
    historico = ListaDuplamenteEncadeada()
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
    "#Voltar\n"
    "#Avançar\n"
    "#historico\n"
    "#exit --> Encerra o programa\n")
    while True:
        cli = input(">")
        if cli.lower().startswith("#add "):
            sites.inserir_fim(cli.lower().removeprefix("#add ").strip()) 
            db = open("sites_registrados.txt", "a")
            db.write("\n" + cli.lower().removeprefix("#add ").strip())
            db.close
        elif cli.lower().strip() == "#show":
            print(str(sites).replace("<->", ""))

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
            resultado = pagina_web("https://" + url)

            if resultado is not None:
                historico.visitar(url)

                titulo, elementos, links = resultado
                print(f"Home: {historico.pagina_atual()}")
                print(titulo)
                print(elementos)
                print(links)
            else:
                print("Url nao esta registrada.")
            
        elif cli.lower().startswith("#voltar"):
            url = historico.voltar()

            if url is None:
                print("Não há página anterior.")
            else:
                print(f"Home: {url}")

        elif cli.lower().startswith("#avancar"):
            url = historico.avancar()

            if url is None:
                print("Não há página seguinte.")
            else:
                print(f"Home: {url}")

        elif cli.lower().startswith("#historico"):
            print("Histórico:", historico.historico())
            print("Home:", historico.pagina_atual())

        elif cli.lower().strip() == "#exit":
            print("Encerrando Programa...")
            time.sleep(1)
            break

if __name__ == "__main__":
    main()
    