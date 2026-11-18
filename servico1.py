from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

filmes = [
    {
        "id": 1,
        "titulo": "Interestelar",
        "genero": "Ficção científica",
        "duracao_minutos": 169,
        "classificacao": "10 anos",
        "sinopse": "Uma equipe viaja pelo espaço em busca de um novo lar para a humanidade.",
        "imagem": "imagens/interestelar.jpg"
    },
    {
        "id": 2,
        "titulo": "Divertida Mente 2",
        "genero": "Animação",
        "duracao_minutos": 96,
        "classificacao": "Livre",
        "sinopse": "Riley enfrenta novas emoções durante a adolescência.",
        "imagem": "imagens/divertidamente2.jpg"
    },
    {
        "id": 3,
        "titulo": "Batman",
        "genero": "Ação",
        "duracao_minutos": 176,
        "classificacao": "14 anos",
        "sinopse": "Batman investiga uma série de crimes que ameaça Gotham City.",
        "imagem": "imagens/batman.jpg"
    },
    {
        "id": 4,
        "titulo": "Avatar: O Caminho da Água",
        "genero": "Ficção / Ação",
        "duracao_minutos": 192,
        "classificacao": "12 anos",
        "sinopse": "Jake Sully e Neytiri exploram as regiões desconhecidas dos oceanos de Pandora.",
        "imagem": "imagens/avatar.jpg"
    },
    {
        "id": 5,
        "titulo": "O Poderoso Chefão",
        "genero": "Drama / Crime",
        "duracao_minutos": 175,
        "classificacao": "16 anos",
        "sinopse": "A saga da família Corleone na preservação de seu império mafioso nos EUA.",
        "imagem": "imagens/poderoso_chefao.jpg"
    }
]

sessoes = [
    {"id": 1, "filme_id": 1, "data": "2026-11-05", "horario": "18:30", "sala": 1, "idioma": "Legendado"},
    {"id": 2, "filme_id": 1, "data": "2026-11-05", "horario": "21:30", "sala": 2, "idioma": "Dublado"},
    {"id": 3, "filme_id": 2, "data": "2026-11-05", "horario": "15:00", "sala": 3, "idioma": "Dublado"},
    {"id": 4, "filme_id": 3, "data": "2026-11-05", "horario": "20:00", "sala": 1, "idioma": "Legendado"},
    {"id": 5, "filme_id": 4, "data": "2026-11-05", "horario": "17:00", "sala": 4, "idioma": "3D Dublado"},
    {"id": 6, "filme_id": 5, "data": "2026-11-05", "horario": "21:00", "sala": 5, "idioma": "Legendado VIP"}
]

@app.get("/")
def inicio(): return jsonify({"servico": "CinePop - Cartaz", "status": "online"}), 200

@app.get("/filmes")
def listar_filmes(): return jsonify(filmes), 200

@app.get("/sessoes")
def listar_sessoes():
    data = request.args.get("data")
    resultado = sessoes if not data else [s for s in sessoes if s["data"] == data]
    resposta = []
    for sessao in resultado:
        filme = next((f for f in filmes if f["id"] == sessao["filme_id"]), None)
        item = dict(sessao)
        item["filme"] = filme["titulo"] if filme else "Não encontrado"
        item["imagem"] = filme["imagem"] if (filme and "imagem" in filme) else ""
        item["sinopse"] = filme["sinopse"] if (filme and "sinopse" in filme) else ""
        resposta.append(item)
    return jsonify(resposta), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
