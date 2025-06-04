"""
Módulo gerenciador de diálogos e interações sociais
"""
import random
import re
from typing import List, Optional


class DialogueManager:
    """Gerenciador de diálogos e respostas sociais"""
    
    def __init__(self, bot_name: str = "Pudim", user_name: str = "Usuário"):
        self.bot_name = bot_name
        self.user_name = user_name
        
        # Respostas variadas para diferentes situações
        self.greetings = [
            f"Olá! Eu sou o {self.bot_name}. Como posso ajudar você hoje?",
            f"Oi! {self.bot_name} aqui. No que posso ser útil?",
            f"Olá, {self.user_name}! Como está? Sou o {self.bot_name}, seu assistente virtual.",
            f"Ei! O {self.bot_name} está aqui para ajudar. O que você precisa?",
            f"Oi! Prazer em falar com você. Eu sou o {self.bot_name}."
        ]
        
        self.farewells = [
            "Até logo! Foi um prazer conversar com você.",
            "Tchau! Estarei aqui quando precisar.",
            "Até mais! Tenha um ótimo dia!",
            "Até a próxima! Sempre que quiser conversar, é só chamar.",
            "Tchau! Cuide-se e volte sempre."
        ]
        
        self.how_are_you_responses = [
            "Estou bem, obrigado por perguntar! E você, como está?",
            "Ótimo! Sempre pronto para ajudar. Como você está se sentindo?",
            "Estou muito bem! Adoro conversar com você. E aí, como vai?",
            "Perfeito! Cada conversa me deixa mais feliz. E você?",
            "Estou excelente! Sempre animado para nossos papos."
        ]
        
        self.help_responses = [
            "Claro! Posso ajudar com informações sobre horários, clima, data e hora, além de responder perguntas sobre os PDFs que tenho acesso.",
            "Estou aqui para isso! Posso consultar horários de aulas, falar sobre o clima, dar informações de data/hora e muito mais.",
            "Com certeza! Sou especialista em horários acadêmicos, informações meteorológicas e posso responder suas dúvidas dos documentos.",
            "Sempre! Posso te ajudar com consultas sobre horários, clima atual, data e hora, além de informações dos arquivos PDF.",
            "É claro! Estou preparado para falar sobre horários, tempo, clima e responder suas perguntas baseadas nos documentos."
        ]
        
        self.unknown_responses = [
            "Hmm, não entendi muito bem. Pode reformular a pergunta?",
            "Desculpe, não compreendi. Pode explicar de outra forma?",
            "Não consegui entender. Pode tentar perguntar de modo diferente?",
            "Ops, essa eu não peguei. Pode repetir de outro jeito?",
            "Não entendi direito. Pode ser mais específico?"
        ]
        
        self.activation_responses = [
            f"Oi! {self.bot_name} aqui! O que você precisa?",
            "Presente! O que posso fazer por você?",
            "Aqui estou! Como posso ajudar?",
            f"Opa! {self.bot_name} à disposição!",
            "Oi! Pode falar, estou ouvindo!"
        ]
    
    def is_greeting(self, text: str) -> bool:
        """Verifica se é um cumprimento"""
        greetings = [
            'oi', 'olá', 'ola', 'ei', 'hey', 'bom dia', 'boa tarde', 
            'boa noite', 'salve', 'e aí', 'eai', 'hello'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{greeting}\b", text_lower) for greeting in greetings)
    
    def is_farewell(self, text: str) -> bool:
        """Verifica se é uma despedida"""
        farewells = [
            'tchau', 'até logo', 'até mais', 'adeus', 'bye', 'valeu',
            'obrigado', 'obrigada', 'até a próxima', 'falou'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{farewell}\b", text_lower) for farewell in farewells)
    
    def is_how_are_you(self, text: str) -> bool:
        """Verifica se está perguntando como está"""
        questions = [
            'como está', 'como vai', 'como você está', 'tudo bem',
            'tudo ok', 'beleza', 'como anda', 'como tem passado'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{question}\b", text_lower) for question in questions)
    
    def is_help_request(self, text: str) -> bool:
        """Verifica se está pedindo ajuda"""
        help_keywords = [
            'ajuda', 'help', 'socorro', 'não sei', 'como', 'pode me ajudar',
            'o que você faz', 'para que serve', 'o que sabe fazer'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in help_keywords)
    
    def is_bot_activation(self, text: str) -> bool:
        """Verifica se o bot está sendo chamado pelo nome"""
        text_lower = text.lower().strip()
        bot_name_lower = self.bot_name.lower()
        
        # Verifica se o nome do bot está no início ou sozinho na frase
        return (text_lower.startswith(bot_name_lower) or 
                text_lower == bot_name_lower or
                f" {bot_name_lower}" in text_lower or
                f"{bot_name_lower}," in text_lower)
    
    def get_random_response(self, response_type: str) -> str:
        """Retorna uma resposta aleatória do tipo especificado"""
        responses = {
            'greeting': self.greetings,
            'farewell': self.farewells,
            'how_are_you': self.how_are_you_responses,
            'help': self.help_responses,
            'unknown': self.unknown_responses,
            'activation': self.activation_responses
        }
        
        if response_type in responses:
            return random.choice(responses[response_type])
        
        return "Desculpe, não sei como responder a isso."
    
    def clean_bot_name_from_text(self, text: str) -> str:
        """Remove o nome do bot do texto para processar o comando"""
        text_lower = text.lower()
        bot_name_lower = self.bot_name.lower()
        
        # Remove o nome do bot do início
        if text_lower.startswith(bot_name_lower):
            text = text[len(self.bot_name):].strip()
            # Remove vírgulas ou pontos que podem ter ficado
            text = re.sub(r'^[,.\s]+', '', text)
        
        return text.strip()
    
    def is_social_interaction(self, text: str) -> bool:
        """Verifica se é uma interação social (cumprimento, despedida, etc.)"""
        return (self.is_greeting(text) or 
                self.is_farewell(text) or 
                self.is_how_are_you(text) or 
                self.is_help_request(text))
    
    def handle_social_interaction(self, text: str, is_farewell: bool = False) -> str:
        """Processa interações sociais e retorna resposta apropriada"""
        if self.is_greeting(text) and not is_farewell:
            return self.get_random_response('greeting')
        elif self.is_farewell(text) or is_farewell:
            return self.get_random_response('farewell')
        elif self.is_how_are_you(text) and not is_farewell:
            return self.get_random_response('how_are_you')
        elif self.is_help_request(text) and not is_farewell:
            return self.get_random_response('help')
        elif not is_farewell:
            return self.get_random_response('unknown')
