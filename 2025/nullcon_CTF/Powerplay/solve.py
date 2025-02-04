import numpy as np

def encontra_indice():
    for i in range(2147483647): # Ate maior valor inteiro possivel
        i2 = np.int32(i) ** 2   # Elevando ao quadrado
        if i2 >= np.int32(-24) and i2 < 0: # Verificando se esta no intervalo -24 a -1
            return i, i2

indice, indiceQuadrado = encontra_indice()
print("Número encontrado " +  str(indice))
print(str(indice) + " ao quadrado = " + str(indiceQuadrado))