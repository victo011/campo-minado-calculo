# Campo Minado de Cálculo

Jogo desktop em Python/Pygame que combina campo minado com perguntas de Funções, Limites, Derivadas e Integrais.

## Rodar no notebook

Instale Python 3.11 ou superior e Git. O desktop foi verificado com Python 3.14.7. Abra um terminal nesta pasta e execute:

```bash
python -m venv .venv
```

Ative o ambiente:

- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
- Windows CMD: `.\.venv\Scripts\activate.bat`
- macOS/Linux: `source .venv/bin/activate`

Instale as bibliotecas e inicie:

```bash
python -m pip install -r requirements.txt
python main.py
```

No Linux, o Pygame CE instala seu wheel pronto junto com SDL.

### Interface web React

Neste notebook, Node.js 24 LTS está incluído localmente em `.tools/node/`; não foi necessária senha de administrador. O arquivo `.tools/` não é enviado ao GitHub. Em outra máquina, instale Node.js 24 LTS e npm. Depois, na pasta do projeto, instale os pacotes e inicie o site:

```bash
./setup_web.sh
./run_web.sh
```

Para gerar a versão estática publicada no Netlify:

```bash
./build_web.sh
```

## Como jogar

Escolha tema e dificuldade no menu. Clique esquerdo abre casas e inicia/responde perguntas; clique direito alterna a bandeira. Ao abrir áreas vazias, o jogo pode revelar casas numeradas e abrir a primeira pergunta pendente. Digite a resposta e pressione Enter. Esc fecha a pergunta.

## Estrutura

- `main.py`: interface, menus, tabuleiro, perguntas e telas finais.
- `game_logic.py`: lógica original do campo minado e gerador de questões com SymPy.
- `requirements.txt`: Pygame CE e SymPy instalados pelo pip.
- `web/src/`: interface React, tabuleiro, configurações e mascote Luma.
- `package.json` e `package-lock.json`: React, Vite e dependências do site.
- `netlify.toml`: comando de build e diretório estático (`web/dist`).

## Publicação

O aplicativo desktop continua em Pygame. Como o Netlify publica arquivos web estáticos e não executa `main.py`, a interface React é compilada para arquivos estáticos em `web/dist`. Importe o repositório GitHub no Netlify; o arquivo `netlify.toml` define `npm run build` e `web/dist`. Será necessário autorizar o Netlify a acessar o repositório durante a conexão da conta.
