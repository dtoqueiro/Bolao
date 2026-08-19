

# Documento de Requisitos: Plataforma Dinâmica de Bolão Lotofácil

## 1. Visão Geral do Projeto

Aplicativo web configurável para coleta de palpites, votação e geração automatizada de jogos de loteria (Lotofácil). O sistema utiliza a inteligência coletiva dos participantes para alimentar um algoritmo de desdobramento matemático (fechamento). O diferencial desta versão é a flexibilidade: o administrador pode parametrizar o tamanho do bolão, definindo o número de participantes, a quantidade de jogos a serem gerados e o tamanho de cada aposta (de 15 a 20 dezenas).

- **Público-Alvo:** Grupos de apostadores (tamanho configurável).

- **Estratégia Matemática:** Dinâmica, baseada na parametrização do Administrador (ex: $X$ jogos de $Y$ dezenas).

- **Emissão:** Geração de volantes otimizados com suporte à exportação para softwares de automação de impressão lotérica.

## 2. Stack Tecnológico (Sugerido)

- **Front-end & Back-end:** Python puro com framework **Streamlit**.

- **Persistência de Dados:** **Google Sheets** (via integração nativa `st.connection` ou biblioteca `gspread`).

- **Hospedagem:** Streamlit Community Cloud (Deploy gratuito via GitHub).

- **Motor Matemático:** Algoritmo combinatório dinâmico em Python (ou mapeamento de banco de matrizes pré-calculadas).

## 3. Regras da Matriz Ortogonal (Motor Dinâmico)

Como os parâmetros agora são variáveis, o sistema abandona a substituição estática ("de-para" fixo) e passa a utilizar um gerador de desdobramentos:

- Total de dezenas utilizadas no tabuleiro: 25.

- **Ranking de Dezenas:** O sistema manterá o saldo de votos, mas o "peso" ou frequência de cada dezena na matriz final será calculado dinamicamente com base na relação entre a quantidade de jogos desejada e o número de dezenas por jogo.

- **Otimização:** O algoritmo de desdobramento (fechamento) buscará sempre a máxima dispersão geométrica das dezenas mais votadas, minimizando a sobreposição entre os jogos para cobrir o maior número de combinações únicas possíveis.

## 4. Requisitos do Sistema

### 4.1. Autenticação e Acesso

- **[REQ-01]** O sistema deve solicitar o número de telefone (celular com DDD) como chave de acesso.

- **[REQ-02]** O sistema deve aplicar uma função de limpeza (Regex) na entrada do usuário, removendo espaços, parênteses, traços e códigos de país (ex: `+55`), garantindo uma string de 11 dígitos numéricos para comparação.

- **[REQ-03]** O sistema deve validar se o telefone limpo existe na lista de participantes cadastrados no banco de dados.

- **[REQ-04]** O sistema deve bloquear o acesso de usuários cujo telefone já conste com o status "Votou" na base de dados, a menos que a votação tenha sido reiniciada pelo administrador.

### 4.2. Coleta de Palpites (Votação)

- **[REQ-05]** O formulário deve permitir a seleção de no máximo **5 dezenas favoritas** (votos positivos).

- **[REQ-06]** O formulário deve permitir a seleção de no máximo **3 dezenas rejeitadas** (votos negativos).

- **[REQ-07]** O sistema deve impedir que a mesma dezena seja escolhida simultaneamente como favorita e rejeitada pelo mesmo usuário.

- **[REQ-08]** Ao submeter os palpites, o sistema deve gravar os dados no banco e alterar o status do participante para "Votou".

### 4.3. Motor de Pontuação e Geração (Backend)

- **[REQ-09]** O sistema deve calcular o saldo de cada uma das 25 dezenas aplicando a fórmula: `Saldo = (Votos Positivos * 1) + (Votos Negativos * -1)`.

- **[REQ-10]** O sistema deve ranquear as dezenas e aplicar o seguinte critério de desempate técnico:
1. Menor número de votos negativos absolutos.

2. Maior número de votos positivos absolutos.

3. Ordem crescente da dezena.
- **[REQ-11]** O sistema deve ler as variáveis de configuração do bolão (quantidade de jogos e dezenas por jogo) e alimentar o módulo de fechamento matemático com o ranking de dezenas gerado.

- **[REQ-12]** O módulo matemático deve gerar a matriz final distribuindo as dezenas do topo do ranking com maior frequência (maior prioridade) e as dezenas do fundo do ranking com menor frequência.

### 4.4. Painel do Administrador e Parametrização Geral

- **[REQ-13]** O sistema deve ter variáveis de estado global gerenciadas pelo Administrador (Status, Quórum, Qtd_Jogos, Qtd_Dezenas).

- **[REQ-14]** **Modo Administrador:** O login com um telefone com privilégios de "Admin" concederá acesso a um painel de controle exclusivo na interface.

- **[REQ-15]** O Painel do Administrador deve permitir as seguintes **Configurações da Campanha**:

- **Definir Quórum:** Estabelecer o número de participantes do bolão atual (gatilho de encerramento automático).

- **Definir Estratégia:** Configurar a **Quantidade de Jogos** (ex: 10) e a **Quantidade de Dezenas por Jogo** (ex: 15, 16, 17, etc.).

- **[REQ-16]** O Painel do Administrador deve permitir as seguintes **Ações de Gestão**:

- **Cadastrar Participantes:** Inserir Nome e Telefone de novos membros.

- **Editar Telefones:** Atualizar dados cadastrados incorretamente.

- **Refazer Votação (Reset):** Apagar os palpites de um usuário específico e zerar seu status.

- **Encerrar Bolão (Manual):** Botão para forçar o status para `FECHADO` antes de atingir o quórum estipulado.

- **[REQ-17]** **Encerramento Automático:** Se o banco de dados registrar um número de votos concluídos igual ao "Quórum" definido no painel, o sistema altera o estado para `FECHADO` automaticamente.

### 4.5. Tela de Resultados e Exportação

- **[REQ-18]** Quando o status for `FECHADO`, a tela de votação é substituída pela tela de "Resultados", exibindo o ranking final e os jogos gerados pela matriz dinâmica.

- **[REQ-19]** O sistema deve disponibilizar um botão de **Download dos Jogos**.

- **[REQ-20]** O arquivo baixado deve ser no formato `.txt`, estruturado especificamente para compatibilidade com o software **COLOG** (cada linha representando um jogo, com as dezenas separadas por espaços simples).

## 5. Planejamento Passo a Passo (Roadmap de Implementação)

### Fase 1: Estruturação dos Dados Dinâmicos (Planilha)

1. Criar a aba `Participantes` com colunas: `Nome`, `Telefone_Limpo`, `Status_Voto`, `Nivel_Acesso`.

2. Criar a aba `Votos` com colunas: `Telefone_Limpo`, `Dezenas_Positivas`, `Dezenas_Negativas`, `DataHora`.

3. Criar a aba `Config` estruturada como chave-valor para suportar a parametrização:
- `Status` = `ABERTO`

- `Quorum_Alvo` = `23`

- `Qtd_Jogos` = `10`

- `Dezenas_Por_Jogo` = `16`

### Fase 2: Configuração do Ambiente e Front-end Básico

1. Inicializar ambiente Python e instalar bibliotecas (`streamlit`, `pandas`, biblioteca de combinações iterertools/algoritmos).

2. Configurar credenciais do Google Sheets.

3. Desenvolver a tela de login via Regex para telefone.

4. Programar a leitura do estado global (Status) da aba `Config`.

### Fase 3: O Painel do Administrador (Parametrização e Gestão)

1. Implementar renderização condicional da aba "Painel de Controle" baseada no `Nivel_Acesso`.

2. Desenvolver a interface para o Admin editar `Quorum_Alvo`, `Qtd_Jogos` e `Dezenas_Por_Jogo` (gravando as mudanças na aba `Config`).

3. Criar formulários de Gestão de Usuários (Cadastrar novo, Editar telefone, Resetar voto de um participante).

4. Adicionar botão "Encerrar Votação Manual".

### Fase 4: Lógica de Votação e Regras

1. Construir os componentes visuais para a escolha das dezenas (com limites de 5 e 3).

2. Criar validações anti-interseção.

3. Implementar a gravação no Google Sheets e checagem de Encerramento Automático (`if votos_recebidos == Quorum_Alvo: fechar_bolao()`).

### Fase 5: O Motor Matemático Dinâmico (Core Upgrade)

1. Escrever função de consolidação e ranking (cálculo de saldo e critérios de desempate técnico).

2. Desenvolver ou integrar o **Módulo de Fechamento Matemático Dinâmico**. Este algoritmo deverá aceitar três inputs: o ranking de dezenas, o número de jogos e o tamanho do jogo.

3. O algoritmo deve distribuir as variáveis otimizando a dispersão para evitar sobreposições (usando heurísticas de cobertura ou geradores combinatórios).

### Fase 6: Tela de Resultados, Exportação COLOGA e Deploy

1. Desenvolver a view `FECHADO`, exibindo o ranking visual das dezenas.

2. Renderizar os $X$ jogos de $Y$ dezenas gerados na tela.

3. Implementar função de formatação do TXT (padrão COLOGA) baseada no array dinâmico e adicionar o botão `st.download_button`.

4. Deploy no Streamlit Community Cloud e geração da URL pública.
