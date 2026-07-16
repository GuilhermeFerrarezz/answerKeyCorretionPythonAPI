from src.core.gabarito import extrair_gabarito
from src.core.scanner import alinhar_por_template
from src.core.resposta import ler_prova
import cv2
if __name__ == "__main__":
    def verificar_erros(respostas_aluno, gabarito_oficial):
        questoes_erradas = []
        offset = 90
        
        for questao_oficial, correta in gabarito_oficial.items():
       
            q_num = int(questao_oficial)
            q_aluno = str(q_num - offset)
            
            aluno = respostas_aluno.get(q_aluno, {}).get('selecao')
            
            if aluno != correta:
                questoes_erradas.append(questao_oficial) 
                
        return len(questoes_erradas), questoes_erradas
    
    
    
    
    
    
    print("Iniciando extração...")
    nome_do_arquivo = "gabaritoMarco2Dia.pdf"
    imagem_torta = cv2.imread('respostaMarco2Dia.jpeg')
    template_referencia = cv2.imread('templateFinal.png')
    arquivo_alinhado = "alinhada_por_template.jpg"
    if imagem_torta is None:
        print(f"ERRO CRÍTICO: Não encontrei a imagem torta'. Verifique se o nome está escrito exatamente assim e se o ficheiro está na mesma pasta.")
        exit() 
    
    if template_referencia is None:
        print(f"ERRO CRÍTICO: Não encontrei o template")
        exit()

    print("Imagens carregadas com sucesso! Iniciando extração...")
    

    nome_do_arquivo = "gabaritoMarco2Dia.pdf"

    print(f"Lendo o arquivo: {nome_do_arquivo}\n")
        
    resultado = extrair_gabarito(nome_do_arquivo)
    
    img_alinhada = alinhar_por_template(imagem_torta, template_referencia)
    cv2.imwrite(arquivo_alinhado, img_alinhada)
    
    
    respostas = ler_prova(arquivo_alinhado, 'gabarito_coordenadas.json')

    print(resultado)
    print(respostas)
    
    total, quais = verificar_erros(respostas, resultado)

    print(f"Você errou {total} questões.")
    print(f"As questões que você errou foram: {quais}")
 
    