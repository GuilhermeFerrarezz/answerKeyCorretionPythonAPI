from src.core.gabarito import extrair_gabarito
if __name__ == "__main__":
    print("Iniciando extração...")

    nome_do_arquivo = "gabaritoEnemTeste.pdf"

    print(f"Lendo o arquivo: {nome_do_arquivo}\n")
        
    resultado = extrair_gabarito(nome_do_arquivo)

    print(resultado)