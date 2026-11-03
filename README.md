# App simples para avaliar consultas no Datadog

App Flask + SQLite instrumentada com `ddtrace`, enviando traces para o Datadog Agent.

## Como rodar

1. Copie `.env.example` para `.env` e preencha `DD_API_KEY` (e `DD_SITE` se sua conta não for `datadoghq.com`).
2. Suba tudo:

   ```bash
   docker compose --env-file .env up --build
   ```

3. Gere tráfego (em outro terminal):

   ```bash
   python gerar_carga.py http://localhost:5000 200
   ```

4. Teste manualmente se quiser:

   ```bash
   curl "http://localhost:5000/produtos?nome=produto-1"
   curl http://localhost:5000/produtos/lenta
   curl http://localhost:5000/erro
   ```

## O que olhar no Datadog (1 a 2 minutos depois)

- **APM > Services > minha-app**: latência, throughput e taxa de erro por endpoint.
- **APM > Traces**: filtre por `service:minha-app`. Cada trace mostra os spans `sqlite` com a query executada e o tempo gasto.
  - `/produtos/lenta` aparece com a maior duração.
  - `/erro` aparece com erro (`no such table`).
- **Logs > Explorer**: logs do container, correlacionados aos traces (`DD_LOGS_INJECTION`).

## Sem Docker

```bash
pip install -r requirements.txt
# O Datadog Agent precisa estar rodando na máquina com APM habilitado
DD_SERVICE=minha-app DD_ENV=dev ddtrace-run python app.py
```

## Observações

- SQLite aparece no APM como spans de banco. O **Database Monitoring** (planos de execução, queries normalizadas) só está disponível para Postgres, MySQL, SQL Server, etc. Se quiser isso, troco o SQLite por Postgres no compose.
- Nunca versione o arquivo `.env` com a API key.
