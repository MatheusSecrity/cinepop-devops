import os
from threading import Lock
from itertools import count
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SERVICO_RESERVAS_URL = os.environ.get("SERVICO_RESERVAS_URL", "http://127.0.0.1:5001")
pagamentos = {}
pagamentos_por_reserva = {}
proximo_id = count(1)
bloqueio_pagamentos = Lock()

@app.get("/")
def inicio(): return jsonify({"servico": "CinePop - Pagamentos", "status": "online"}), 200

@app.post("/pagamentos")
def realizar_pagamento():
    dados = request.get_json(silent=True) or {}
    reserva_ids = dados.get("reserva_ids") or ([dados.get("reserva_id")] if dados.get("reserva_id") else [])
    valor = float(dados.get("valor", 0))
    
    if not reserva_ids:
        return jsonify({"erro": "Nenhuma reserva informada"}), 400

    # 1. Valida todas as reservas no Servico 2
    poltronas_confirmadas = []
    try:
        for rid in reserva_ids:
            resposta = requests.get(f"{SERVICO_RESERVAS_URL}/reservas/{rid}", timeout=5)
            if resposta.status_code != 200:
                return jsonify({"erro": f"Reserva {rid} invalida ou nao encontrada"}), 404
            poltronas_confirmadas.append(resposta.json().get("poltrona"))
    except Exception:
        return jsonify({"erro": "Erro de conexao com o Servico 2"}), 502

    # 2. Processa pagamento
    with bloqueio_pagamentos:
        for rid in reserva_ids:
            if rid in pagamentos_por_reserva:
                return jsonify({"erro": f"Pagamento ja efetuado para a reserva {rid}"}), 409
            
        pagamento_id = next(proximo_id)
        pagamento = {
            "pagamento_id": pagamento_id,
            "reserva_ids": reserva_ids,
            "poltronas": poltronas_confirmadas,
            "valor": f"{valor:.2f}",
            "status": "aprovado"
        }
        pagamentos[pagamento_id] = pagamento
        for rid in reserva_ids:
            pagamentos_por_reserva[rid] = pagamento_id
        
    return jsonify({"mensagem": "Pagamento simulado aprovado", "pagamento": pagamento}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
