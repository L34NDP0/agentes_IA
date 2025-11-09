import os
from dotenv import load_dotenv # Importa a função para ler .env
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader

# Carrega as variáveis do .env para o ambiente
load_dotenv()

# Agora você pode acessar suas variáveis por os.environ
api_key = os.environ['GROQ_API_KEY']        # Obtém o valor da chave da API do arquivo .env

# Para videos youtube,não pode ser grande limitação token gratis
chat = ChatGroq(model='groq/compound-mini')

#Template para prompt Padrão
template = ChatPromptTemplate.from_messages([
    ('system', 'Você é um assistente amigável e tem acesso as seguintes informações para dar suas respostas: {documentos_informados}'),
    ('user', '{input}')
])


##Acessando YouTube
# url = 'https://www.youtube.com/watch?v=4H1JXPwhPtw'
# loader = YoutubeLoader.from_youtube_url(
#     url,
#     language=['pt']
# )
# lista_documentos = loader.load()


## Load para acessar sites
#loader = WebBaseLoader("https://asimov.academy/")
#lista_documentos = loader.load()
#print(lista_documentos)


##ACESSANDO PDFs
# caminho = '/Projetos Python/Agentes_IA/agentes_IA/arquivos/Residencial_San_Levi.pdf'
# loader = PyPDFLoader(caminho)
# lista_documentos = loader.load()


## Processo de listas de conteudo tanto p video, pdf ou site
# documento = ''
# for doc in lista_documentos:
#     documento = documento + doc.page_content
#print(documento)

#print(lista_documentos[0].page_content)


##Modelo de perguntas padrão sobre os conteudos extraídos
# chain_pdf = template | chat
# resposta = chain_pdf.invoke({'documentos_informados': documento, 'input': 'Localização do empreendimento?'})
# print(resposta.content)


# chain_youtube = template | chat
# resposta = chain_youtube.invoke({'documentos_informados': documento, 'input': 'Quais livros são indicados?'})
# print(resposta.content)


# chain = template | chat
# resposta = chain.invoke({'documentos_informados': documento, 'input': 'Quais as trilhas disponiveis na asimov?'})
# print(resposta.content)


## 
def resposta_bot(mensagens, documento):
    mensagem_system = '''Você é um assistente amigável chamado Siri.
    Você utiliza as seguintes informações para formular as suas respostas: {informacoes}'''
    mensagens_modelo = [('system', mensagem_system)]
    #mensagens_modelo = [('system', 'Você é um assistente amigável chamado SIRI')]
    mensagens_modelo += mensagens
    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat
    return chain.invoke({'informacoes': documento}).content




def carrega_site():
    url_site = input('Digite a url do site: ')
    loader = WebBaseLoader(url_site)
    lista_documentos = loader.load()
    documento = ''
    for doc in lista_documentos:
        documento = documento + doc.page_content
    return documento

def carrega_pdf():
    caminho = '/Projetos Python/Agentes_IA/agentes_IA/arquivos/Residencial_San_Levi.pdf'
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento = ''  # Adicionei esta linha que estava faltando
    for doc in lista_documentos:
        documento = documento + doc.page_content
    return documento

def carrega_youtube():
    url_youtube = input('Digite a url do video: ')
    loader = YoutubeLoader.from_youtube_url(url_youtube,language=['pt'])
    lista_documentos = loader.load()
    documento = ''
    for doc in lista_documentos:
        documento = documento + doc.page_content
    return documento

print(f'Bem Vindo')

texto_selecao = '''Digite 1 se você quiser conversar com um site
Digite 2 se você quiser conversar com um PDF
Digite 3 se você quiser conversar com um video Youtube

'''

while True:
    selecao = input(texto_selecao)
    if selecao == '1':
        #print('site')
        documento = carrega_site()
        break
    if selecao == '2':
        #print('PDF')
        documento = carrega_pdf()
        break
    if selecao == '3':
        #print('YouTube')
        documento = carrega_youtube()
        break
    print('Digite um valor entre 1 e 3')

#LOOP DE CONVERSA COM O USUARIO
mensagens = []
while True:
    pergunta = input('Usuário: ')
    if pergunta.lower() == 'x':
        break
    mensagens.append(('user', pergunta))
    resposta = resposta_bot(mensagens, documento)
    mensagens.append(('assistant', resposta))
    print(f'Bot: {resposta}')
    
print('\nMuito Obrigado por utilizar a SIRI! O histórico completo da conversa foi:')
print(mensagens)


#langchain padroniza acesso a IAs, meio de acesso a API das IAs