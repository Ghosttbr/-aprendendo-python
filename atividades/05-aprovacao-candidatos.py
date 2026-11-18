nome = input("Seja muto bem vindo ao sistema de verificação do ENEM, para começarmos, primeiramente me diga o seu nome...")
idade = int(input("Olá, seja muito bem vindo(a), agora para continuarmos precisamos saber a sua idade, pode me dizer?"))
aprovado = "Parabéns! Você foi aprovado no curso de sua escolha, tenha bons estudos!"
analise = "Você está em analise devido a sua nota, verifique o resultado no site oficial do enem semana que vem."
reprovado = "Você foi reprovado! Tente novamente ano que vem."

if idade<18:
    if 18-idade>1:
        print("Ops, parece que você não tem a idade minima de 18 anos, volte daqui:", 18-idade, "anos!")
    else:
        print("Ops, parece que você não tem a idade minima de 18 anos, volte daqui:", 18-idade, "ano!")
    exit()
else:
    print("Você possui a idade minima de 18 anos!")

print("Otimo! estou recebendo o seu curso escolhido, nota de corte, inscrição no sisu...")
nota = float(input("Agora vamos vamos verificar se você foi aprovada na sua lista! me diga qual foi a nota que você tirou! (MAX: 100pts)"))

if nota>100:
    print("Parábens! Você conseguiu tirar uma nota maior do que é possivel! Comece novamente e escreva sua nota real (MAX: 100 pts)")
    exit()
else:
    print("")


if nota>=80 and idade>=18:
    print("--- RESULTADO DA AVALIAÇÃO ---")
    print("Candidato: ", nome)
    print("Idade: ", idade)
    print("Nota: ", nota)
    print("Resultado: APROVADO")
elif nota<=79.99 and nota>=60 and idade>=18:
    print("--- RESULTADO DA AVALIAÇÃO ---")
    print("Candidato: ", nome)
    print("Idade: ", idade)
    print("Nota: ", nota)
    print("Resultado: EM ANALISE")
else:
    print("--- RESULTADO DA AVALIAÇÃO ---")
    print("Candidato: ", nome)
    print("Idade: ", idade)
    print("Nota: ", nota)
    print("Resultado: REPROVADO")
