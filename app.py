from flask import Flask, render_template, request, jsonify
from estruturas import Pilha, ListaDuplamenteEncadeada
from paginas import pagina_web

app = Flask(__name__)

# Instâncias globais que permanecem vivas na memória RAM do servidor
historico = Pilha()
home = ""
sites_registrados = ListaDuplamenteEncadeada()

def carregar_banco():
    try:
        with open("sites_registrados.txt", "r") as db:
            for site in db.read().splitlines():
                if site.strip():
                    sites_registrados.inserir_fim(site.strip())
    except FileNotFoundError:
        open("sites_registrados.txt", "w").close()

carregar_banco()

@app.route("/")
def index():
    # Carrega o arquivo HTML dentro da pasta /templates
    return render_template("index.html")

@app.route("/api/executar", methods=["POST"])
def executar_comando():
    global home
    dados = request.json
    entrada = dados.get("entrada", "").strip()

    if not entrada:
        return jsonify({"status": "erro", "mensagem": "Entrada vazia."})

    cmd = entrada.lower()

    # Comando #back usando a Pilha
    if cmd == "#back":
        if historico.is_empty():
            return jsonify({"status": "erro", "mensagem": "O histórico está vazio."})
        
        home = historico.topo.url
        historico.pop()
        return jsonify({
            "status": "sucesso",
            "home": home,
            "conteudo": f"Retornou para: {home}"
        })

    # Comando #showhist
    elif cmd == "#showhist":
        atual = historico.topo
        elementos_hist = []
        while atual:
            elementos_hist.append(atual.url)
            atual = atual.anterior
        return jsonify({
            "status": "sucesso",
            "home": home,
            "conteudo": f"Histórico Atual: {' -> '.join(elementos_hist) if elementos_hist else 'Vazio'}"
        })

    # Comando #add
    elif cmd.startswith("#add "):
        nova_url = cmd.removeprefix("#add").strip()
        if nova_url not in sites_registrados:
            sites_registrados.inserir_fim(nova_url)
            with open("sites_registrados.txt", "a") as db:
                db.write(nova_url + "\n")
            return jsonify({"status": "sucesso", "home": home, "conteudo": f"Site '{nova_url}' registrado!"})
        return jsonify({"status": "erro", "mensagem": "Site já registrado."})

    # Navegação e links internos
    else:
        destino = entrada
        if destino.startswith("/"):
            if not home:
                return jsonify({"status": "erro", "mensagem": "Nenhuma página base para link interno."})
            destino = home + destino

        # Consulta a Lista Duplamente Encadeada
        if destino in sites_registrados:
            if home:
                historico.push(home)
            home = destino

            try:
                url_fmt = "https://" + destino if not destino.startswith("http") else destino
                titulo, elementos, links = pagina_web(url_fmt)
                
                texto_final = f"=== {titulo} ===\n\n"
                for tag, txt in elementos:
                    texto_final += f"{txt}\n"
                
                if links:
                    texto_final += "\nLinks disponíveis:\n"
                    for idx, link in enumerate(links):
                        texto_final += f"[{idx}] {link}\n"

                return jsonify({
                    "status": "sucesso",
                    "home": home,
                    "conteudo": texto_final
                })
            except Exception as e:
                return jsonify({
                    "status": "sucesso",
                    "home": home,
                    "conteudo": f"Página encontrada no banco, mas erro ao carregar via HTTP: {e}"
                })
        else:
            return jsonify({"status": "erro", "mensagem": f"Erro 404: URL '{destino}' não cadastrada."})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)