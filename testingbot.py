import time
from chatbot import start_conversation, PudimBot, get_bot_instance

start_conversation(duration_minutes=1)
bot = get_bot_instance()

while bot.conversation_active:
    print("🤖 Robô está ativo e aguardando interação...")
    time.sleep(1)
