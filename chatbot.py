import os
import sys
import threading
import time
from typing import Optional, Callable
from dotenv import load_dotenv

# Importa todos os módulos
from modules.stt import STTManager
from modules.tts import TTSManager
from modules.pdf_reader import PDFReader
from modules.weather import WeatherManager
from modules.time_utils import TimeManager
from modules.dialogue_manager import DialogueManager


class PudimBot:
    """
    Classe principal do chatbot Pudim - Singleton para economia de recursos
    Mantém modelos carregados em memória para ativação rápida
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa padrão Singleton"""
        if cls._instance is None:
            cls._instance = super(PudimBot, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evita reinicialização se já foi inicializado
        if PudimBot._initialized:
            return
            
        # Carrega variáveis do arquivo .env
        load_dotenv()
        
        # Configurações do bot
        self.bot_name = os.getenv('BOT_NAME', 'Pudim')
        self.user_name = os.getenv('USER_NAME', 'Usuário')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Estado do bot
        self.is_running = False
        self.is_paused = False
        self.conversation_active = False
        
        # Inicializa componentes (carrega modelos na memória)
        self._initialize_components()
        
        PudimBot._initialized = True
        print(f"🤖 {self.bot_name} carregado na memória e pronto para ativação!")
        print("=" * 50)
    
    def _initialize_components(self):
        """Inicializa todos os componentes do bot - carrega modelos na memória"""
        try:
            print("🔄 Carregando modelos na memória...")
            
            # STT (Speech-to-Text)
            whisper_model = os.getenv('WHISPER_MODEL', 'tiny')
            self.stt = STTManager(model_name=whisper_model)
            if self.debug:
                print(f"🎤 Engine STT: {self.stt.get_engine_info()}")
            
            # TTS (Text-to-Speech)
            tts_engine = os.getenv('TTS_ENGINE', 'system')
            self.tts = TTSManager(engine_type=tts_engine)
            
            # PDF Reader
            self.pdf_reader = PDFReader()
            
            # Weather Manager
            api_key = os.getenv('OPENWEATHER_API_KEY', '')
            city = os.getenv('CITY_NAME', 'Rio de Janeiro')
            country = os.getenv('COUNTRY_CODE', 'BR')
            self.weather = WeatherManager(api_key, city, country)
            
            # Time Manager
            self.time_manager = TimeManager()
            
            # Dialogue Manager
            self.dialogue = DialogueManager(self.bot_name, self.user_name)
            
            print("✅ Todos os componentes carregados na memória!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar componentes: {e}")
            sys.exit(1)
    
    def activate_conversation(self, duration_minutes: int = 5) -> bool:
        """
        Ativa o chatbot para uma conversa
        Args:
            duration_minutes: Duração máxima da conversa em minutos
        Returns:
            bool: True se a conversa foi iniciada com sucesso
        """
        if self.conversation_active:
            print("⚠️ Conversa já está ativa")
            return False
        
        print(f"🤖 Ativando {self.bot_name} para conversa...")
        self.conversation_active = True
        self.is_running = True
        self.is_paused = False
        
        # Cumprimento inicial
        greeting = self.time_manager.get_greeting()
        initial_message = f"{greeting}! Eu sou o {self.bot_name}. Como posso ajudar você?"
        self.tts.speak(initial_message)
        
        # Inicia thread para conversa com timeout
        conversation_thread = threading.Thread(
            target=self._conversation_loop, 
            args=(duration_minutes,), 
            daemon=False
        )
        conversation_thread.start()

        
        return True
    
    def deactivate_conversation(self):
        """Desativa o chatbot e retorna controle"""
        print(f"🔇 Desativando {self.bot_name}...")
        self.conversation_active = False
        self.is_running = False
        self.stt.stop_listening()
        
        # Mensagem de despedida
        farewell = self.dialogue.get_random_response('farewell')
        self.tts.speak(farewell)
        
        print(f"✅ {self.bot_name} desativado - controle retornado")
    
    def _conversation_loop(self, duration_minutes: int):
        """Loop principal da conversa com timeout"""
        start_time = time.time()
        timeout = duration_minutes * 60  # Converte para segundos
        
        # Configura callback do STT
        self.stt.set_callback(self.process_user_input)
        
        if self.stt.is_available():
            self.stt.start_listening()
            print(f"🎤 {self.bot_name} está ouvindo... (timeout: {duration_minutes}min)")
        else:
            print("⚠️ STT não disponível. Usando timeout apenas.")
        
        try:
            while self.conversation_active and self.is_running:
                # Verifica timeout
                if time.time() - start_time > timeout:
                    print(f"⏰ Timeout de {duration_minutes} minutos atingido")
                    break
                
                # Se pausado, escuta apenas por ativação
                if self.is_paused:
                    user_input = self.stt.listen_once(timeout=5.0)
                    if user_input and self.dialogue.is_bot_activation(user_input):
                        self.is_paused = False
                        response = "Voltei! O que você precisa?"
                        self.tts.speak(response)
                        print(f"🎤 {self.bot_name} retomou a escuta...")
                
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Erro na conversa: {e}")
        finally:
            self.deactivate_conversation()
    
    def quick_response(self, text: str) -> str:
        """
        Gera uma resposta rápida sem iniciar conversa completa
        Args:
            text: Texto de entrada
        Returns:
            str: Resposta gerada
        """
        response = self._generate_response(text)
        if response:
            return response
        else:
            return self.dialogue.get_random_response('unknown')
    
    def speak_and_listen_once(self, message: str = None, timeout: float = 10.0) -> Optional[str]:
        """
        Fala uma mensagem e escuta uma resposta única
        Args:
            message: Mensagem para falar (opcional)
            timeout: Timeout para escuta
        Returns:
            str: Texto ouvido ou None
        """
        if message:
            self.tts.speak(message)
        
        if self.stt.is_available():
            return self.stt.listen_once(timeout)
        else:
            return input("Digite sua resposta: ")
    
    def process_user_input(self, text: str):
        """Processa entrada do usuário e gera resposta"""
        if not text.strip():
            return
        
        original_text = text
        if self.debug:
            print(f"🔍 DEBUG - Entrada: '{original_text}'")
        
        # Verifica se o bot está sendo ativado pelo nome
        if self.dialogue.is_bot_activation(text):
            response = self.dialogue.get_random_response('activation')
            self.tts.speak(response)
            
            # Remove o nome do bot para processar o resto do comando
            text = self.dialogue.clean_bot_name_from_text(text)
            if not text.strip():
                return
        
        # Processa diferentes tipos de entrada
        response = self._generate_response(text)
        
        if response:
            if self.debug:
                print(f"🔍 DEBUG - Resposta: '{response}'")
            self.tts.speak(response)
        else:
            # Resposta padrão para quando não entende
            unknown_response = self.dialogue.get_random_response('unknown')
            self.tts.speak(unknown_response)
    
    def _generate_response(self, text: str) -> Optional[str]:
        """Gera resposta baseada no texto de entrada"""
        # 1. Verifica interações sociais
        if self.dialogue.is_social_interaction(text) and not self.dialogue.is_farewell(text):
            return self.dialogue.handle_social_interaction(text)
        
        # 2. Verifica perguntas sobre data/hora
        if self.time_manager.is_time_question(text):
            return self.time_manager.format_time_response(text)
        
        # 3. Verifica perguntas sobre clima
        if self.weather.is_weather_question(text):
            return self.weather.format_weather_response()
        
        # 4. Comandos de controle
        if self._is_control_command(text) or self.dialogue.is_farewell(text):
            return self._handle_control_command(text)
        
        # 5. Busca nos PDFs
        pdf_response = self.pdf_reader.answer_question(text)
        if pdf_response:
            return pdf_response
        
        # 6. Se não encontrou resposta específica, tenta busca geral nos PDFs
        general_results = self.pdf_reader.search_in_content(text)
        if general_results and "Não encontrei" not in general_results:
            return general_results
        
        return None
    
    def _is_control_command(self, text: str) -> bool:
        """Verifica se é um comando de controle"""
        control_words = ['parar', 'pausar', 'sair', 'desligar', 'pare', 'stop']
        text_lower = text.lower()
        return any(word in text_lower for word in control_words)
    
    def _handle_control_command(self, text: str) -> str:
        """Lida com comandos de controle"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['parar', 'pausar', 'pare']):
            self.is_paused = True
            return "Ok, vou pausar. Me chame pelo nome quando quiser que eu volte."
        
        elif any(word in text_lower for word in ['sair', 'desligar', 'stop', 'tchau', 'até logo']) or self.dialogue.is_farewell(text):
            self.tts.speak(self.dialogue.handle_social_interaction(text, is_farewell=True))
            self.conversation_active = False
            self.is_running = False
            return ""
        
        return "Comando não reconhecido."
    
    def is_ready(self) -> bool:
        """Verifica se o bot está pronto para uso"""
        return PudimBot._initialized and not self.conversation_active
    
    def get_status(self) -> dict:
        """Retorna status atual do bot"""
        return {
            'initialized': PudimBot._initialized,
            'conversation_active': self.conversation_active,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'stt_available': self.stt.is_available() if hasattr(self, 'stt') else False,
            'stt_engine': self.stt.get_engine_info() if hasattr(self, 'stt') else 'N/A'
        }
    
    # Métodos antigos mantidos para compatibilidade (agora deprecados)
    def start_listening(self):
        """DEPRECADO: Use activate_conversation() ao invés"""
        print("⚠️ start_listening() está deprecado. Use activate_conversation()")
        return self.activate_conversation()
    
    def stop(self):
        """DEPRECADO: Use deactivate_conversation() ao invés"""
        print("⚠️ stop() está deprecado. Use deactivate_conversation()")
        self.deactivate_conversation()
    
    def start_interactive_mode(self):
        """Modo interativo via texto (para desenvolvimento/teste)"""
        print(f"\n🤖 {self.bot_name} - Modo Interativo")
        print("Digite 'sair' para encerrar")
        print("=" * 50)
        
        # Cumprimento inicial
        greeting = self.time_manager.get_greeting()
        initial_message = f"{greeting}! Eu sou o {self.bot_name}. Como posso ajudar você hoje?"
        print(f"🤖 {initial_message}")
        
        self.conversation_active = True
        self.is_running = True
        
        try:
            while self.conversation_active and self.is_running:
                try:
                    user_input = input(f"\n{self.user_name}: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['sair', 'exit', 'quit', 'tchau']:
                        break
                    
                    response = self._generate_response(user_input)
                    if response:
                        print(f"🤖 {response}")
                    else:
                        unknown_response = self.dialogue.get_random_response('unknown')
                        print(f"🤖 {unknown_response}")
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                    
        finally:
            farewell = self.dialogue.get_random_response('farewell')
            print(f"\n🤖 {farewell}")
            self.conversation_active = False
            self.is_running = False


# Funções utilitárias para interface com código externo
def get_bot_instance() -> PudimBot:
    """Retorna instância singleton do bot"""
    return PudimBot()

def initialize_bot() -> PudimBot:
    """Inicializa o bot e retorna a instância"""
    bot = PudimBot()
    return bot

def start_conversation(duration_minutes: int = 5) -> bool:
    """Interface simples para iniciar conversa"""
    bot = get_bot_instance()
    return bot.activate_conversation(duration_minutes)

def stop_conversation():
    """Interface simples para parar conversa"""
    bot = get_bot_instance()
    bot.deactivate_conversation()

def ask_question(question: str) -> str:
    """Interface simples para fazer uma pergunta"""
    bot = get_bot_instance()
    return bot.quick_response(question)

def speak_and_listen(message: str = None, timeout: float = 10.0) -> Optional[str]:
    """Interface simples para falar e escutar"""
    bot = get_bot_instance()
    return bot.speak_and_listen_once(message, timeout)

def is_bot_ready() -> bool:
    """Verifica se o bot está pronto para uso"""
    try:
        bot = get_bot_instance()
        return bot.is_ready()
    except Exception:
        return False
