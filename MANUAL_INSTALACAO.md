# Manual de Instalacao - Oracle Fusion Shipping SOAP

## 1. Objetivo

Este mini sistema web executa o processo SOAP do Oracle Fusion Shipping usando o servico `processShipmentAction`.

O ActionCode padrao e `FD_ERROR`.

## 2. Estrutura dos arquivos

```text
oracle_shipping_soap_app/
├─ app.py
├─ requirements.txt
├─ Procfile
├─ render.yaml
├─ .env.example
├─ exemplo_shipments.csv
├─ MANUAL_INSTALACAO.md
├─ README.md
├─ templates/
│  └─ index.html
└─ static/
   ├─ app.js
   └─ styles.css
```

## 3. Como testar localmente

### 3.1 Instalar Python

Instale Python 3.11 ou superior.

### 3.2 Abrir terminal na pasta do projeto

Entre na pasta extraida:

```bash
cd oracle_shipping_soap_app
```

### 3.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3.4 Executar o sistema

```bash
python app.py
```

### 3.5 Abrir no navegador

Acesse:

```text
http://localhost:5000
```

## 4. Como usar a tela

1. Selecione o ambiente: DEV, TESTE ou PROD.
2. Informe a URL base do Oracle Fusion ou endpoint SOAP completo.
3. Informe o usuario.
4. Informe a senha.
5. Confirme o ActionCode padrao `FD_ERROR`.
6. Use o botao `Testar Conexao`.
7. Informe os Shipments manualmente ou importe o CSV.
8. Use o botao `Executar Processamento`.
9. Veja o retorno na tabela e nos logs.
10. Exporte o resultado para CSV ou Excel.

## 5. URL correta

URL base aceita:

```text
https://SEU_AMBIENTE.fa.ocs.oraclecloud.com
```

O sistema completa automaticamente para:

```text
https://SEU_AMBIENTE.fa.ocs.oraclecloud.com/fscmService/ShipmentService
```

Endpoint SOAP completo aceito:

```text
https://SEU_AMBIENTE.fa.ocs.oraclecloud.com/fscmService/ShipmentService
```

## 6. URL bloqueada

O sistema bloqueia URL de login ou IDCS contendo:

```text
identity.oraclecloud.com
/ui/v1/signin
idcs-
```

Mensagem exibida:

```text
A URL informada e uma URL de login/IDCS. Essa URL nao executa servico SOAP. Informe a URL do Oracle Fusion Apps ou o endpoint ShipmentService.
```

## 7. CSV de entrada

Exemplo:

```csv
Shipment,ActionCode
1672590,FD_ERROR
1672867,FD_ERROR
```

## 8. Publicar no Render

### 8.1 Criar repositorio no GitHub

1. Acesse GitHub.
2. Crie um repositorio chamado `oracle-shipping-soap`.
3. Envie todos os arquivos da pasta `oracle_shipping_soap_app`.

### 8.2 Criar Web Service no Render

1. Acesse Render.
2. Selecione `New`.
3. Selecione `Web Service`.
4. Conecte ao GitHub.
5. Escolha o repositorio `oracle-shipping-soap`.

### 8.3 Configuracao no Render

Use:

```text
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

O arquivo `render.yaml` tambem ja esta incluido para facilitar a configuracao.

### 8.4 Testar publicacao

Depois do deploy abrir a URL gerada pelo Render.

Exemplo:

```text
https://oracle-shipping-soap.onrender.com
```

## 9. Seguranca

- Nao colocar senha real no codigo.
- Nao salvar senha no navegador.
- Nao gravar senha em logs.
- Nao exibir senha em texto aberto.
- Em producao, usar variavel de ambiente, secret manager ou cofre de senha.
- O backend Flask executa a chamada SOAP para evitar CORS e exposicao direta da senha pelo navegador.

## 10. Observacao importante

Para executar contra o Oracle Fusion real, o servidor onde o sistema esta hospedado precisa ter acesso de rede ao endpoint Oracle Fusion e o usuario precisa ter permissao para consumir o servico SOAP de Shipping.
