nome = input("Qual o nome do seu cliente?")
valor_da_compra = float(input("Qual foi o valor da compra?"))
vip = valor_da_compra>300
especial = valor_da_compra>=100<=299.99
comum = valor_da_compra<=99.99
desconto_vip = valor_da_compra*0.15
desconto_especial = valor_da_compra*0.10

print("--- CLASSIFICAÇÃO DO CLIENTE ---")
print("Cliente:", nome)
if vip:
    print("Categoria: VIP")
elif especial:
    print("Categoria: Especial")
else:
    print("Categoria: Comum")
print("Valor Original:", valor_da_compra)
if vip:
    print("Desconto:", desconto_vip)
elif especial:
    print("Desconto", desconto_especial)
else:
    print("Desconto: Sem Desconto")

if vip:
    print("Valor final:", valor_da_compra-valor_da_compra*0.15)
elif especial:
    print("Valor final:", valor_da_compra-valor_da_compra*0.10)
else:
    print("Valor final:", valor_da_compra)