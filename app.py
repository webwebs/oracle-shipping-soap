import os
import html
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BLOCKED_URL_MARKERS = ["identity.oraclecloud.com", "/ui/v1/signin", "idcs-"]
DEFAULT_PATH = "/fscmService/ShipmentService"


def short_text(value, limit=500):
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def validate_and_normalize_url(input_url):
    if not input_url or not input_url.strip():
        raise ValueError("Informe a URL SOAP ou a URL base do Oracle Fusion.")

    url = input_url.strip()
    lower_url = url.lower()

    if any(marker in lower_url for marker in BLOCKED_URL_MARKERS):
        raise ValueError(
            "A URL informada é uma URL de login/IDCS. Essa URL nao executa servico SOAP. "
            "Informe a URL do Oracle Fusion Apps ou o endpoint ShipmentService."
        )

    if not lower_url.startswith(("https://", "http://")):
        url = "https://" + url

    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("URL invalida. Informe uma URL do Oracle Fusion Apps ou o endpoint ShipmentService.")

    path = parsed.path.rstrip("/")
    if path == "":
        url = f"{parsed.scheme}://{parsed.netloc}{DEFAULT_PATH}"
    elif not path.lower().endswith("/fscmservice/shipmentservice"):
        if "shipmentservice" not in path.lower():
            raise ValueError("URL SOAP invalida. Informe a URL base do Oracle Fusion Apps ou o endpoint /fscmService/ShipmentService.")

    return url


def build_soap_xml(action_code, shipment):
    action = html.escape((action_code or "FD_ERROR").strip())
    shipment_value = html.escape(str(shipment).strip())
    return f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\"
                  xmlns:ns1=\"http://xmlns.oracle.com/apps/scm/shipping/shipConfirm/deliveries/shipmentService/types/\">
   <soapenv:Header/>
   <soapenv:Body>
      <ns1:processShipmentAction>
         <ns1:apiVersionNumber>1.0</ns1:apiVersionNumber>
         <ns1:InitMsgList>T</ns1:InitMsgList>
         <ns1:ActionCode>{action}</ns1:ActionCode>
         <ns1:Shipment>{shipment_value}</ns1:Shipment>
      </ns1:processShipmentAction>
   </soapenv:Body>
</soapenv:Envelope>"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "oracle-shipping-soap"})


@app.route("/api/test-connection", methods=["POST"])
def test_connection():
    data = request.get_json(force=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"ok": False, "resultado": "ERRO", "message": "Informe usuario e senha."}), 400

    try:
        soap_url = validate_and_normalize_url(data.get("url"))
        wsdl_url = soap_url + "?WSDL"
        response = requests.get(wsdl_url, auth=(username, password), timeout=30)
        result = "SUCESSO" if 200 <= response.status_code <= 299 else "ERRO"
        return jsonify({
            "ok": 200 <= response.status_code <= 299,
            "urlTestada": wsdl_url,
            "statusHttp": response.status_code,
            "resultado": result,
            "retornoResumo": short_text(response.text, 500),
            "message": "Conexao validada com sucesso." if result == "SUCESSO" else "Falha ao validar conexao. Verifique URL, usuario, senha e permissao."
        })
    except ValueError as exc:
        return jsonify({"ok": False, "resultado": "ERRO", "message": str(exc)}), 400
    except requests.RequestException as exc:
        return jsonify({
            "ok": False,
            "urlTestada": data.get("url", ""),
            "statusHttp": "",
            "resultado": "ERRO CONEXAO",
            "retornoResumo": short_text(exc, 500),
            "message": "Erro de conexao ao testar o WSDL."
        }), 502


@app.route("/api/process", methods=["POST"])
def process_shipments():
    data = request.get_json(force=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    default_action = (data.get("defaultActionCode") or "FD_ERROR").strip()
    rows = data.get("shipments", [])

    if not username or not password:
        return jsonify({"ok": False, "message": "Informe usuario e senha."}), 400

    try:
        soap_url = validate_and_normalize_url(data.get("url"))
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    results = []
    for row in rows:
        shipment = str(row.get("shipment", "")).strip()
        action_code = (row.get("actionCode") or default_action or "FD_ERROR").strip()

        if not shipment:
            continue

        xml_payload = build_soap_xml(action_code, shipment)
        timestamp = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M:%S")

        try:
            response = requests.post(
                soap_url,
                data=xml_payload.encode("utf-8"),
                auth=(username, password),
                headers={
                    "Content-Type": "text/xml;charset=UTF-8",
                    "SOAPAction": "processShipmentAction",
                },
                timeout=60,
            )
            status_http = response.status_code
            resultado = "SUCESSO" if 200 <= response.status_code <= 299 else "ERRO"
            response_text = short_text(response.text, 1500)
        except requests.RequestException as exc:
            status_http = ""
            resultado = "ERRO CONEXAO"
            response_text = short_text(exc, 1500)

        results.append({
            "shipment": shipment,
            "actionCode": action_code,
            "statusHttp": status_http,
            "resultado": resultado,
            "respostaSoap": response_text,
            "dataHora": timestamp,
            "urlSoapUsada": soap_url,
            "xmlEnviado": xml_payload,
        })

    return jsonify({"ok": True, "results": results, "urlSoapUsada": soap_url})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
