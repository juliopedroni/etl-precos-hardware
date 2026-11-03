# 🛒 Pipeline ETL: Monitoramento Automatizado de Preços de Hardware

Este projeto é um pipeline de Engenharia de Dados (ETL) construído para extrair, limpar, armazenar e alertar automaticamente sobre variações de preços de hardwares em e-commerces.

O objetivo principal é monitorar produtos específicos e disparar uma notificação por E-mail (via SMTP) sempre que o preço sofrer uma queda percentual configurada na regra de negócio.

## 🛠️ Arquitetura e Tecnologias

1. **Extract:** `Python` + `Selenium` para web scraping dinâmico.
2. **Transform:** Expressões Regulares (`re`) e manipulação nativa em Python para limpeza de strings e conversão monetária.
3. **Load:** Ingestão dos dados estruturados no banco relacional `PostgreSQL` via `psycopg2`.
4. **Trigger & Notify:** Consulta ao histórico SQL e disparo de Webhook para o `n8n`, que orquestra e envia o alerta por e-mail.

## ⚙️ Stack Técnico
- **Linguagem:** Python 3.x
- **RPA / Scraping:** Selenium WebDriver
- **Banco de Dados:** PostgreSQL
- **Automação & Integração:** n8n via Webhooks
- **Protocolos:** HTTP (Requests), SMTP

## 🚀 Como Executar o Projeto

### 1. Configuração do Ambiente
```bash
git clone [https://github.com/juliopedroni/etl-precos-hardware.git](https://github.com/juliopedroni/etl-precos-hardware.git)
cd etl-precos-hardware
pip install -r requirements.txt