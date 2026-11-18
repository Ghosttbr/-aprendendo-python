nome = input("Qual o seu nome?")
valor = float(input("Qual o valor da sua compra?"))

print("--- RESUMO DA SUA COMPRA ---")
print("Cliente:", nome)
print("Valor dos itens:", valor)
if valor>100:
    print("Desconto: R$", valor*0.10 )
    print("Valor total: ", valor-valor*0.10)
else:
    print("Valor total: ", valor)
