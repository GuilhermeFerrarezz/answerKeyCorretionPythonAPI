import json


arquivo_entrada = 'gabarito_coordenadas.json' 
arquivo_saida = 'gabarito_coordenadas.json'


offset_x = -0.009
#0.009 Dia 1


with open(arquivo_entrada, 'r') as f:
    mapa = json.load(f)

for q in range(76, 91):
    q_str = str(q)
    if q_str in mapa:
        for alt in ['A', 'B', 'C', 'D', 'E']:
            if alt in mapa[q_str]:
                
                valor_antigo = mapa[q_str][alt]['x']
                mapa[q_str][alt]['x'] = valor_antigo + offset_x


with open(arquivo_saida, 'w') as f:
    json.dump(mapa, f, indent=4)

#print(f"✅ Sucesso! As coordenadas X das questões 76 a 90 foram deslocadas em +{offset_x}.")
#print(f"Novo arquivo salvo como: {arquivo_saida}")