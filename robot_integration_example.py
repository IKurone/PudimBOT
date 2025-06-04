"""
Exemplo de como usar o Pudim Chatbot como serviço para robô

Este arquivo demonstra como integrar o chatbot com o código de movimentação do robô.
O chatbot fica carregado na memória e é ativado quando uma pessoa é detectada.
"""

import time
from chatbot import (
    initialize_bot, 
    start_conversation, 
    stop_conversation, 
    ask_question, 
    speak_and_listen,
    is_bot_ready,
    get_bot_instance
)


def simulate_robot_movement():
    """Simula código de movimentação do robô"""
    print("🤖 Robô se movimentando...")
    time.sleep(2)


def simulate_person_detection():
    """Simula detecção de pessoa"""
    print("👤 Pessoa detectada!")
    return True


def handle_person_interaction(bot):
    """Gerencia interação com pessoa detectada"""
    print("🛑 Parando movimentação - pessoa detectada!")
    
    if not is_bot_ready():
        print("❌ Bot não está pronto para conversa")
        return
        
    print("💬 Ativando chatbot...")
    conversation_started = start_conversation(duration_minutes=3)
    
    if conversation_started:
        # Espera a conversa terminar
        while bot.conversation_active:
            time.sleep(1)
        print("✅ Conversa finalizada!")
    else:
        print("❌ Não foi possível iniciar conversa")


def main_robot_loop():
    """Loop principal do robô com integração do chatbot"""
    
    # Inicializa o chatbot na memória
    print("🔄 Inicializando chatbot na memória...")
    bot = initialize_bot()
    
    print("✅ Chatbot carregado! Status:", bot.get_status())
    print("🤖 Iniciando loop principal do robô...")
    print("=" * 50)
    
    # Loop principal do robô
    while True:
        try:
            # Simula movimentação do robô
            simulate_robot_movement()
            
            # Verifica se detectou uma pessoa
            if simulate_person_detection():
                handle_person_interaction(bot)
                print("🔄 Retomando movimentação...")
            
            # Simula intervalo entre movimentos
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n🛑 Parando robô...")
            if bot.conversation_active:
                stop_conversation()
            break

def test_quick_interactions():
    """Testa interações rápidas sem conversa completa"""
    print("\n=== Teste de Interações Rápidas ===")
    
    initialize_bot()
    
    # Pergunta rápida sem iniciar conversa completa
    response = ask_question("Que horas são?")
    print(f"Resposta: {response}")
    
    # Fala algo e escuta resposta única
    response = speak_and_listen("Olá! Como você está?", timeout=5.0)
    print(f"Usuário respondeu: {response}")

def test_conversation_mode():
    """Testa modo de conversa completa"""
    print("\n=== Teste de Conversa Completa ===")
    
    # Inicia conversa por 2 minutos
    if start_conversation(duration_minutes=2):
        print("Conversa iniciada! Fale com o robô...")
        
        # Simula espera enquanto conversa acontece
        bot = get_bot_instance()
        while bot.conversation_active:
            time.sleep(1)
        
        print("Conversa finalizada!")

def run_test_mode():
    """Executa o modo de teste selecionado pelo usuário"""
    print("🤖 Exemplo de Integração Pudim + Robô")
    print("Escolha o modo de teste:")
    print("1 - Simulação completa do robô")
    print("2 - Teste de interações rápidas") 
    print("3 - Teste de conversa completa")
    
    choice = input("Digite sua escolha (1-3): ").strip()
    
    if choice == "1":
        main_robot_loop()
    elif choice == "2":
        test_quick_interactions()
    elif choice == "3":
        test_conversation_mode()
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    run_test_mode()
