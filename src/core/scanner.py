import cv2
import numpy as np

def alinhar_por_template(imagem_torta, imagem_template, max_features=5000, match_percent=0.15):
    
    torta_cinza = cv2.cvtColor(imagem_torta, cv2.COLOR_BGR2GRAY)
    template_cinza = cv2.cvtColor(imagem_template, cv2.COLOR_BGR2GRAY)


    orb = cv2.ORB_create(max_features)
    keypoints_torta, descriptores_torta = orb.detectAndCompute(torta_cinza, None)
    keypoints_template, descriptores_template = orb.detectAndCompute(template_cinza, None)

    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptores_torta, descriptores_template, None)

    matches = list(matches)
    matches.sort(key=lambda x: x.distance, reverse=False)

    
    num_bons_matches = int(len(matches) * match_percent)
    matches = matches[:num_bons_matches]

    pontos_torta = np.zeros((len(matches), 2), dtype=np.float32)
    pontos_template = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        pontos_torta[i, :] = keypoints_torta[match.queryIdx].pt
        pontos_template[i, :] = keypoints_template[match.trainIdx].pt


    matriz_homografia, mascara = cv2.findHomography(pontos_torta, pontos_template, cv2.RANSAC)
    if matriz_homografia is None:
        raise ValueError("A imagem enviada não parece ser um gabarito válido (Padrão não reconhecido).")
    
    inliers = np.sum(mascara)
    print(f"[DEBUG] Pontos de alinhamento válidos encontrados: {inliers}")
    
    if inliers < 40: 
        raise ValueError(f"Imagem rejeitada. Não foram encontrados pontos de referência suficientes ({inliers}). Envie uma foto clara do gabarito.")
    
    
    altura, largura = imagem_template.shape[:2]
    imagem_alinhada = cv2.warpPerspective(imagem_torta, matriz_homografia, (largura, altura))

    cv2.imwrite("3_alinhada_por_template.jpg", imagem_alinhada)

    return imagem_alinhada


if __name__ == '__main__':

    img_torta = cv2.imread('respostaMarco2Dia.jpeg')
    img_template = cv2.imread('templateFinal.png')

  
    img_corrigida = alinhar_por_template(img_torta, img_template)

    cv2.imwrite("3_alinhada_por_template.jpg", img_corrigida)
    print("Alinhamento automático concluído!")