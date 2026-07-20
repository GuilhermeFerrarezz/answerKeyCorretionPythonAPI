from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import cv2
import os
import shutil
import numpy as np
from src.core.gabarito import extrair_gabarito
from src.core.scanner import alinhar_por_template
from src.core.resposta import ler_prova

app = FastAPI(title="API de Correção de Provas")

template_dia1 = cv2.imread('images/templateFinalDia1.png')
template_dia2 = cv2.imread('images/templateFinal.png')


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
@app.post("/corrigir-prova")
async def corrigir_prova_endpoint(
    imagem: UploadFile = File(...),
    pdf: UploadFile = File(...),
    dia: int = Form(...)
) :
    print(f"Recebendo arquivos: {imagem.filename} e {pdf.filename}")
    if dia not in [1, 2]:
        raise HTTPException(status_code=400, detail="O campo 'dia' deve ser 1 ou 2.")
    if dia == 1:
        template_referencia = template_dia1
    
    else:
        template_referencia = template_dia2

    
    
    
    
    caminho_pdf_temp = f"temp_{pdf.filename}"
    with open(caminho_pdf_temp, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)

    contents = await imagem.read()
    nparr = np.frombuffer(contents, np.uint8)
    imagem_torta = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    
    if imagem_torta is None:
        os.remove(caminho_pdf_temp)
        raise HTTPException(status_code=400, detail="A imagem enviada é inválida ou está corrompida.")
    if template_referencia is None:
        os.remove(caminho_pdf_temp)
        raise HTTPException(status_code=500, detail="Erro no servidor: Template de referência não encontrado.")
    
    try: 
        gabarito_oficial = extrair_gabarito(caminho_pdf_temp)
        img_alinhada = alinhar_por_template(imagem_torta, template_referencia)
        
        if (dia == 1): 
            respostas_aluno = ler_prova(img_alinhada, 'gabarito_coordenadasDia1.json')
        else: 
            respostas_aluno = ler_prova(img_alinhada, 'gabarito_coordenadas.json')
        os.remove(caminho_pdf_temp)
        return {
            "sucesso": True,
            "resumo": {
                "gabarito": gabarito_oficial,
                "respostas": respostas_aluno
            }
        }
    except Exception as e:
        if os.path.exists(caminho_pdf_temp): os.remove(caminho_pdf_temp)
        if os.path.exists("temp_alinhada.jpg"): os.remove("temp_alinhada.jpg")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    

    

    
    
    
    
    
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
 
    