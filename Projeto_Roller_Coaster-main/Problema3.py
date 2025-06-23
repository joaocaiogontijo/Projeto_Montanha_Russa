from simulacao_montanha_russa import executar_simulacao
if __name__ == "__main__":

    print("=" * 20 + " INICIANDO PROBLEMA 3: N CARROS " + "=" * 20)
    
    executar_simulacao(
        n=100,
        m=4,        
        C=10, 
        Tm=60,     
        Te=25,      
        Tp_min=10,
        Tp_max=20
    )