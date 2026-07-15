import pdfplumber
import re

def extrair_gabarito(caminho_pdf):
    gabarito = {}
    
    padrao = re.compile(r"QUESTÃO\s+(\d+)\s+Resposta\s+([A-E])", re.IGNORECASE)
    
    try: 
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                
                if texto:
                    resultados = padrao.findall(texto)
                    for num, resp in resultados:
                        gabarito[num] = resp.upper()
        return gabarito
    except FileNotFoundError:
        print(f"Erro: O aquivo '{caminho_pdf}' não foi encontrado")
        return None
    except Exception as e:
        print(f"Erro inesperado ao ler o PDF: {e}")
        return None
    