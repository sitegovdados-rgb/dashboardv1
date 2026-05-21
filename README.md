# 📊 Painel de Monitoramento do Programa Cidade Integrada (Urbanismo Social)

Este repositório contém uma aplicação web interativa desenvolvida com **Streamlit**, **Pandas** e **Plotly** para monitorar e analisar políticas públicas do **Programa Cidade Integrada** (PCI - Governo do Estado do Rio de Janeiro). O foco principal do dashboard está na abordagem do **Urbanismo Social**, integrando ações de desenvolvimento social e intervenções de infraestrutura física nas favelas atendidas.

---

## 🚀 Demonstração Visual e Funcionalidades

O dashboard oferece as seguintes análises estruturadas:

1. **Painel Geral Integrado (Visão Holística)**:
   * **KPIs Globais**: Investimentos totais, quantidade de ações sociais ativas, população beneficiada estimada e índices gerais de execução física.
   * **Mapa Interativo (Plotly Mapbox)**: Georeferenciamento das comunidades atendidas (como Jacarezinho, Manguinhos, Muzema, Rio das Pedras e PPG), exibindo bolhas proporcionais ao investimento, quantidade de ações ou beneficiados, e categorizadas por cor de acordo com o eixo (Social vs. Urbanismo).
   * **Gráfico de Integração**: Comparativo de correlação entre quantidade de ações sociais e investimento em obras por região do PCI.

2. **Eixo de Desenvolvimento Social**:
   * **Ações por Categoria**: Classificação automática de iniciativas (Esporte e Lazer, Cultura e Arte, Saúde e Bem-Estar, Qualificação e Renda, Serviços e Assistência) via processamento de texto.
   * **Ranking de Órgãos**: Gráficos com as principais secretarias/organizações responsáveis.
   * **Matriz de Gaps de Coleta de Dados**: Monitoramento de transparência cadastral (dados de gênero, raça, idade, renda, etc.) através de gráficos de barras empilhadas e um **Mapa Térmico (Heatmap)** interativo para auditar a maturidade de dados por projeto.

3. **Eixo de Urbanismo e Obras**:
   * **Monitoramento Orçamentário**: Divisão de investimentos previstos vs. realizados por sub-eixo (Saneamento, Habitação, Mobilidade, Espaços Públicos, Segurança/Defesa Civil) e região.
   * **Cronograma e Status**: Acompanhamento do status físico-financeiro (Concluído, Em execução, Bloqueada, Planejada) das obras de infraestrutura.

4. **Exploração Avançada e Download**:
   * **Filtros Dinâmicos Cruzados**: Filtre toda a base por termos livres, órgãos e eixos específicos na própria página.
   * **Central de Download**: Baixe os dados de sua análise filtrada em formato `.csv` ou planilha formatada do `.xlsx` (Excel).
   * **Inspetor Detalhado de Projetos**: Um card interativo que permite escolher um projeto individual e verificar todas as suas informações de cronograma, responsáveis e checklist de dados cadastrais.

---

## 📂 Estrutura de Arquivos do Projeto

```
dashboardv1-main/
│
├── .streamlit/
│   └── config.toml               # Configurações de design visual e limites do Streamlit
│
├── app.py                        # Aplicação principal modularizada e estilizada
├── dashboard-social-geral.csv    # Dados reais das iniciativas sociais do PCI
├── dashboard-urbanismo-geral.csv # Dados realistas de obras e infraestrutura (Saneamento, Encostas, LED)
├── requirements.txt              # Bibliotecas Python necessárias
└── README.md                     # Manual de documentação do sistema (Este arquivo)
```

---

## 🎨 Identidade Visual e Temas

O dashboard foi estilizado com foco em uma experiência **Premium e Institucional**:
* **Tema Padrão**: Dark Mode (Slate `#0F172A` e Dark Blue `#1E293B`).
* **Cor Primária/Destaque**: Verde Esmeralda (`#00D4B2`) - Representa transformação urbana, sustentabilidade e meio ambiente.
* **Cor de Apoio**: Azul Cobalto (`#1E3A8A`) e Roxo suave (`#6366F1`) para diferenciar os eixos do programa.
* **CSS Customizado**: Cards com efeitos de reflexo (glassmorphism), animação suave no cursor (hover transition) e tipografia moderna.

---

## 📤 Formatos de Upload Suportados (CSV & Excel)

O painel permite que gestores públicos façam upload de bases atualizadas tanto em formato **CSV** quanto **Excel** (`.xlsx`, `.xls`):

*   **Leitura Inteligente**: O sistema detecta a extensão automaticamente e seleciona a biblioteca correta (`openpyxl` ou `xlrd` para planilhas Excel e o parser nativo para arquivos delimitados).
*   **Gestão de Múltiplas Abas**: Ao subir uma pasta de trabalho Excel com várias abas (*sheets*), a barra lateral exibirá dinamicamente uma caixa de seleção para escolher qual aba ler.
*   **Validação de Esquemas**: Garante que o dashboard não quebre mesmo em uploads incorretos.

### Layout Recomendado das Colunas:
*   **Base Social**: Deve conter as colunas: `Tarefa`, `Região (PCI)`, `Localidade Específica`, `Status`, `Tipo` e as colunas de dados socioeconômicos (ex: `Possui Dados de Gênero`, `Possui Dados de Cor/Raça`, etc.).
*   **Base de Urbanismo**: Deve conter as colunas: `Tarefa`, `Região (PCI)`, `Localidade Específica`, `Status`, `Tipo`, `Investimento Previsto (R$)`, `Investimento Realizado (R$)` e `Qtd. Total`.

---

## 💻 Como Executar Localmente

Siga o passo a passo para rodar o projeto em sua máquina:

### 1. Pré-requisitos
Certifique-se de ter o Python 3.9 ou superior instalado em seu sistema.

### 2. Clonar ou Baixar o Repositório
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/cidade-integrada-dashboard.git
cd cidade-integrada-dashboard
```

### 3. Criar Ambiente Virtual (Recomendado)
* **Windows**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS/Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Executar a Aplicação
```bash
streamlit run app.py
```
A aplicação abrirá automaticamente no seu navegador padrão no endereço local `http://localhost:8501`.

---

## ☁️ Deploy no Streamlit Community Cloud

Para disponibilizar o painel publicamente na nuvem gratuita do Streamlit:

1. **Subir para o GitHub**:  
   Crie um repositório no seu perfil do GitHub e envie os arquivos do projeto (incluindo a pasta `.streamlit` com o `config.toml`).
   
2. **Conectar ao Streamlit**:  
   Acesse [share.streamlit.io](https://share.streamlit.io/) e faça login utilizando sua conta do GitHub.
   
3. **Configurar o Aplicativo**:  
   * Clique em **"Create App"** ou **"New App"**.
   * Selecione o repositório do projeto, a branch (ex: `main` ou `master`).
   * No campo **"Main file path"**, insira `app.py`.
   * Clique em **"Deploy!"**.

4. **Pronto!**  
   Após alguns instantes de compilação das dependências, o Streamlit fornecerá uma URL pública permanente para o seu dashboard institucional.