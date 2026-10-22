"""Lógica do navegador simulado: cadastro de urls, navegação, histórico e comandos #.

A interface (web ou terminal, ver main.py) só envia o texto digitado para
Navegador.executar() e exibe a resposta. Assim, a barra de endereço e os botões
passam exatamente pelo mesmo caminho.
"""

import os
import re

from estruturas import Pilha, ServidorRaiz

# Domínio: rótulos separados por ponto, terminando em um TLD só de letras (ex.: www.ifpb.edu.br).
_ROTULO = r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
_DOMINIO = re.compile(rf"^(?:{_ROTULO}\.)+[a-z]{{2,}}$")
_PASTA = re.compile(r"^[\w\-.~]+$")


class UrlInvalida(ValueError):
    """A url digitada não está no formato aceito."""


def separar_url(texto):
    """Valida o formato e devolve (dominio, [pastas]).

    Aceita, por exemplo: www.ifpb.edu.br, http://example.com, https://example.com/register/.
    """
    url = texto.strip().lower()
    for esquema in ("http://", "https://"):
        if url.startswith(esquema):
            url = url[len(esquema):]
            break
    url = url.rstrip("/")
    if not url:
        raise UrlInvalida("url vazia")
    if any(c in url for c in " ?#\\"):
        raise UrlInvalida(f"'{texto.strip()}' contém caracteres não permitidos")

    dominio, *pastas = url.split("/")
    if not _DOMINIO.match(dominio):
        raise UrlInvalida(f"'{dominio}' não é um domínio válido (ex.: www.exemplo.com.br)")
    for pasta in pastas:
        if pasta in ("", ".", "..") or not _PASTA.match(pasta):
            raise UrlInvalida(f"'/{pasta}' não é um nome de pasta válido")
    return dominio, pastas


class Navegador:
    """Estado do navegador e execução dos comandos digitados."""

    def __init__(self, arquivo_sites="sites_registrados.txt", pasta_conteudo="conteudo"):
        self._arquivo_sites = arquivo_sites
        self._pasta_conteudo = pasta_conteudo
        self._servidor = ServidorRaiz()
        self._historico = Pilha()   # páginas visitadas antes do home (topo = a mais recente)
        self._a_frente = Pilha()    # páginas desfeitas com #back, usadas por #forward
        self._home = None
        self.encerrado = False
        self.avisos_carga = []      # problemas encontrados ao ler o banco, exibidos ao iniciar
        self._carregar_banco()

        # nome -> (função, uso, descrição). Também gera o texto do #help.
        self._comandos = {
            "#back": (self._cmd_back, "#back", "Volta para a última página visitada (botão ←)."),
            "#forward": (self._cmd_forward, "#forward", "Avança para a página desfeita pelo #back (botão →)."),
            "#showhist": (self._cmd_showhist, "#showhist", "Mostra o histórico a partir do home."),
            "#add": (self._cmd_add, "#add <url> [texto]",
                     "Cadastra uma url (e as pastas internas que faltarem). O texto opcional vira o conteúdo da página."),
            "#pop": (self._cmd_pop, "#pop [url]",
                     "Remove a url e suas páginas internas. Sem url, remove o último site da lista."),
            "#show": (self._cmd_show, "#show", "Mostra todas as urls cadastradas em forma de árvore."),
            "#help": (self._cmd_help, "#help", "Mostra esta ajuda."),
            "#sair": (self._cmd_sair, "#sair", "Encerra o programa (botão Encerrar)."),
        }
        self._apelidos = {
            "#voltar": "#back", "#avancar": "#forward", "#avançar": "#forward",
            "#historico": "#showhist", "#histórico": "#showhist", "#exit": "#sair",
            "#ajuda": "#help",
        }

    # ------------------------------------------------------------------ banco de urls

    def _carregar_banco(self):
        """Povoa o servidor raiz a partir do arquivo texto, rejeitando linhas em formato inválido."""
        avisos = self.avisos_carga
        try:
            linhas = self._ler_texto(self._arquivo_sites).splitlines()
        except FileNotFoundError:
            linhas = []
            avisos.append(f"'{self._arquivo_sites}' não existia e será criado ao cadastrar a primeira url.")
        except OSError as e:
            avisos.append(f"Não foi possível ler '{self._arquivo_sites}': {e}")
            return

        for n, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                dominio, pastas = separar_url(linha)
                for no in self._servidor.registrar(dominio, pastas):
                    self._garantir_conteudo(no.url())
            except ValueError as e:   # inclui UrlInvalida e limite de links
                avisos.append(f"Linha {n} ignorada ({linha[:60]}): {e}")

    @staticmethod
    def _ler_texto(caminho):
        with open(caminho, "rb") as f:
            dados = f.read()
        for codificacao in ("utf-8-sig", "utf-16", "latin-1"):
            try:
                return dados.decode(codificacao)
            except UnicodeDecodeError:
                continue
        return dados.decode("utf-8", errors="replace")

    def _salvar_banco(self):
        with open(self._arquivo_sites, "w", encoding="utf-8") as f:
            for url in self._servidor.urls():
                f.write(url + "\n")

    def _arquivo_da_pagina(self, url):
        """Cada url tem um .txt em disco: conteudo/<dominio>/<pastas...>/index.txt"""
        return os.path.join(self._pasta_conteudo, *url.split("/"), "index.txt")

    def _garantir_conteudo(self, url, texto=None):
        """Cria o .txt da página se ainda não existir (ou grava o texto informado)."""
        caminho = self._arquivo_da_pagina(url)
        if texto is None and os.path.exists(caminho):
            return
        if texto is None:
            texto = (f"Bem-vindo(a) a {url}.\n\n"
                     f"Esta página ainda não tem conteúdo próprio. "
                     f"Edite o arquivo {caminho} para alterar este texto.")
        try:
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto + "\n")
        except OSError as e:
            self.avisos_carga.append(f"Não foi possível criar {caminho}: {e}")

    # ------------------------------------------------------------------ páginas

    def _pagina(self, url):
        """Simula a requisição: devolve status 200 com o texto do arquivo, ou 404."""
        try:
            dominio, pastas = separar_url(url)
        except UrlInvalida:
            dominio, pastas = None, []
        no = self._servidor.resolver(dominio, pastas) if dominio else None
        if no is None:
            return {"url": url, "status": 404, "ip": None, "links": [],
                    "texto": "404 — Página não encontrada (ela pode ter sido removida)."}
        try:
            texto = self._ler_texto(self._arquivo_da_pagina(url)).strip()
        except OSError:
            texto = "(O arquivo de conteúdo desta página não foi encontrado.)"
        return {"url": url, "status": 200, "ip": self._servidor.ip(dominio),
                "links": no.links(), "texto": texto}

    def _resolver_destino(self, texto):
        """Transforma o que foi digitado (url completa ou /pasta) em url normalizada."""
        if texto.startswith("/"):
            if self._home is None:
                raise UrlInvalida("nenhuma página aberta: digite uma url completa antes de usar /pasta")
            texto = self._home + "/" + texto.strip("/")
        dominio, pastas = separar_url(texto)
        return "/".join([dominio] + pastas)

    def _navegar(self, texto):
        try:
            url = self._resolver_destino(texto)
        except UrlInvalida as e:
            return self._erro(f"Url inválida: {e}.")

        pagina = self._pagina(url)
        if pagina["status"] == 404:
            if texto.startswith("/") and self._home:
                return self._erro(f"404 — Página não encontrada: '{texto}' não é um link de {self._home}.")
            return self._erro(f"404 — Página não encontrada: {url} não está cadastrada.")

        if url == self._home:
            return self._ok("Você já está nesta página.", pagina=pagina)
        if self._home is not None:
            self._historico.push(self._home)   # guarda a atual antes de se deslocar
        self._a_frente.limpar()
        self._home = url
        return self._ok("200 OK — Página encontrada!", pagina=pagina)

    # ------------------------------------------------------------------ comandos

    def executar(self, texto):
        """Ponto de entrada único: recebe o texto digitado e devolve um dicionário de resposta."""
        texto = (texto or "").strip()
        if not texto:
            return self._erro("Digite uma url, /pasta ou um comando iniciado por # (veja #help).")
        if not texto.startswith("#"):
            return self._navegar(texto)

        nome, _, argumento = texto.partition(" ")
        nome = self._apelidos.get(nome.lower(), nome.lower())
        if nome == "#buscar":   # compatibilidade com a versão de terminal anterior
            return self._navegar(argumento.strip()) if argumento.strip() else self._erro("Uso: #buscar <url>")
        if nome not in self._comandos:
            return self._erro(f"Comando '{nome}' não existe. Digite #help para ver os comandos.")
        try:
            return self._comandos[nome][0](argumento.strip())
        except OSError as e:
            return self._erro(f"Erro ao acessar arquivos em disco: {e}")

    def _cmd_back(self, _):
        if self._historico.is_empty():
            return self._erro("Não há página anterior: o histórico está vazio.")
        self._a_frente.push(self._home)
        self._home = self._historico.pop()   # a url sai do histórico ao ser visitada
        return self._ok(f"Voltou para {self._home}.", pagina=self._pagina(self._home))

    def _cmd_forward(self, _):
        if self._a_frente.is_empty():
            return self._erro("Não há página para avançar.")
        self._historico.push(self._home)
        self._home = self._a_frente.pop()
        return self._ok(f"Avançou para {self._home}.", pagina=self._pagina(self._home))

    def _cmd_showhist(self, _):
        if self._home is None:
            linhas = ["Nenhuma página visitada ainda."]
        else:
            linhas = [f"Home: {self._home}"]
            linhas += [f"{i}. {url}" for i, url in enumerate(self._historico, 1)]
            if self._historico.is_empty():
                linhas.append("(nenhuma página anterior)")
        return self._ok(saida=("Histórico de navegação (do home para trás)", linhas))

    def _cmd_add(self, argumento):
        url_txt, _, texto = argumento.partition(" ")
        if not url_txt:
            return self._erro("Uso: #add <url> [texto da página]")
        if url_txt.startswith("/"):   # permite cadastrar uma pasta interna do home: #add /nova
            if self._home is None:
                return self._erro("Abra uma página antes de cadastrar uma pasta com /.")
            url_txt = self._home + "/" + url_txt.strip("/")
        try:
            dominio, pastas = separar_url(url_txt)
            criados = self._servidor.registrar(dominio, pastas)
        except ValueError as e:
            return self._erro(f"Não foi possível cadastrar: {e}.")
        url = "/".join([dominio] + pastas)
        if not criados:
            if texto.strip():
                self._garantir_conteudo(url, texto.strip())
                return self._ok(f"{url} já estava cadastrada; o conteúdo foi atualizado.")
            return self._erro(f"{url} já está cadastrada.")

        for no in criados:
            self._garantir_conteudo(no.url(), texto.strip() if no.url() == url and texto.strip() else None)
        self._salvar_banco()
        extras = [n.url() for n in criados if n.url() != url]
        msg = f"{url} cadastrada!"
        if extras:
            msg += f" Também foram criadas: {', '.join(extras)}."
        return self._ok(msg)

    def _cmd_pop(self, argumento):
        if argumento:
            try:
                dominio, pastas = separar_url(argumento)
            except UrlInvalida as e:
                return self._erro(f"Url inválida: {e}.")
        else:
            urls = self._servidor.urls()
            if not urls:
                return self._erro("Não há sites cadastrados.")
            dominio, pastas = separar_url(urls[-1])

        removidas = self._servidor.remover(dominio, pastas)
        if not removidas:
            return self._erro(f"{'/'.join([dominio] + pastas)} não está cadastrada.")
        self._salvar_banco()
        msg = f"Removida: {removidas[0]}"
        if len(removidas) > 1:
            msg += f" (e mais {len(removidas) - 1} página(s) interna(s))"
        return self._ok(msg + ".")

    def _cmd_show(self, _):
        linhas = []
        for raiz in self._servidor.arvores():
            linhas.append(f"{raiz.nome}   (IP {self._servidor.ip(raiz.nome)})")
            linhas.extend("    " + l for l in raiz.desenho())
            linhas.append("")
        return self._ok(saida=("Urls cadastradas", linhas[:-1] or ["Nenhuma url cadastrada."]))

    def _cmd_help(self, _):
        linhas = ["<url>              Abre uma url cadastrada (ex.: www.ifpb.edu.br/tsi).",
                  "/<pasta>           Abre um link interno do home (ex.: /tsi).", ""]
        for _, uso, descricao in self._comandos.values():
            linhas.append(f"{uso:<19}{descricao}")
        linhas += ["", "Atalhos aceitos: " + ", ".join(f"{a} = {c}" for a, c in self._apelidos.items()),
                   "Os comandos não diferenciam maiúsculas de minúsculas."]
        return self._ok(saida=("Ajuda — comandos disponíveis", linhas))

    def _cmd_sair(self, _):
        self.encerrado = True
        return self._ok("Encerrando o programa...", encerrado=True)

    # ------------------------------------------------------------------ respostas

    @staticmethod
    def _ok(mensagem=None, pagina=None, saida=None, encerrado=False):
        resposta = {"ok": True, "mensagem": mensagem, "pagina_aberta": pagina is not None, "encerrado": encerrado}
        if saida:
            resposta["saida"] = {"titulo": saida[0], "linhas": saida[1]}
        return resposta

    @staticmethod
    def _erro(mensagem):
        return {"ok": False, "mensagem": mensagem, "pagina_aberta": False, "encerrado": False}

    def estado(self):
        """Tudo o que a interface precisa para se desenhar."""
        return {
            "sites": self._servidor.urls(),
            "historico": list(self._historico)[::-1],   # do mais antigo para o mais recente
            "home": self._home,
            "a_frente": list(self._a_frente),
            "pode_voltar": not self._historico.is_empty(),
            "pode_avancar": not self._a_frente.is_empty(),
            "pagina": self._pagina(self._home) if self._home else None,
        }
