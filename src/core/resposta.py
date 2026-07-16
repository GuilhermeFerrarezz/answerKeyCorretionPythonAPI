import cv2
import json
import numpy as np

def ler_prova(caminho_imagem, caminho_json):
    img = cv2.imread(caminho_imagem)
    if img is None:
        print("Erro: Imagem não encontrada!")
        return {}

    img_debug = img.copy()
    h_img, w_img = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
  
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 21, 10)
    
    with open(caminho_json, 'r') as f:
        mapa = json.load(f)

    respostas = {}
    
    for q in sorted(mapa.keys(), key=int):
        alternativas = mapa[q]
        pontuacoes = {}
        
        for alt, c in alternativas.items():
            
            x = int(c['x'] * w_img)
            y = int(c['y'] * h_img)
            w = int(c['w'] * w_img)
            h = int(c['h'] * h_img)
            
           
            cv2.rectangle(img_debug, (x, y), (x+w, y+h), (0, 0, 255), 1)
            
            
            roi = thresh[y:y+h, x:x+w]
            
          
            r_h, r_w = roi.shape
            if r_h > 0 and r_w > 0:
                centro = roi[int(r_h*0.2):int(r_h*0.8), int(r_w*0.2):int(r_w*0.8)]
                pontuacoes[alt] = cv2.countNonZero(centro)
            else:
                pontuacoes[alt] = 0
        
    
        max_val = max(pontuacoes.values()) if pontuacoes else 0
     
        if max_val < 50: 
            estado = "BRANCO"
            selecao = None
        else:
         
            selecao = max(pontuacoes, key=pontuacoes.get)
            estado = "MARCADA"

        
        respostas[q] = {
            "estado": estado,
            "selecao": selecao,
            "densidades": pontuacoes
        }
            

    cv2.imwrite("debug_leitura.jpg", img_debug)
    print("Imagem de debug salva como 'debug_leitura.jpg'")
            
    return respostas

if __name__ == "__main__":
    resultado = ler_prova("3_alinhada_por_template.jpg", "gabarito_coordenadas.json")
    print(json.dumps(resultado, indent=4))