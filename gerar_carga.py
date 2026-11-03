"""Gera tráfego para a app, para que o Datadog tenha dados para avaliar.

Uso: python gerar_carga.py [URL_BASE] [QTD_REQUISICOES]
"""
import random
import sys
import time
import urllib.error
import urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
total = int(sys.argv[2]) if len(sys.argv) > 2 else 200

# Peso maior para consultas rápidas, algumas lentas e poucos erros
rotas = (
    ["/produtos?nome=1"] * 6
    + ["/produtos?nome=produto-2"] * 3
    + ["/produtos/lenta"] * 2
    + ["/erro"] * 1
)

for i in range(total):
    rota = random.choice(rotas)
    try:
        with urllib.request.urlopen(base + rota, timeout=30) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:  # noqa: BLE001
        status = f"falha ({e})"
    print(f"{i + 1:>4} {rota:<30} -> {status}")
    time.sleep(random.uniform(0.05, 0.3))
