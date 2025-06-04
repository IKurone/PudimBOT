"""
Módulo de Text-to-Speech (TTS) usando RealtimeTTS
"""
import threading
import time
from typing import Optional

try:
    from RealtimeTTS import TextToAudioStream, KokoroEngine, PiperEngine, PiperVoice, SystemEngine
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ RealtimeTTS não disponível. Funcionalidade de voz desabilitada.")


class TTSManager:
    """Gerenciador de Text-to-Speech"""
    
    def __init__(self, engine_type: str = "kokoro"):
        self.engine_type = engine_type
        self.stream = None
        self.is_speaking = False
        
        if TTS_AVAILABLE:
            self._initialize_tts()
    
    def _initialize_tts(self):
        """Inicializa o TTS"""
        try:
            if self.engine_type.lower() == "kokoro":
                engine = KokoroEngine()
                engine.set_voice("pf_dora")
            elif self.engine_type.lower() == "piper":
                voice = PiperVoice()
                engine = PiperEngine(voice=voice)
            else:
                # Fallback para engine padrão
                engine = SystemEngine()
                engine.set_voice("Maria")
            
            self.stream = TextToAudioStream(engine, language="pt")
            print(f"✅ TTS inicializado com engine {self.engine_type}")
        except Exception as e:
            print(f"❌ Erro ao inicializar TTS: {e}")
            self.stream = None
    
    def speak(self, text: str, wait: bool = True):
        """Fala o texto fornecido"""
        if not TTS_AVAILABLE or not self.stream:
            # Fallback para print em desenvolvimento
            print(f"🔊 {text}")
            return
        if self.is_speaking:
            self.stop_speaking()
        else:
            try:
                self.is_speaking = True
                if wait:
                    # Modo síncrono
                    self.stream.feed(text)
                    self.stream.play()

                else:
                    # Modo assíncrono
                    self._speak_async(text)
                    # threading.Thread(target=self._speak_async, args=(text,), daemon=True).start()
            except Exception as e:
                print(f"❌ Erro ao falar: {e}")
            finally:
                if wait:
                    self.is_speaking = False
    
    def _speak_async(self, text: str):
        """Fala de forma assíncrona"""
        try:
            self.stream.feed(text)
            self.stream.play_async()
        except Exception as e:
            print(f"❌ Erro ao falar (async): {e}")
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        """Para a fala atual"""
        if self.stream and self.is_speaking:
            try:
                self.stream.stop()
                self.is_speaking = False
                print("🔇 Parando fala...")
            except Exception as e:
                print(f"❌ Erro ao parar fala: {e}")
    
    def is_busy(self) -> bool:
        """Verifica se está falando"""
        return self.is_speaking



# if __name__ == "__main__":
#     # Teste rápido do TTS
#     engine = SystemEngine()
#     voices = engine.get_voices()
#     print("Vozes disponíveis:", voices)