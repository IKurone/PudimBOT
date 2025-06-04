"""
Módulo de Speech-to-Text (STT) com suporte a múltiplas engines:
- RealtimeSTT (usando FastWhisper)
- Speech Recognition (usando Google Speech API)
"""
import threading
import time
import os
from typing import Optional, Callable
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importações condicionais para as bibliotecas STT
try:
    from RealtimeSTT import AudioToTextRecorder
    REALTIME_STT_AVAILABLE = True
except ImportError:
    REALTIME_STT_AVAILABLE = False
    print("⚠️ RealtimeSTT não disponível.")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ SpeechRecognition não disponível.")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio não disponível.")


class STTManager:
    """Gerenciador de Speech-to-Text com múltiplas engines"""
    
    def __init__(self, model_name: str = "tiny", language: str = "pt"):
        self.model_name = model_name
        self.language = language
        self.is_listening = False
        self.callback = None
        
        # Determina qual engine usar baseado no .env
        self.stt_engine = os.getenv('STT_ENGINE', 'speech_recognition').lower()
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        
        # Debug: mostra o valor lido
        print(f"🔍 DEBUG STT_ENGINE lido: '{os.getenv('STT_ENGINE', 'speech_recognition')}'")
        
        # Inicializa a engine apropriada
        self.recorder = None
        self.recognizer = None
        self.microphone = None
        
        self._initialize_stt()
        
    def _initialize_stt(self):
        """Inicializa a engine STT apropriada"""
        if self.stt_engine == "realtime_stt" and REALTIME_STT_AVAILABLE:
            self._initialize_realtime_stt()
        elif self.stt_engine == "speech_recognition" and SPEECH_RECOGNITION_AVAILABLE:
            self._initialize_speech_recognition()
        else:
            print(f"❌ Engine STT '{self.stt_engine}' não disponível. Usando fallback para texto.")
            self.stt_engine = "text_input"
    
    def _initialize_realtime_stt(self):
        """Inicializa RealtimeSTT"""
        try:
            self.recorder = AudioToTextRecorder(
                model=self.model_name,
                language=self.language,
                post_speech_silence_duration=1.5,
                compute_type="float32",
                device="cpu",  # Use "cuda" para GPU se disponível
            )
            print(f"✅ RealtimeSTT inicializado com modelo {self.model_name}")
        except Exception as e:
            print(f"❌ Erro ao inicializar RealtimeSTT: {e}")
            self.recorder = None
            self.stt_engine = "text_input"
    
    def _initialize_speech_recognition(self):
        """Inicializa Speech Recognition"""
        try:
            if not PYAUDIO_AVAILABLE:
                print("❌ PyAudio não disponível. Necessário para Speech Recognition.")
                self.stt_engine = "text_input"
                return
                
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Ajusta para ruído ambiente
            print("🔧 Calibrando microfone para ruído ambiente...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("✅ Speech Recognition inicializado")
        except Exception as e:
            print(f"❌ Erro ao inicializar Speech Recognition: {e}")
            self.recognizer = None
            self.microphone = None
            self.stt_engine = "text_input"
    
    def set_callback(self, callback: Callable[[str], None]):
        """Define função callback para quando texto for transcrito"""
        self.callback = callback
    
    def start_listening(self):
        """Inicia escuta contínua"""
        if self.stt_engine == "text_input":
            print("⚠️ STT não disponível. Use modo interativo.")
            return
            
        if self.is_listening:
            return
            
        self.is_listening = True
        
        if self.stt_engine == "realtime_stt":
            threading.Thread(target=self._realtime_listen_loop, daemon=True).start()
        elif self.stt_engine == "speech_recognition":
            threading.Thread(target=self._speech_recognition_listen_loop, daemon=True).start()
            
        print(f"🎤 Iniciando escuta com {self.stt_engine}...")
    
    def stop_listening(self):
        """Para a escuta"""
        self.is_listening = False
        print("🔇 Parando escuta...")
    
    def _realtime_listen_loop(self):
        """Loop principal de escuta para RealtimeSTT"""
        while self.is_listening:
            try:
                if self.recorder:
                    text = self.recorder.text()
                    if text.strip() and self.callback:
                        self.callback(text.strip())
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Erro na escuta RealtimeSTT: {e}")
                time.sleep(1)
    
    # def animacao_escutando(self, duracao=3):
    #     print("🎤 Escutando", end="", flush=True)
    #     inicio = time.time()
    #     pontos = ["", ".", "..", "..."]
    #     i = 0

    #     while time.time() - inicio < duracao:
    #         print(f"\r🎤 Escutando{pontos[i % 4]}", end="", flush=True)
    #         i += 1
    #         time.sleep(0.5)

        print()  # quebra de linha ao final
    def _speech_recognition_listen_loop(self):
        """Loop principal de escuta para Speech Recognition"""
        while self.is_listening:
            try:
                if self.recognizer and self.microphone:
                    # Cria nova instância do microfone para cada escuta
                    mic = sr.Microphone()
                    with mic as source:
                        # Escuta áudio
                        audio = self.recognizer.listen(source)
                    
                    try:
                        # Reconhece fala usando Google
                        if self.google_api_key and self.google_api_key != "your_google_speech_api_key_here":
                            text = self.recognizer.recognize_google(
                                audio, 
                                key=self.google_api_key, 
                                language=self._get_language_code()
                            )
                        else:
                            # Usa o serviço gratuito do Google (limitado)
                            text = self.recognizer.recognize_google(
                                audio, 
                                language=self._get_language_code()
                            )
                        
                        if text.strip() and self.callback:
                            self.callback(text.strip())
                            
                    except sr.UnknownValueError:
                        # Google não conseguiu entender o áudio
                        pass
                    except sr.RequestError as e:
                        print(f"❌ Erro no serviço Google Speech Recognition: {e}")
                        time.sleep(2)
                        
            except sr.WaitTimeoutError:
                # Timeout normal, continua escutando
                pass
            except Exception as e:
                print(f"❌ Erro na escuta Speech Recognition: {e}")
                time.sleep(1)
    
    def _get_language_code(self):
        """Converte código de idioma para formato do Google"""
        language_map = {
            'pt': 'pt-BR',
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR'
        }
        return language_map.get(self.language, 'pt-BR')
    
    def listen_once(self, timeout: float = 10.0) -> Optional[str]:
        """Escuta uma única vez e retorna o texto"""
        if self.stt_engine == "text_input":
            # Fallback para input de texto
            return input("Digite sua mensagem: ")
        
        if self.stt_engine == "realtime_stt" and self.recorder:
            return self._listen_once_realtime(timeout)
        elif self.stt_engine == "speech_recognition" and self.recognizer and self.microphone:
            return self._listen_once_speech_recognition(timeout)
        else:
            return input("Digite sua mensagem: ")
    
    def _listen_once_realtime(self, timeout: float) -> Optional[str]:
        """Escuta uma única vez usando RealtimeSTT"""
        try:
            print("🎤 Escutando (RealtimeSTT)...")
            start_time = time.time()
            while time.time() - start_time < timeout:
                text = self.recorder.text()
                if text.strip():
                                return text.strip()
                time.sleep(0.1)
            return None
        except Exception as e:
            print(f"❌ Erro ao escutar com RealtimeSTT: {e}")
            return None
    
    def _listen_once_speech_recognition(self, timeout: float) -> Optional[str]:
        """Escuta uma única vez usando Speech Recognition"""
        try:
            print("🎤 Escutando (Speech Recognition)...")
            # Cria nova instância do microfone para evitar conflitos
            mic = sr.Microphone()
            with mic as source:
                # Escuta por um período limitado
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Reconhece a fala
            if self.google_api_key and self.google_api_key != "your_google_speech_api_key_here":
                text = self.recognizer.recognize_google(
                    audio, 
                    key=self.google_api_key, 
                    language=self._get_language_code()
                )
            else:
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self._get_language_code()
                )
            
            return text.strip() if text else None
            
        except sr.UnknownValueError:
            print("❌ Não consegui entender o áudio")
            return None
        except sr.RequestError as e:
            print(f"❌ Erro no serviço Google Speech Recognition: {e}")
            return None
        except sr.WaitTimeoutError:
            print("❌ Timeout - nenhum áudio detectado")
            return None
        except Exception as e:
            print(f"❌ Erro ao escutar com Speech Recognition: {e}")
            return None
    
    def get_engine_info(self) -> str:
        """Retorna informações sobre a engine atual"""
        if self.stt_engine == "realtime_stt":
            return f"RealtimeSTT (Modelo: {self.model_name})"
        elif self.stt_engine == "speech_recognition":
            api_status = "Com API Key" if (self.google_api_key and self.google_api_key != "your_google_speech_api_key_here") else "Serviço gratuito"
            return f"Speech Recognition Google ({api_status})"
        else:
            return "Entrada de texto (STT não disponível)"
    
    def is_available(self) -> bool:
        """Verifica se alguma engine STT está disponível"""
        return self.stt_engine != "text_input"


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Módulo STT ===")
    
    # Teste com diferentes engines
    for engine in ["realtime_stt", "speech_recognition"]:
        print(f"\n--- Testando {engine} ---")
        
        # Configura temporariamente a engine
        os.environ['STT_ENGINE'] = engine
        
        stt = STTManager()
        print(f"Engine: {stt.get_engine_info()}")
        print(f"Disponível: {stt.is_available()}")
        
        if stt.is_available():
            print("Teste de escuta única (5 segundos)...")
            result = stt.listen_once(timeout=5.0)
            print(f"Resultado: {result}")