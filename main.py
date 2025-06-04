"""
🤖 Pudim - Chatbot por Voz para Raspberry Pi 4

Um assistente virtual em português brasileiro que responde por voz,
consulta PDFs locais, informa clima e horários, e realiza interações sociais.

"""

import sys
import argparse
from chatbot import PudimBot, initialize_bot


def show_help():
    """Mostra informações de ajuda"""
    help_text = """
🤖 Pudim - Chatbot por Voz para Raspberry Pi 4

MODOS DE EXECUÇÃO:
  --interactive    Modo interativo via texto (para desenvolvimento/teste)
  --service        Modo serviço (carrega bot na memória e aguarda)
  --conversation   Inicia conversa por voz imediatamente
  --help           Mostra esta ajuda

EXEMPLOS:
  python main.py --interactive     # Teste via texto
  python main.py --service         # Carrega como serviço
  python main.py --conversation    # Conversa por voz
  python main.py                   # Modo padrão (conversa por voz)

INTEGRAÇÃO COM ROBÔ:
  O modo --service é ideal para integração com código de movimento do robô.
  Use as funções do módulo chatbot.py para controlar o bot externamente.
"""
    print(help_text)


def run_interactive_mode(bot):
    """Executa modo interativo"""
    print("📝 Modo Interativo (Texto)")
    bot.start_interactive_mode()


def run_service_mode(bot):
    """Executa modo serviço"""
    print("🔧 Modo Serviço")
    print("Bot carregado na memória e pronto para uso externo.")
    print("Use as funções do módulo chatbot.py para controlar.")
    print("Pressione Ctrl+C para encerrar.")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Encerrando serviço...")


def run_conversation_mode(bot):
    """Executa modo conversa por voz"""
    print("🎤 Modo Conversa (Voz)")
    if not bot.stt.is_available():
        print("❌ STT não disponível. Usando modo interativo.")
        bot.start_interactive_mode()
    else:
        success = bot.activate_conversation(duration_minutes=10)
        if not success:
            print("❌ Não foi possível iniciar a conversa.")


def run_default_mode(bot):
    """Executa modo padrão (conversa por voz)"""
    print("🎤 Modo Padrão (Conversa por Voz)")
    if not bot.stt.is_available():
        print("❌ STT não disponível. Usando modo interativo.")
        print("💡 Use --interactive para modo texto ou configure o STT.")
        bot.start_interactive_mode()
    else:
        success = bot.activate_conversation(duration_minutes=10)
        if not success:
            print("❌ Não foi possível iniciar a conversa.")


def main():
    """Função principal com suporte a múltiplos modos"""
    parser = argparse.ArgumentParser(
        description='Pudim - Chatbot por Voz para Raspberry Pi 4',
        add_help=False
    )
    parser.add_argument('--interactive', action='store_true', help='Modo interativo via texto')
    parser.add_argument('--service', action='store_true', help='Modo serviço (carrega e aguarda)')
    parser.add_argument('--conversation', action='store_true', help='Inicia conversa por voz')
    parser.add_argument('--help', action='store_true', help='Mostra ajuda')
    
    args = parser.parse_args()
    
    # Mostra ajuda se solicitado
    if args.help:
        show_help()
        return
    
    print("🤖 Inicializando Pudim...")
    
    try:
        # Inicializa o bot (carrega modelos na memória)
        bot = initialize_bot()
        
        # Executa modo selecionado
        if args.interactive:
            run_interactive_mode(bot)
        elif args.service:
            run_service_mode(bot)
        elif args.conversation:
            run_conversation_mode(bot)
        else:
            run_default_mode(bot)
                    
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("💡 Tente executar com --interactive para modo texto")
        print("💡 Ou use --help para ver todas as opções")
        sys.exit(1)


if __name__ == "__main__":
    main()