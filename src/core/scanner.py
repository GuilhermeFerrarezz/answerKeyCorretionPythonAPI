import cv2
import numpy as np

def alinhar_por_template(imagem_torta, imagem_template, max_features=5000):
    torta_cinza = cv2.cvtColor(imagem_torta, cv2.COLOR_BGR2GRAY)
    template_cinza = cv2.cvtColor(imagem_template, cv2.COLOR_BGR2GRAY)

    
    sift = cv2.SIFT_create(max_features)
    keypoints_torta, descriptores_torta = sift.detectAndCompute(torta_cinza, None)
    keypoints_template, descriptores_template = sift.detectAndCompute(template_cinza, None)

   
    matcher = cv2.BFMatcher()
    
    
    matches_brutos = matcher.knnMatch(descriptores_torta, descriptores_template, k=2)

    matches = []
    for m, n in matches_brutos:
        
        if m.distance < 0.75 * n.distance:
            matches.append(m)

    pontos_torta = np.zeros((len(matches), 2), dtype=np.float32)
    pontos_template = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        pontos_torta[i, :] = keypoints_torta[match.queryIdx].pt
        pontos_template[i, :] = keypoints_template[match.trainIdx].pt

    
    matriz_homografia, mascara = cv2.findHomography(pontos_torta, pontos_template, cv2.RANSAC, 5.0)
    
    if matriz_homografia is None:
        raise ValueError("A imagem enviada não parece ser um gabarito válido (Padrão não reconhecido).")
    
    inliers = np.sum(mascara)
    #print(f"[DEBUG] Pontos únicos de alinhamento perfeito encontrados: {inliers}")
    
    if inliers < 40: 
        raise ValueError(f"Imagem rejeitada. Não foram encontrados pontos de referência únicos suficientes ({inliers}). Envie uma foto clara.")
    
    altura, largura = imagem_template.shape[:2]
    imagem_alinhada = cv2.warpPerspective(imagem_torta, matriz_homografia, (largura, altura))

    return imagem_alinhada

if __name__ == '__main__':
    img_torta = cv2.imread('images/respostaMarco2Dia.jpeg')
    img_template = cv2.imread('images/templateFinal.png')

    if img_torta is not None and img_template is not None:
        img_corrigida = alinhar_por_template(img_torta, img_template)
        cv2.imwrite("3_alinhada_por_template.jpg", img_corrigida)
        print("Alinhamento de Alta Precisão concluído!")
    else:
        print("Erro ao carregar as imagens de teste.")