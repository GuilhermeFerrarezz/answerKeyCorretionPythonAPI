import cv2
import numpy as np

def alinhar_por_template(imagem_torta, imagem_template, max_features=5000, match_percent=0.15):
    # 1. Converter ambas as imagens para tons de cinza
    torta_cinza = cv2.cvtColor(imagem_torta, cv2.COLOR_BGR2GRAY)
    template_cinza = cv2.cvtColor(imagem_template, cv2.COLOR_BGR2GRAY)

    # 2. Inicializar o detector ORB
    # Ele vai procurar até 'max_features' (pontos de interesse) nas duas imagens
    orb = cv2.ORB_create(max_features)
    keypoints_torta, descriptores_torta = orb.detectAndCompute(torta_cinza, None)
    keypoints_template, descriptores_template = orb.detectAndCompute(template_cinza, None)

    # 3. Combinar os pontos (Feature Matching)
    # Compara os pontos encontrados na foto com os pontos do template
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptores_torta, descriptores_template, None)

    # 4. Ordenar as combinações pela qualidade (distância)
    matches = list(matches)
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Manter apenas os melhores X% dos pontos combinados para evitar falsos positivos
    num_bons_matches = int(len(matches) * match_percent)
    matches = matches[:num_bons_matches]

    # 5. Extrair as coordenadas (x,y) dos melhores pontos
    pontos_torta = np.zeros((len(matches), 2), dtype=np.float32)
    pontos_template = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        pontos_torta[i, :] = keypoints_torta[match.queryIdx].pt
        pontos_template[i, :] = keypoints_template[match.trainIdx].pt

    # 6. Calcular a Homografia (Matriz de Transformação Matemática)
    # O RANSAC ignora pontos que por acaso combinaram errado
    matriz_homografia, mascara = cv2.findHomography(pontos_torta, pontos_template, cv2.RANSAC)

    # 7. Aplicar a transformação na imagem torta original
    # O resultado terá exatamente a mesma largura e altura do template
    altura, largura = imagem_template.shape[:2]
    imagem_alinhada = cv2.warpPerspective(imagem_torta, matriz_homografia, (largura, altura))

    return imagem_alinhada

# ==========================================
# TESTANDO A FUNÇÃO
# ==========================================
if __name__ == '__main__':
    # Carregar as imagens (Substitua pelos caminhos reais do seu servidor/máquina)
    img_torta = cv2.imread('respostaMarco2Dia.jpeg')
    img_template = cv2.imread('templateFinal.png')

    # Executar o alinhamento
    img_corrigida = alinhar_por_template(img_torta, img_template)

    # Salvar para verificação
    cv2.imwrite("3_alinhada_por_template.jpg", img_corrigida)
    print("Alinhamento automático concluído!")