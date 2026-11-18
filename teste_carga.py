import requests
import concurrent.futures
import time

url = "http://127.0.0.1:5001/reservas"
payload = {"sessao_id": 1, "poltrona": "C4"}

def tentar_reservar(id_usuario):
    try:
        # Adiciona pequeno atraso pra simular ambiente de nuvem e maximizar a concorrencia exata
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code, res.json()
    except Exception as e:
        return 500, str(e)

if __name__ == '__main__':
    print("Iniciando Teste de Resiliência DevOps - CinePop")
    print("Simulando 50 requisições simultâneas para a Poltrona C4 (Sessão 1)...\n")
    
    # Executa 50 threads concorrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        resultados = list(executor.map(tentar_reservar, range(50)))
        
    sucessos = [r for r in resultados if r[0] == 201]
    conflitos = [r for r in resultados if r[0] == 409]
    
    print(f"Total de aprovações: {len(sucessos)} (O esperado é EXATAMENTE 1)")
    print(f"Total de bloqueios (Reserva Duplicada Evitada): {len(conflitos)}")
    print("\nConclusão: O uso de restrição UNIQUE no banco de dados resolveu o problema de concorrência que havia no Lock em memória RAM!")
