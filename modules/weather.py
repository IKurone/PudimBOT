"""
Módulo para consulta de informações meteorológicas usando OpenWeatherAPI
"""
import requests
import os
from typing import Optional, Dict
from datetime import datetime


class WeatherManager:
    """Gerenciador de informações meteorológicas"""
    
    def __init__(self, api_key: str, city: str = "São Paulo", country_code: str = "BR"):
        self.api_key = api_key
        self.city = city
        self.country_code = country_code
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_current_weather(self) -> Optional[Dict]:
        """Obtém informações meteorológicas atuais"""
        if not self.api_key or self.api_key == "your_openweather_api_key_here":
            return self._get_mock_weather()
        
        try:
            params = {
                'q': f"{self.city},{self.country_code}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'pt'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao consultar clima: {e}")
            return self._get_mock_weather()
        except Exception as e:
            print(f"❌ Erro inesperado ao consultar clima: {e}")
            return self._get_mock_weather()
    
    def _get_mock_weather(self) -> Dict:
        """Retorna dados meteorológicos fictícios para desenvolvimento"""
        return {
            'name': self.city,
            'main': {
                'temp': 25.0,
                'feels_like': 27.0,
                'humidity': 65,
                'pressure': 1013
            },
            'weather': [{
                'main': 'Clear',
                'description': 'céu limpo'
            }],
            'wind': {
                'speed': 3.5
            }
        }
    
    def format_weather_response(self) -> str:
        """Formata uma resposta sobre o clima atual"""
        weather_data = self.get_current_weather()
        
        if not weather_data:
            return "Desculpe, não consegui obter informações sobre o clima no momento."
        
        try:
            city = weather_data.get('name', self.city)
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            
            response = f"Em {city}, agora são {temp:.0f}°C, "
            response += f"com sensação térmica de {feels_like:.0f}°C. "
            response += f"O céu está {description}. "
            response += f"A umidade está em {humidity}%."
            
            # Adiciona informações extras se disponíveis
            if 'wind' in weather_data and 'speed' in weather_data['wind']:
                wind_speed = weather_data['wind']['speed'] * 3.6  # m/s para km/h
                response += f" Vento a {wind_speed:.0f} km/h."
            
            return response
            
        except KeyError as e:
            print(f"❌ Erro ao processar dados meteorológicos: {e}")
            return "Consegui consultar o clima, mas houve um problema ao processar as informações."
    
    def is_weather_question(self, text: str) -> bool:
        """Verifica se a pergunta é sobre clima"""
        weather_keywords = [
            'clima', 'tempo', 'temperatura', 'chuva', 'sol', 'nuvem',
            'quente', 'frio', 'graus', '°c', 'celsius', 'umidade',
            'vento', 'meteorologia', 'previsão'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in weather_keywords)
