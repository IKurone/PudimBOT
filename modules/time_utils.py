"""
Módulo para utilitários de data e hora
"""
from datetime import datetime, timedelta
import locale


class TimeManager:
    """Gerenciador de informações de data e hora"""
    
    def __init__(self):
        # Tenta configurar locale para português brasileiro
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            except locale.Error:
                print("⚠️ Não foi possível definir locale para português")
    
    def get_current_time(self) -> str:
        """Retorna a hora atual formatada"""
        now = datetime.now()
        return now.strftime("%H:%M")
    
    def get_current_date(self) -> str:
        """Retorna a data atual formatada"""
        now = datetime.now()
        try:
            # Tenta usar locale português
            return now.strftime("%A, %d de %B de %Y")
        except (locale.Error, ValueError):
            # Fallback para formato manual
            days = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
            months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            
            day_name = days[now.weekday()]
            month_name = months[now.month - 1]
            
            return f"{day_name}, {now.day} de {month_name} de {now.year}"
    
    def get_current_datetime(self) -> str:
        """Retorna data e hora atuais formatadas"""
        return f"{self.get_current_date()}, {self.get_current_time()}"
    
    def get_greeting(self) -> str:
        """Retorna cumprimento baseado no horário"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Bom dia"
        elif 12 <= hour < 18:
            return "Boa tarde"
        else:
            return "Boa noite"
    
    def is_time_question(self, text: str) -> bool:
        """Verifica se a pergunta é sobre data/hora"""
        time_keywords = [
            'hora', 'horas', 'time', 'data', 'dia', 'hoje',
            'agora', 'atual', 'quando', 'que dia', 'que hora'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in time_keywords)
    
    def format_time_response(self, text: str) -> str:
        """Formata resposta sobre data/hora baseada na pergunta"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hora', 'horas', 'que hora']):
            return f"Agora são {self.get_current_time()}."
        
        elif any(word in text_lower for word in ['data', 'dia', 'hoje', 'que dia']):
            return f"Hoje é {self.get_current_date()}."
        
        else:
            return f"Agora são {self.get_current_time()} de {self.get_current_date()}."
