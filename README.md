# 🚀 Siemens Point of Sales (POS) - Carga Retroativa Integrada

Um sistema robusto de backfill (carga retroativa) desenvolvido em Python e Flask para extrair dados de vendas do ERP Sankhya (Oracle DB) e integrá-los diretamente à API de Point of Sales da Siemens.

Este projeto foi desenhado para lidar com grandes volumes de dados de forma resiliente, contando com processamento em lote (batches), mecanismo de retry autônomo, e um dashboard de monitoramento em tempo real operado via Server-Sent Events (SSE).

---

## 🌟 Principais Funcionalidades

- **Extração e Mapeamento Inteligente**: Realiza queries avançadas no banco de dados Oracle para consolidar dados fiscais, de faturamento, filiais e parceiros (clientes), formatando-os rigorosamente de acordo com a especificação JSON exigida pela API Siemens.
- **Processamento em Lotes (Batching)**: Previne timeouts e erros `413 Request Too Long` fatiando requisições gigantescas em lotes menores e configuráveis (ex: 1000 registros).
- **Dashboard em Tempo Real**: Uma interface web interativa que exibe o progresso do envio, logs de diagnóstico e contagem de sucesso/erros instantaneamente usando SSE (Sem precisar de *polling*).
- **Mecanismo "Dry Run"**: Permite simular o envio localmente, logando as estruturas do JSON no terminal para validação de dados antes de efetivamente disparar requisições à Siemens.
- **Tratamento de Dados Nulos (NVL)**: Previne falhas de parsing nas pontas garantindo tipagem consistente, mesmo perante dados não preenchidos no ERP original.
- **Resiliência e Retry Backoff**: Caso a API fique instável ou o tráfego atinja limites (Rate Limit), o sistema aguarda um período exponencial seguro e tenta reprocessar automaticamente o batch falho.

---

## 🛠️ Tecnologias Utilizadas

**Backend:**
- **Python 3.x**
- **Flask** (Servidor HTTP e streaming SSE)
- **oracledb** (Conexão Oracle driver *thin*, sem necessidade de Oracle Client nativo)
- **Requests** (Requisições HTTP síncronas e robustas)

**Frontend:**
- **HTML5 / CSS3** (Vanilla, design dark-mode focado na experiência de monitoramento)
- **JavaScript (ES6)** (EventSource para o streaming dinâmico)

---

## 📁 Estrutura da Aplicação

```text
├── app.py                # Servidor principal (Flask), rotas REST, fila e gerência das Threads
├── db_oracle.py          # Conexão de banco e query principal (Motor de tratamento de dados)
├── siemens_api.py        # Wrapper do Client HTTP (Headers, Retry, Tratamento 201/400)
├── config.py             # Parser e concentrador de variáveis de ambiente (.env)
├── .env                  # Credenciais (Tokens, DB User/Pass) *Não versionado*
├── requirements.txt      # Dependências do pacote
└── templates/
    └── index.html        # Estrutura do Dashboard Frontend
```

---

## ⚙️ Como Configurar e Rodar Localmente

1. **Clone e Dependências**
   Certifique-se de estar utilizando um ambiente virtual (ex: `.venv`) e instale as libs:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuração do `.env`**
   Crie um arquivo `.env` na raiz do projeto com os seguintes parâmetros:
   ```env
   # Oracle Database
   ORA_USER=SEU_USUARIO
   ORA_PASS=SUA_SENHA
   ORA_DSN=SEU_HOST:PORTA/SERVICO

   # Siemens API
   SIEMENS_API_URL=https://api.pos.siemens.com/qua/create_record
   SIEMENS_API_TOKEN=seu_token_api_aqui

   # Configurações do Worker
   BATCH_SIZE=1000
   RETRY_MAX=3
   RETRY_BACKOFF=2
   ```

3. **Iniciando a Aplicação**
   No terminal, execute:
   ```bash
   python app.py
   ```
   Acesse a interface de operação no navegador através do endereço: `http://localhost:5000`

---

## 💡 Lições e Desafios (Para o Portfólio)

* **Tratamento de concorrência (Deadlocks):** Durante a criação do dashboard, a thread que enviava a carga concorria com a thread que publicava os eventos visuais no SSE. Isso foi resolvido ao implementar o uso de bloqueios reentrantes (`threading.RLock()`), preservando a estabilidade durante processos críticos de I/O.
* **Sobrecarga de Servidores de Terceiros:** A princípio a carga era monolítica, o que resultava no bloqueio da porta do servidor de destino (`413 Payload Too Large`). Foi arquitetada uma rotina de *Chunking* (particionamento de dados na memória do Python antes do disparo).
* **Ausência de Dados (Data Cleansing):** O ambiente do ERP comumente retorna registros parcialmente incompletos ou mesclados. A injeção de técnicas avançadas de `NVL` direto na ponte Oracle > Python protegeu o schema JSON de serialização indevida.

---

*Desenvolvido focado em engenharia de dados, monitoramento e integridade de APIs.*
