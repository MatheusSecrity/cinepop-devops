import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SESSOES = {
    1: {"sala": 1}, 
    2: {"sala": 2}, 
    3: {"sala": 3}, 
    4: {"sala": 1},
    5: {"sala": 4},
    6: {"sala": 5}
}
FILEIRAS = ("A", "B", "C", "D", "E")
POLTRONAS_VALIDAS = {f"{f}{n}" for f in FILEIRAS for n in range(1, 9)}

DB_PATH = os.environ.get("DB_PATH", "banco_cinepop.db")

def obter_conexao():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) if os.path.dirname(DB_PATH) else None
    conn = obter_conexao()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao_id INTEGER,
            sala INTEGER,
            poltrona TEXT,
            status TEXT,
            UNIQUE(sessao_id, poltrona)
        )
    ''')
    conn.commit()
    conn.close()

inicializar_banco()

@app.get("/")
def inicio(): return jsonify({"servico": "CinePop - Mapa de Poltronas", "status": "online"}), 200

@app.get("/sessoes/<int:sessao_id>/poltronas")
def consultar_poltronas(sessao_id):
    if sessao_id not in SESSOES:
        return jsonify({"erro": "Sessão não encontrada."}), 404
    conn = obter_conexao()
    ocupadas = [linha["poltrona"] for linha in conn.execute('SELECT poltrona FROM reservas WHERE sessao_id = ?', (sessao_id,)).fetchall()]
    conn.close()
    
    mapa = []
    for poltrona in sorted(POLTRONAS_VALIDAS):
        mapa.append({"poltrona": poltrona, "status": "ocupada" if poltrona in ocupadas else "disponivel"})
    
    return jsonify({"sessao_id": sessao_id, "poltronas": mapa}), 200

@app.post("/reservas")
def reservar_poltrona():
    dados = request.get_json(silent=True)
    if not dados: return jsonify({"erro": "JSON invalido"}), 400
    
    sessao_id = dados.get("sessao_id")
    poltronas_raw = dados.get("poltronas") or ([dados.get("poltrona")] if dados.get("poltrona") else [])
    
    if not sessao_id or sessao_id not in SESSOES or not poltronas_raw:
        return jsonify({"erro": "Sessão ou poltronas inválidas."}), 400

    poltronas = [str(p).strip().upper() for p in poltronas_raw if str(p).strip().upper() in POLTRONAS_VALIDAS]

    if not poltronas:
        return jsonify({"erro": "Nenhuma poltrona válida enviada."}), 400

    conn = obter_conexao()
    reserva_ids = []
    sucesso = True

    try:
        conn.execute("BEGIN TRANSACTION")
        for poltrona in poltronas:
            cursor = conn.execute('INSERT INTO reservas (sessao_id, sala, poltrona, status) VALUES (?, ?, ?, ?)',
                                  (sessao_id, SESSOES[sessao_id]["sala"], poltrona, "reservada"))
            reserva_ids.append(cursor.lastrowid)
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        sucesso = False
    finally:
        conn.close()

    if not sucesso: 
        return jsonify({"erro": "Uma ou mais poltronas selecionadas já estão ocupadas."}), 409

    return jsonify({"mensagem": "Reserva efetuada com sucesso!", "reserva_ids": reserva_ids, "reserva_id": reserva_ids[0]}), 201

@app.get("/reservas/<int:reserva_id>")
def consultar_reserva(reserva_id):
    conn = obter_conexao()
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()
    conn.close()
    if reserva is None: return jsonify({"erro": "Reserva não encontrada."}), 404
    return jsonify(dict(reserva)), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
