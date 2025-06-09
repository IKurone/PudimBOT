"""Como executar o bot de forma simples, e integrando ao robô Pudim."""	

"""Para executar o bot, você precisa ter o arquivo `chatbot.py` no mesmo diretório em conjunto ao .env. Também é necessário ter a pasta "module" e "data" no mesmo diretório. E executar as seguintes linhas de código."""

from chatbot import start_conversation

start_conversation(duration_minutes=1)


"""Também é possivel executar o bot executando o main.py no terminal "python.exe main.py --[args]", usando argumentos como `--interactive`, `--service` ou `--conversation`."""
