# Projeto Contabilidade

Primeiramente vocês precisam instalar as dependências do projeto.
Instalar o poetry e depois sempre tenham certeza de usar o poetry shell quando mexer no projeto.
Dar um poetry install.
E por fim um instalar o pre-commit com pre-commit install.

Pode ser que seja necessário baixar manualmente o pacote "re" para rodar o programa main 

# TODO

Para primeira entrega, temos que realizar as seguintes tarefas:

- Melhorar o layout do streamlit para ter todas as funcionalidades e ficar bonito
    - Adicionar opção para escolher qual banco vai ser utilizado
    - Visualizar tanto o extrato quanto o boleto
    - Visualizar o lançamento
    - Baixar o lançamento
    - Criar opção para adicionar manualmente uma conta bancária

- Implementar o código para extrair os dados do extrato pdf (de vários bancos diferentes)
    - Usar o PyPDF2 para ler e coletar os dados de forma correta
    - Verificar formato dos dados
    - Salvar os dados em um csv

- Implementar o código para extrair os dados do boleto pdf 
    - Apenas alguns dados são importantes de coletar (coletar todos inicialmente)
    - Salvar em um csv

- Mesclar os dados do extrato com o boleto 
    - Onde tiver "CRÉD.LIQUIDAÇÃO COBRANÇA" no extrato deve ser procurado no boleto quais valores foram lançados nessa data e substituir

- Gerar os lançamentos  
    - Juntar os dados do extrato e do boleto e criar o arquivo txt com os lançamentos no formato certo

- [x] (Bruno) Eu entendi o que deve ser feito 
- [ ] (Lorde) Eu entendi o que deve ser feito 
- [ ] (Thales) Eu entendi o que deve ser feito 
