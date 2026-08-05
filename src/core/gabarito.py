import pdfplumber
import re

def extrair_gabarito(caminho_pdf, idioma_escolhido):
    gabarito = {}
    
    padrao_questao = re.compile(r"QUESTÃO\s+(\d+)\s+Resposta\s+([A-E])", re.IGNORECASE)
    padrao_idioma = re.compile(r"opção\s+(inglês|ingles|espanhol)", re.IGNORECASE)
    idioma_escolhido = idioma_escolhido.lower().replace('ê', 'e')
    idioma_atual = 'comum'
    try: 
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                
                if texto:
                    linhas = texto.split('\n')
                    
                    for linha in linhas:
                        match_idioma = padrao_idioma.search(linha)
                        if match_idioma:
                            idioma_atual = match_idioma.group(1).lower().replace('ê', 'e')
                            continue 
                        
    
                        match_questao = padrao_questao.search(linha)
                        if match_questao:
                            num = int(match_questao.group(1))
                            resp = match_questao.group(2).upper()
                            chave_limpa = str(num)
                            
                
                            if 1 <= num <= 5:
                                if idioma_atual == idioma_escolhido:
                                    gabarito[chave_limpa] = resp
                            else:
    
                                gabarito[chave_limpa] = resp
                                
        return gabarito
    except FileNotFoundError:
        #print(f"Erro: O aquivo '{caminho_pdf}' não foi encontrado")
        return None
    except Exception as e:
        #print(f"Erro inesperado ao ler o PDF: {e}")
        return None
    