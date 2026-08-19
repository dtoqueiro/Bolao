# Bolão Lotofácil 🍀

Uma plataforma dinâmica e interativa para gerenciamento de um bolão de Lotofácil com grupo de apostadores. Desenvolvido em Python com a interface construída em [Streamlit](https://streamlit.io/) e com persistência de dados conectada nativamente ao **Google Sheets**.

O grande diferencial deste sistema é não utilizar desdobramentos ou matrizes matemáticas estáticas. O motor matemático utiliza um algoritmo híbrido (Greedy + Simulated Annealing) que processa as dezenas de acordo com a inteligência coletiva (ranking dos votos positivos e negativos) para criar um conjunto configurável de jogos otimizados, sempre priorizando as dezenas mais votadas do grupo enquanto minimiza interseções para cobrir mais combinações.

## 🚀 Funcionalidades

- **Votação Interativa:** Os participantes podem votar em até 5 dezenas "favoritas" e até 3 "indesejadas". O formulário garante que o voto não tenha intersecções inválidas.
- **Login sem Senha:** Autenticação focada em usabilidade baseada no número de telefone do participante cadastrado ou nome completo.
- **Painel de Administração:** Controle completo do bolão pelo Admin:
  - Definir/Mudar o Quórum esperado (Padrão: 25 participantes).
  - Configurar estratégia: Quantidade de jogos (Padrão: 10 jogos) e tamanho de cada jogo (Padrão: 16 dezenas).
  - Encerrar e reabrir o bolão.
  - Executar o motor matemático em tempo real para cálculo dos jogos.
- **Exportação:** Exporta os jogos gerados num formato `.txt` compatível nativamente com softwares de impressão/gerenciamento lotérico (como o COLOGA).

## 🛠 Pré-requisitos

- Python 3.9+
- Projeto configurado no **Google Cloud Console** com a API do Google Sheets e Google Drive habilitadas.
- Uma Planilha no Google Sheets criada (o banco de dados da aplicação).

## ⚙️ Configuração do Ambiente

1. Clone o repositório ou acesse o diretório do projeto:
   ```bash
   cd Bolao
   ```

2. Crie um ambiente virtual (recomendado) e ative-o:
   ```bash
   python -m venv venv
   
   # No Windows
   venv\Scripts\activate
   
   # No Mac/Linux
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as credenciais do **Google Sheets**:
   - Salve seu arquivo de chaves de serviço do Google como `credentials.json` na raiz do projeto.
   - Crie um arquivo `config.env` na raiz do projeto e insira a ID da planilha que será utilizada como banco de dados:
     ```env
     SheetID=COLOQUE_SUA_ID_AQUI
     ```
   *(A ID da planilha é aquele código grande na URL, ex: `https://docs.google.com/spreadsheets/d/AQUI_FICA_A_ID/edit`)*

5. Certifique-se de que o e-mail da conta de serviço (encontrado dentro do seu `credentials.json`) tenha permissão de **Editor** na sua planilha do Google Sheets.

## ▶️ Executando a Aplicação

Com o ambiente virtual ativado e as credenciais configuradas, execute o aplicativo Streamlit:

```bash
streamlit run app.py
```

Isso abrirá automaticamente uma aba no seu navegador padrão (geralmente em `http://localhost:8501`). O sistema criará sozinho as abas de "Configuracao", "Participantes" e "Votos" no seu Google Sheets se a planilha estiver vazia.

*(Obs: Para visualizar o Painel Admin, cadastre um participante no seu Google Sheets, defina o "Nivel de Acesso" como `Admin` e insira um telefone para logar com ele).*

## 🧪 Rodando os Testes Automatizados

Este projeto foi construído com a mentalidade TDD (Test-Driven Development). Uma ampla gama de testes unitários foi construída utilizando o `pytest` para garantir as regras de negócio e testar até mesmo a UI (AppTest do Streamlit).

Para rodar todos os testes, basta executar o seguinte comando a partir da pasta raiz do projeto:

```bash
python -m pytest tests/ -v
```

Isso processará os 147+ testes do sistema que validam o repositório, validação das dezenas de voto, login de participantes, serviços de contagem e os algoritmos geradores/otimizadores matemáticos.
