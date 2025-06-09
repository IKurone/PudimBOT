"""Como executar o bot de forma simples, e integrando ao robô Pudim."""	

"""Para executar o bot, você precisa ter o arquivo `chatbot.py` no mesmo diretório em conjunto ao .env. Também é necessário ter a pasta "module" e "data" no mesmo diretório. E executar as seguintes linhas de código."""

# from chatbot import start_conversation
# start_conversation(duration_minutes=1)

"""(RECOMENDADO)É possivel inicializa-lo na memória usando o "initialize_bot()" e o start_conversation(), exemplo abaixo:"""

# from chatbot import initialize_bot, start_conversation
# print("Iniciando o bot...")
# initialize_bot()
# print("Iniciando conversa...")
# start_conversation(duration_minutes=1)


"""Também é possivel executar o bot executando o main.py no terminal "python.exe main.py --[args]", usando argumentos como `--interactive`, `--service` ou `--conversation`."""
