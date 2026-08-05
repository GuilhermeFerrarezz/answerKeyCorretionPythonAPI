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

@app.post("/corrigir-prova")
async def corrigir_prova_endpoint(
    image: UploadFile = File(...),
    pdf: UploadFile = File(...),
    day: int = Form(...),
    idioma: str= Form(...)
) :
    print(f"Recebendo arquivos: {image.filename} e {pdf.filename}")
    if day not in [1, 2]:
        raise HTTPException(status_code=400, detail="O campo 'dia' deve ser 1 ou 2.")
    if day == 1:
        template_referencia = template_dia1
    
    else:
        template_referencia = template_dia2

    
    
    
    
    caminho_pdf_temp = f"temp_{pdf.filename}"
    with open(caminho_pdf_temp, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)

    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    imagem_torta = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    
    if imagem_torta is None:
        os.remove(caminho_pdf_temp)
        raise HTTPException(status_code=400, detail="A imagem enviada é inválida ou está corrompida.")
    if template_referencia is None:
        os.remove(caminho_pdf_temp)
        raise HTTPException(status_code=500, detail="Erro no servidor: Template de referência não encontrado.")
    
    try: 
        gabarito_oficial = extrair_gabarito(caminho_pdf_temp, idioma)
        img_alinhada = alinhar_por_template(imagem_torta, template_referencia)
        
        if (day == 1): 
            respostas_aluno = ler_prova(img_alinhada, 'gabarito_coordenadas_dia_1_3.json', 1)
        else: 
            respostas_aluno = ler_prova(img_alinhada, 'gabarito_coordenadas_dia_2_3.json', 2)
        os.remove(caminho_pdf_temp)
        if respostas_aluno and gabarito_oficial: 
            return {
                "sucesso": True,
                "resumo": {
                    "gabarito": gabarito_oficial,
                    "respostas": respostas_aluno
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Erro no servidor: Não foi possível ler o gabarito.")
        
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
        
resultado = extrair_gabarito(nome_do_arquivo, 'ingles')
    
img_alinhada = alinhar_por_template(imagem_torta, template_referencia)
cv2.imwrite(arquivo_alinhado, img_alinhada)
    
    
respostas = ler_prova(arquivo_alinhado, 'gabarito_coordenadas.json')

print(resultado)
print(respostas)
    
 
    