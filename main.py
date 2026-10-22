"""Ponto de entrada do navegador simulado.

    python main.py             abre a interface gráfica (index.html) no navegador
    python main.py --terminal  usa a interface de texto, no próprio terminal

Nas duas interfaces tudo é feito digitando na barra de url: urls, /pastas e
comandos iniciados por # (#help lista todos). Os botões da interface gráfica
apenas enviam o comando equivalente.
"""

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from navegador import Navegador

PASTA = os.path.dirname(os.path.abspath(__file__))
HOST, PORTA = "127.0.0.1", 8000


class Manipulador(BaseHTTPRequestHandler):
    """Rotas: GET / (index.html), GET /api/estado e POST /api/comando {"texto": "..."}."""

    navegador = None

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                with open(os.path.join(PASTA, "index.html"), "rb") as f:
                    self._enviar(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                self._enviar(500, "index.html não encontrado.".encode(), "text/plain; charset=utf-8")
        elif self.path == "/api/estado":
            resposta = {"ok": True, "estado": self.navegador.estado()}
            if self.navegador.avisos_carga:   
                resposta["saida"] = {"titulo": "Avisos ao carregar sites_registrados.txt",
                                     "linhas": self.navegador.avisos_carga}
                self.navegador.avisos_carga = []
            self._json(resposta)
        else:
            self._enviar(404, b"Not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/comando":
            return self._enviar(404, b"Not found", "text/plain")
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            texto = json.loads(self.rfile.read(tamanho) or b"{}").get("texto", "")
        except (ValueError, AttributeError):
            return self._json({"ok": False, "mensagem": "Requisição inválida."}, 400)

        try:
            resposta = self.navegador.executar(str(texto))
        except Exception as e:   
            resposta = {"ok": False, "mensagem": f"Erro inesperado: {e}"}
        resposta["estado"] = self.navegador.estado()
        self._json(resposta)

        if self.navegador.encerrado:
            
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    def _json(self, dados, codigo=200):
        self._enviar(codigo, json.dumps(dados, ensure_ascii=False).encode("utf-8"),
                     "application/json; charset=utf-8")

    def _enviar(self, codigo, corpo, tipo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args):
        pass   


def iniciar_web(navegador):
    Manipulador.navegador = navegador
    servidor = None
    for porta in range(PORTA, PORTA + 10):   
        try:
            servidor = HTTPServer((HOST, porta), Manipulador)
            break
        except OSError:
            continue
    if servidor is None:
        print(f"Não foi possível abrir as portas {PORTA}-{PORTA + 9}. Use: python main.py --terminal")
        return

    endereco = f"http://{HOST}:{servidor.server_port}"
    print(f"Navegador em execução: {endereco}")
    print("Digite #sair na barra de url (ou clique em Encerrar) para fechar. Ctrl+C também encerra.")
    threading.Timer(0.5, webbrowser.open, args=(endereco,)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
    print("Programa encerrado.")


def _colchetes(urls):
    return "".join(f"[{u}]" for u in urls) or "[ ]"


def iniciar_terminal(navegador):
    try:   
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    for aviso in navegador.avisos_carga:
        print("Aviso:", aviso)
    print("Digite #help para ver todos os comandos.\n")

    while not navegador.encerrado:
        estado = navegador.estado()
        print("-" * 60)
        print("Histórico de Visitas:", _colchetes(estado["historico"]))
        print("Home:", _colchetes([estado["home"]] if estado["home"] else []))
        print("Digite a url ou #back para retornar à última página visitada.")
        try:
            texto = input("url: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break

        resposta = navegador.executar(texto)
        print()
        if resposta.get("mensagem"):
            print(resposta["mensagem"] if resposta["ok"] else "Erro: " + resposta["mensagem"])
        if resposta.get("saida"):
            print(f"\n== {resposta['saida']['titulo']} ==")
            print("\n".join(resposta["saida"]["linhas"]))
        if resposta.get("pagina_aberta"):
            pagina = navegador.estado()["pagina"]
            print(f"\nurl: {pagina['url']}\n\n{pagina['texto']}\n")
            print("Links disponíveis:")
            print("\n".join(pagina["links"]) or "(nenhum)")
        print()
    print("Programa encerrado.")


def main():
    
    os.chdir(PASTA)
    navegador = Navegador("sites_registrados.txt", "conteudo")
    if "--terminal" in sys.argv[1:]:
        iniciar_terminal(navegador)
    else:
        iniciar_web(navegador)


if __name__ == "__main__":
    main()
