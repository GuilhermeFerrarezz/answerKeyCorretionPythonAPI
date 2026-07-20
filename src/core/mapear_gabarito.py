import cv2
import numpy as np
import json

def gerar_mapa_coordenadas(imagem_template_caminho):
  
    template = cv2.imread(imagem_template_caminho)
    if template is None:
        print(f"Erro: Não foi possível carregar a imagem em: {imagem_template_caminho}")
        return

    # 2. Padronizar largura (1200px)
    largura_padrao = 1200
    proporcao = largura_padrao / float(template.shape[1])
    altura_padrao = int(template.shape[0] * proporcao)
    template_redim = cv2.resize(template, (largura_padrao, altura_padrao))

    
    gray = cv2.cvtColor(template_redim, cv2.COLOR_BGR2GRAY)
 
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 31, 12
    )
    
    cv2.imwrite("debug_threshold.jpg", thresh)

    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    candidatos = []
    limite_cabecalho_y = altura_padrao * 0.35 
    
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        
     
        if w == 0 or h == 0: continue
        solidez = float(area) / (w * h)
        aspect_ratio = w / float(h)
        
        if y < limite_cabecalho_y:
            continue


        if 14 <= w <= 35 and 14 <= h <= 25 and 0.75 <= aspect_ratio <= 1.25 and 0.6 < solidez < 0.95:
            candidatos.append((x, y, w, h))


    candidatos = sorted(candidatos, key=lambda b: b[2]*b[3], reverse=True)
    
    bolhas_unicas = []
    for c in candidatos:
        x, y, w, h = c
        cx, cy = x + w/2, y + h/2
        sobrepoe = False
        
        for b in bolhas_unicas:
            bx, by, bw, bh = b
            bcx, bcy = bx + bw/2, by + bh/2

            if np.sqrt((cx - bcx)**2 + (cy - bcy)**2) < 16:
                sobrepoe = True
                break
                
        if not sobrepoe:
            bolhas_unicas.append(c)

    bolhas_finais = []
    for i, c1 in enumerate(bolhas_unicas):
        x1, y1, w1, h1 = c1
        tem_vizinho = False
        
        for j, c2 in enumerate(bolhas_unicas):
            if i == j:
                continue
            x2, y2, w2, h2 = c2
            
            dist_y = abs(y1 - y2)
            dist_x = abs(x1 - x2)
            
            if dist_y <= 9 and 18 <= dist_x <= 35:
                tem_vizinho = True
                break
                
        if tem_vizinho:
            bolhas_finais.append(c1)


    imagem_debug = template_redim.copy()
    for (x, y, w, h) in bolhas_finais:
        cv2.circle(imagem_debug, (int(x + w/2), int(y + h/2)), int(w/2), (0, 255, 0), 2)
        
    cv2.imwrite("debug_contornos.jpg", imagem_debug)
            
    print(f"\nTotal de bolhas detetadas: {len(bolhas_finais)} (Esperado: 450)")
    
    if len(bolhas_finais) != 450:
        print("\n[AVISO] O número de bolhas detetadas ainda não é 450.")
        return


    bolhas_finais = sorted(bolhas_finais, key=lambda b: b[0])
    
    gabarito_mapa = {}
    total_colunas = 6
    questoes_por_coluna = 15
    alternativas = ['A', 'B', 'C', 'D', 'E']
    largura_total = float(template_redim.shape[1])
    altura_total = float(template_redim.shape[0])
    
    for col in range(total_colunas):
        inicio_col = col * (questoes_por_coluna * 5)
        fim_col = inicio_col + (questoes_por_coluna * 5)
        bolhas_da_coluna = bolhas_finais[inicio_col:fim_col]
        
        bolhas_da_coluna = sorted(bolhas_da_coluna, key=lambda b: b[1])
        
        for q in range(questoes_por_coluna):
            numero_questao = (col * questoes_por_coluna) + q + 1
            
            inicio_q = q * 5
            fim_q = inicio_q + 5
            linha_questao = bolhas_da_coluna[inicio_q:fim_q]
            
            linha_questao = sorted(linha_questao, key=lambda b: b[0])
            
            gabarito_mapa[str(numero_questao)] = {}
            for idx, alt in enumerate(alternativas):
                if idx < len(linha_questao):
                    bx, by, bw, bh = linha_questao[idx]
    
                    gabarito_mapa[str(numero_questao)][alt] = {
                        "x": bx / largura_total,
                        "y": by / altura_total,
                        "w": bw / largura_total,
                        "h": bh / altura_total
                    }
                
    with open("gabarito_coordenadas.json", "w") as f:
        json.dump(gabarito_mapa, f, indent=4)
        
    print("\n[SUCESSO] O arquivo 'gabarito_coordenadas.json' foi gerado com sucesso!")

if __name__ == '__main__':
    gerar_mapa_coordenadas('images/templateFinal.png')