import gradio as gr
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, YoutubeLoader
import tempfile

# Carrega as variáveis do .env
load_dotenv()

# Configuração do modelo
chat = ChatGroq(model='groq/compound-mini')

# Funções para carregar documentos
def carrega_site(url):
    if not url:
        return "Por favor, forneça uma URL válida."
    
    try:
        loader = WebBaseLoader(url)
        lista_documentos = loader.load()
        documento = ''
        for doc in lista_documentos:
            documento = documento + doc.page_content
        return documento
    except Exception as e:
        return f"Erro ao carregar o site: {str(e)}"

def carrega_pdf():
    try:
        # Caminho fixo para o arquivo PDF
        caminho = 'D:/Projetos Python/Agentes_IA/agentes_IA/arquivos/Residencial_San_Levi.pdf'
        
        # Verificar se o arquivo existe
        if not os.path.exists(caminho):
            return f"Arquivo não encontrado: {caminho}"
        
        loader = PyPDFLoader(caminho)
        lista_documentos = loader.load()
        documento = ''
        for doc in lista_documentos:
            documento = documento + doc.page_content
        return documento
    except Exception as e:
        return f"Erro ao processar o PDF: {str(e)}"

def carrega_youtube(url):
    if not url:
        return "Por favor, forneça uma URL do YouTube válida."
    
    try:
        loader = YoutubeLoader.from_youtube_url(url, language=['pt'])
        lista_documentos = loader.load()
        documento = ''
        for doc in lista_documentos:
            documento = documento + doc.page_content
        return documento
    except Exception as e:
        return f"Erro ao carregar o vídeo: {str(e)}"

# Função para processar a conversa
def processar_conversa(fonte, url_site, url_youtube, historico, pergunta):
    if not pergunta:
        return historico, ""
    
    # Adicionar a pergunta ao histórico
    historico = historico + [[pergunta, None]]
    
    # Verificar se já temos um documento carregado ou precisamos carregar
    if not hasattr(processar_conversa, "documento") or processar_conversa.documento is None:
        if fonte == "Site" and url_site:
            documento = carrega_site(url_site)
            processar_conversa.documento = documento
        elif fonte == "PDF":
            documento = carrega_pdf()
            processar_conversa.documento = documento
        elif fonte == "YouTube" and url_youtube:
            documento = carrega_youtube(url_youtube)
            processar_conversa.documento = documento
        else:
            return historico[:-1] + [[pergunta, "Por favor, forneça a fonte de informação corretamente."]], ""
    
    # Preparar mensagens para o LangChain
    mensagens_lc = []
    for msg in historico[:-1]:  # Excluir a última mensagem que acabamos de adicionar
        if msg[1] is not None:  # Se tem resposta
            mensagens_lc.append(("user", msg[0]))
            mensagens_lc.append(("assistant", msg[1]))
        else:
            mensagens_lc.append(("user", msg[0]))
    
    # Adicionar a pergunta atual
    mensagens_lc.append(("user", pergunta))
    
    try:
        # Obter resposta
        mensagem_system = '''Você é um assistente amigável chamado Siri.
        Você utiliza as seguintes informações para formular as suas respostas: {informacoes}'''
        mensagens_modelo = [('system', mensagem_system)]
        mensagens_modelo += mensagens_lc
        template = ChatPromptTemplate.from_messages(mensagens_modelo)
        chain = template | chat
        resposta = chain.invoke({'informacoes': processar_conversa.documento}).content
        
        # Atualizar o histórico com a resposta
        historico[-1][1] = resposta
        
        return historico, ""
    except Exception as e:
        historico[-1][1] = f"Erro: {str(e)}"
        return historico, ""

# Função para limpar a conversa
def limpar_conversa():
    if hasattr(processar_conversa, "documento"):
        processar_conversa.documento = None
    return [], "", ""

# Interface Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Assistente IA - SIRI")
    gr.Markdown("Converse com diferentes fontes de informação")
    
    with gr.Row():
        with gr.Column(scale=1):
            fonte = gr.Radio(["Site", "PDF", "YouTube"], label="Escolha a fonte de informação", value="Site")
            
            with gr.Group():
                url_site = gr.Textbox(label="URL do Site", placeholder="Digite a URL do site", visible=True)
                # Removemos o componente de upload de arquivo
                url_youtube = gr.Textbox(label="URL do YouTube", placeholder="Digite a URL do vídeo do YouTube", visible=False)
            
            carregar_btn = gr.Button("Carregar Fonte")
            status = gr.Textbox(label="Status", interactive=False)
            
            def atualizar_visibilidade(escolha):
                return {
                    url_site: gr.update(visible=escolha == "Site"),
                    url_youtube: gr.update(visible=escolha == "YouTube")
                }
            
            fonte.change(atualizar_visibilidade, fonte, [url_site, url_youtube])
            
            def carregar_fonte(fonte, url_site, url_youtube):
                try:
                    if fonte == "Site":
                        if not url_site:
                            return "Por favor, forneça uma URL válida."
                        documento = carrega_site(url_site)
                        processar_conversa.documento = documento
                        return "Site carregado com sucesso! Pode começar a fazer perguntas."
                    
                    elif fonte == "PDF":
                        documento = carrega_pdf()
                        processar_conversa.documento = documento
                        return "PDF carregado com sucesso! Pode começar a fazer perguntas."
                    
                    elif fonte == "YouTube":
                        if not url_youtube:
                            return "Por favor, forneça uma URL do YouTube válida."
                        documento = carrega_youtube(url_youtube)
                        processar_conversa.documento = documento
                        return "Vídeo carregado com sucesso! Pode começar a fazer perguntas."
                    
                    return "Tipo de fonte não reconhecido."
                except Exception as e:
                    return f"Erro ao carregar: {str(e)}"
            
            carregar_btn.click(carregar_fonte, [fonte, url_site, url_youtube], status)
        
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Conversa com SIRI", height=500)
            pergunta = gr.Textbox(label="Digite sua pergunta", placeholder="O que você gostaria de saber?")
            
            with gr.Row():
                enviar_btn = gr.Button("Enviar")
                limpar_btn = gr.Button("Nova Consulta")
            
            enviar_btn.click(processar_conversa, 
                           [fonte, url_site, url_youtube, chatbot, pergunta], 
                           [chatbot, pergunta])
            
            pergunta.submit(processar_conversa, 
                          [fonte, url_site, url_youtube, chatbot, pergunta], 
                          [chatbot, pergunta])
            
            limpar_btn.click(limpar_conversa, [], [chatbot, pergunta, url_site])

# Inicializar o documento como None
processar_conversa.documento = None

demo.launch()