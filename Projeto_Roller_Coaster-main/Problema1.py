from simulacao_montanha_russa import executar_simulacao
if __name__ == "__main__":
    
    print("=" * 20 + " INICIANDO PROBLEMA 1: CARRO ÚNICO " + "=" * 20)
    
    executar_simulacao(
        n=65, 
        m=1, 
        C=5, 
        Tm=60,     
        Te=25,      
        Tp_min=10,
        Tp_max=20
    )