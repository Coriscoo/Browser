import time
from paginas import pagina_web, exibir_pagina
from estruturas import ListaDuplamenteEncadeada

ARQUIVO = "sites_registrados.txt"


def carregar_sites(sites):
    with open(ARQUIVO, "r") as db:
        for linha in db.read().splitlines():
            linha = linha.strip()
            if linha:  # ignora linhas em branco
                sites.inserir_fim(linha)


def salvar_sites(sites):
    with open(ARQUIVO, "w") as db:
        db.write("\n".join(sites))


def main():
    historico = ListaDuplamenteEncadeada()
    sites = ListaDuplamenteEncadeada()
    carregar_sites(sites)

    print("Forma de Uso:\n"
          "#show --> Mostra os sites ja registrados\n"
          "#add <url> --> Registra um site\n"
          "#pop --> Remove o ultimo site registrado\n"
          "#pop <url> --> Remove a url de sites registrados\n"
          "#buscar <url> --> Busca por um site registrado\n"
          "#voltar\n"
          "#avancar\n"
          "#historico\n"
          "#exit --> Encerra o programa\n")

    while True:
        cli = input(">").strip()
        comando = cli.lower()

        if comando.startswith("#add "):
            url = comando.removeprefix("#add ").strip()
            if url in sites:
                print("Site ja registrado.")
            else:
                sites.inserir_fim(url)
                salvar_sites(sites)

        elif comando == "#show":
            print(str(sites).replace("<->", ""))

        elif comando.startswith("#pop"):
            if comando == "#pop":
                if sites.is_empty():
                    print("Nenhum site registrado.")
                    continue
                sites.remover_fim()
            else:
                url = comando.removeprefix("#pop").strip()
                if not sites.remover(url):
                    print("Url nao encontrada.")
                    continue
            salvar_sites(sites)

        elif comando.startswith("#buscar"):
            url = comando.removeprefix("#buscar").strip()

            if url not in sites:
                print("Url nao esta registrada.")
                continue

            resultado = pagina_web("https://www." + url)

            if resultado is not None:
                historico.visitar(url)
                titulo, elementos, links = resultado
                exibir_pagina(url, titulo, elementos, links)
            else:
                print("Nao foi possivel carregar a pagina.")

        elif comando.startswith("#voltar"):
            url = historico.voltar()
            if url is None:
                print("Não há página anterior.")
            else:
                print(f"Home: {url}")

        elif comando.startswith(("#avancar", "#avançar")):
            url = historico.avancar()
            if url is None:
                print("Não há página seguinte.")
            else:
                print(f"Home: {url}")

        elif comando.startswith("#historico"):
            print("Histórico:", historico.historico())
            print("Home:", historico.pagina_atual())

        elif comando == "#exit":
            print("Encerrando Programa...")
            time.sleep(1)
            break


if __name__ == "__main__":
    main()