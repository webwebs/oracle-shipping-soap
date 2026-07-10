# Oracle Fusion Shipping - Processamento SOAP

Mini sistema web em Flask para executar `processShipmentAction` do Oracle Fusion Shipping.

## Execucao local

```bash
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://localhost:5000
```

## Publicacao no Render

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Consulte o arquivo `MANUAL_INSTALACAO.md` para o passo a passo completo.
