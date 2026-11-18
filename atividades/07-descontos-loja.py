nome = input("Qual o nome do cliente?")
valor = float(input("Qual o valor da compra?"))
idade = int(input("Qual a idade do cliente?"))
categoria = input("O cliente já possui alguma categoria? se sim informe qual é (VIP, ESPECIAL e COMUM)")


print("--- RESUMO DA SUA COMPRA ---")
print("Cliente:", nome)
print("Valor dos itens:", valor)
if idade>=60 or categoria=="VIP":
    print("Desconto: R$", valor*0.15 )
    print("Categoria: VIP")
    print("Valor total: ", valor-valor*0.15)
elif categoria=="ESPECIAL":
    print("Desconto: ", valor*0.10)
    print("Valor total: ", valor-valor*0.10)
else:
    print("Valor total: ", valor)
