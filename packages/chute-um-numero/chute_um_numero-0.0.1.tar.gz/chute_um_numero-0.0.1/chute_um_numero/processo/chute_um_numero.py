import random

valor = random.randint(1,10)

contador = 0
acertou = False

while contador < 10 and acertou == False:
    chute = int(input('Chute um número de 1 a 10: '))
    contador = contador + 1

    if chute > valor:  
        print('O chute foi maior que o valor aleatório')
    elif chute < valor:
        print('O chute foi menor que o valor aleatório')
    else:
        acertou = True
        print('Parabéns! Você acertou em', contador, 'tentativas')