import subprocess
import time
import sys

print("Iniciando Serviços do CinePop...")
p1 = subprocess.Popen([sys.executable, "servico1.py"])
p2 = subprocess.Popen([sys.executable, "servico2.py"])
p3 = subprocess.Popen([sys.executable, "servico3.py"])

print("Serviços online nas portas 5000, 5001 e 5002.")
print("Para parar, pressione Ctrl+C")

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    p1.terminate()
    p2.terminate()
    p3.terminate()
    print("Serviços encerrados.")
