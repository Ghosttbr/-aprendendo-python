# Aprendendo Python

Este repositório reúne atividades práticas desenvolvidas durante minhas aulas de Python. A ideia é guardar cada exercício em um só lugar e acompanhar minha evolução ao longo do aprendizado.

## Minha proposta de aprendizado

Quero aprender por meio de desafios práticos, aplicando aos poucos os conceitos vistos nas aulas. Cada atividade registra uma etapa desse processo e serve como referência para acompanhar o que já pratiquei.

## Atividades desenvolvidas

| Nº | Atividade | Conceitos praticados |
| --- | --- | --- |
| 01 | Cadastro Usuario | entrada de dados (`input()`), saída de dados (`print()`), variáveis |
| 02 | Calculadora de compras | Operações matemáticas e conversão de tipos |
| 03 | Sistema de descontos | `if` e `else` |
| 04 | Classificação de clientes | Condições e operadores de comparação |
| 05 | Aprovação de candidatos | `if`, `elif`, `else` e condições aninhadas |
| 06 | Sistema de acesso | Operadores lógicos e condições |
| 07 | Descontos de loja | `or`, `if`, `elif` e `else` |

O registro de conclusão e os conceitos de cada atividade também estão em [`docs/progresso.md`](docs/progresso.md).

## Tecnologias utilizadas

- Python
- Visual Studio Code (VS Code)
- Git

## Minha evolução

Até aqui, pratiquei entrada e saída de dados, variáveis, conversão de tipos, operações matemáticas, condições, comparações e operadores lógicos. Vou atualizar esta seção conforme avançar nas aulas e desenvolver novas atividades.

## Como atualizar o repositório

O monitor local acompanha a pasta `atividades`. Salve cada nova atividade com o padrão `atividade 09.py`, `atividade 10.py`, `atividade 11.py` e assim por diante. Quando o arquivo fica sem alterações por cinco minutos, passa na verificação de sintaxe e não contém padrões detectáveis de e-mail, telefone, CPF, IP/MAC ou credenciais, o README e o progresso são atualizados e a alteração é enviada ao GitHub. Como o nome do arquivo não informa o tema, a tabela registra o título como `Atividade 09`, por exemplo. O monitor inicia junto com sua sessão do Windows. Salve na pasta somente atividades prontas: o monitor não consegue deduzir se você ainda está desenvolvendo a ideia. Para desativar o início automático, execute `python monitorar_atividades.py --uninstall` no terminal do projeto.

Se o monitor estiver pausado ou você preferir atualizar manualmente:

1. Salve o código na pasta `atividades`, seguindo a numeração e o padrão de nomes existente.
2. Acrescente a atividade à lista deste README e à tabela de [`docs/progresso.md`](docs/progresso.md), com os conceitos praticados e o status.
3. No terminal, dentro da pasta do projeto, registre e publique as alterações:

```bash
git add .
git commit -m "Descrição da atualização"
git push
```
