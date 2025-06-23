import threading
import time
import random
from collections import deque

N_PASSAGEIROS = 0
N_CARROS = 0
CAPACIDADE_CARRO = 0
TEMPO_PASSEIO = 0
TEMPO_EMBARQUE_DESEMBARQUE = 0
INTERVALO_CHEGADA_MIN = 0
INTERVALO_CHEGADA_MAX = 0

turnos_carros = []
semaforo_desembarque = []
semaforo_carro_vazio = []
print_lock = threading.Lock()
fila_de_espera = deque()
lock_fila_espera = threading.Lock()
portao_de_embarque_lock = threading.Lock()
tempos_de_espera = []
lock_tempos_espera = threading.Lock()
passageiros_transportados = 0
lock_passageiros_transportados = threading.Lock()
tempo_total_simulacao = 0
tempo_total_carros_em_movimento = 0
lock_tempo_movimento = threading.Lock()

def passageiro(id_passageiro):
    global passageiros_transportados

    tempo_chegada = time.time()
    
    with print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] Passageiro {id_passageiro} chegou e entrou na fila.")

    meu_semaforo = threading.Semaphore(0)
    id_carro_para_embarcar_ref = [-1] 

    with lock_fila_espera:
        fila_de_espera.append((id_passageiro, meu_semaforo, id_carro_para_embarcar_ref, tempo_chegada))
    
    meu_semaforo.acquire()
    id_carro_para_embarcar = id_carro_para_embarcar_ref[0]

    semaforo_desembarque[id_carro_para_embarcar].acquire()

    with print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] Passageiro {id_passageiro} desembarcou do Carro {id_carro_para_embarcar}.")
    
    if semaforo_desembarque[id_carro_para_embarcar]._value == 0:
        semaforo_carro_vazio[id_carro_para_embarcar].release()

    with lock_passageiros_transportados:
        passageiros_transportados += 1

def carro(id_carro):
    global tempo_total_carros_em_movimento

    while passageiros_transportados < N_PASSAGEIROS:
        
        turnos_carros[id_carro].acquire()

        if passageiros_transportados >= N_PASSAGEIROS:
            turnos_carros[(id_carro + 1) % N_CARROS].release()
            break
        
        while len(fila_de_espera) < CAPACIDADE_CARRO:
            if passageiros_transportados >= N_PASSAGEIROS: break
            time.sleep(0.2)
        if passageiros_transportados >= N_PASSAGEIROS:
            turnos_carros[(id_carro + 1) % N_CARROS].release()
            break

        with portao_de_embarque_lock:
            with print_lock:
                print(f"[{time.strftime('%H:%M:%S')}] Carro {id_carro} começou o embarque.")

            passageiros_nesta_viagem = []
            for _ in range(CAPACIDADE_CARRO):
                with lock_fila_espera:
                    passageiros_nesta_viagem.append(fila_de_espera.popleft())

            for id_p, sem_p, ref_carro_p, tempo_chegada_p in passageiros_nesta_viagem:
                tempo_saida_fila = time.time()
                tempo_espera = tempo_saida_fila - tempo_chegada_p
                with lock_tempos_espera:
                    tempos_de_espera.append(tempo_espera)
                
                with print_lock:
                    print(f"[{time.strftime('%H:%M:%S')}] Passageiro {id_p} embarcou no Carro {id_carro}.")
                
                ref_carro_p[0] = id_carro
                sem_p.release()
        
        time.sleep(TEMPO_EMBARQUE_DESEMBARQUE)

        with print_lock:
            print(f"[{time.strftime('%H:%M:%S')}] Carro {id_carro} começou o passeio.")

        time.sleep(TEMPO_PASSEIO)

        with lock_tempo_movimento:
            global tempo_total_carros_em_movimento
            tempo_total_carros_em_movimento += TEMPO_PASSEIO

        with print_lock:
            print(f"[{time.strftime('%H:%M:%S')}] Carro {id_carro} retornou e começou o desembarque.")
        for _ in range(CAPACIDADE_CARRO):
            semaforo_desembarque[id_carro].release()

        time.sleep(TEMPO_EMBARQUE_DESEMBARQUE)

        if CAPACIDADE_CARRO > 0:
            semaforo_carro_vazio[id_carro].acquire()

        proximo_carro = (id_carro + 1) % N_CARROS
        turnos_carros[proximo_carro].release()

def executar_simulacao(n, m, C, Tm, Te, Tp_min, Tp_max):
    global N_PASSAGEIROS, N_CARROS, CAPACIDADE_CARRO, TEMPO_PASSEIO, TEMPO_EMBARQUE_DESEMBARQUE
    global INTERVALO_CHEGADA_MIN, INTERVALO_CHEGADA_MAX
    
    N_PASSAGEIROS = n
    N_CARROS = m
    CAPACIDADE_CARRO = C
    TEMPO_PASSEIO = Tm
    TEMPO_EMBARQUE_DESEMBARQUE = Te
    INTERVALO_CHEGADA_MIN = Tp_min
    INTERVALO_CHEGADA_MAX = Tp_max

    global tempos_de_espera, passageiros_transportados, tempo_total_carros_em_movimento
    global fila_de_espera, turnos_carros, semaforo_desembarque, semaforo_carro_vazio
    global portao_de_embarque_lock

    tempos_de_espera = []
    passageiros_transportados = 0
    tempo_total_carros_em_movimento = 0
    fila_de_espera.clear()
    portao_de_embarque_lock = threading.Lock()

    turnos_carros = [threading.Semaphore(1 if i == 0 else 0) for i in range(N_CARROS)]
    semaforo_desembarque = [threading.Semaphore(0) for _ in range(N_CARROS)]
    semaforo_carro_vazio = [threading.Semaphore(0) for _ in range(N_CARROS)]
    
    print("-" * 40)
    print(f"Número de passageiros: {N_PASSAGEIROS}")
    print(f"Número de carros: {N_CARROS}")
    print(f"Capacidade do carro: {CAPACIDADE_CARRO}")
    print("-" * 40)

    inicio_simulacao = time.time()

    threads = []
    
    for i in range(N_CARROS):
        thread_carro = threading.Thread(target=carro, args=(i,))
        threads.append(thread_carro)
        thread_carro.start()

    for i in range(N_PASSAGEIROS):
        thread_passageiro = threading.Thread(target=passageiro, args=(i,))
        threads.append(thread_passageiro)
        thread_passageiro.start()
        
        tempo_de_espera = random.uniform(INTERVALO_CHEGADA_MIN, INTERVALO_CHEGADA_MAX)
        time.sleep(tempo_de_espera)

    for t in threads:
        t.join()

    fim_simulacao = time.time()
    tempo_total_simulacao = fim_simulacao - inicio_simulacao
    
    print("\n" + "-" * 40)
    print("Relatório:")
    if tempos_de_espera:
        tempo_min = min(tempos_de_espera)
        tempo_max = max(tempos_de_espera)
        tempo_medio = sum(tempos_de_espera) / len(tempos_de_espera)
        print(f"Tempo mínimo de espera na fila: {tempo_min:.2f} seg")
        print(f"Tempo máximo de espera na fila: {tempo_max:.2f} seg")
        print(f"Tempo médio de espera na fila: {tempo_medio:.2f} seg")
    else:
        print("Nenhum passageiro registrou tempo de espera.")

    if tempo_total_simulacao > 0:
        eficiencia = (tempo_total_carros_em_movimento / tempo_total_simulacao) * 100
        print(f"Eficiência do(s) carro(s): {eficiencia:.2f}% (Tempo em movimento / Tempo total)")
    else:
        print("Não foi possível calcular a eficiência.")
    print("-" * 40 + "\n")