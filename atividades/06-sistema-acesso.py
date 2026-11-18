nome = input("Olá, seja bem vindo ao sistema de acesso do grupo SOMA, primeiramente me diga o seu nome completo")
idade = int(input("Agora me diga a sua idade..."))
autorizacao = input("Você possui autorização especial?")
sim = "Otimo, prosseguimos então"
if autorizacao=="sim" and idade>=18:
    print(sim)
    print("--- SISTEMA DE ACESSO ---")
    print("Usuário: ", nome)
    print("Acesso permitido!")
else:
    print("Você deve possuir a autorização especial, para nossa segurança, nosso setor de rh e ti recebeu o seu endereço ip e mac, por conta de tentativa de acesso a área restrita")
