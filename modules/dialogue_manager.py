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
            "Estou excelente! Sempre animado para nossas conversas."
        ]

        self.answer_for_how_are_you_responses = [
            "Fico feliz em ouvir isso! Estou aqui para ajudar.",
            "Que bom que você está bem! Estou sempre aqui para ajudar.",
            "Ótimo saber! Estou aqui para o que você precisar.",
            "Fico contente que esteja bem! Estou sempre à disposição.",
            "É sempre bom ouvir que você está bem! Estou aqui para ajudar."
        ]
        
        self.help_responses = [
            "Claro! Me diga como posso ajudar.",
            "Estou aqui para isso! O que você precisa?",
            "Com certeza! O que posso fazer por você?",
            "Sempre! Estou aqui para ajudar. O que você precisa?",
            "É claro! Estou à disposição para ajudar com o que você precisar."
        ]

        self.function_responses = [
            "Eu posso ajudar com informações sobre horários de aulas, clima atual, data e hora.",
            "Minhas funções incluem fornecer horários de aulas, informações meteorológicas, data e hora atual.",
            "Estou aqui para ajudar com consultas sobre horários acadêmicos, clima, data/hora.",
            "Posso te ajudar com informações sobre horários de aulas, clima atual, data e hora.",
            "Estou preparado para falar sobre horários, tempo, clima e responder suas perguntas."
        ]
        
        self.unknown_responses = [
            "Hmm, não entendi muito bem. Pode reformular a pergunta?",
            "Desculpe, não compreendi. Pode explicar de outra forma?",
            "Não consegui entender. Pode tentar perguntar de modo diferente?",
            "Ops, essa eu não peguei. Pode repetir de outro jeito?",
            "Não entendi direito. Pode ser mais específico?"
        ]

        self.joke_responses = [
            "Por que o livro de matemática se suicidou? Porque tinha muitos problemas!",
            "O que o zero disse para o oito? Que cinto maneiro!",
            "Por que o computador foi ao médico? Porque estava com um vírus!",
            "O que o tomate falou para o outro? Não se preocupe, eu vou ketchup!",
            "Por que o pássaro não usa Facebook? Porque já tem Twitter!"
            "Por que o computador foi preso? Porque executou muitos comandos suspeitos."
        ]

        self.positive_feedback_responses = [
            "Obrigado! Fico feliz que tenha gostado!",
            "Agradeço o elogio! Estou aqui para ajudar.",
            "Fico contente que você tenha gostado! Estou sempre aqui para ajudar.",
            "Muito obrigado! Seu feedback é muito importante para mim.",
            "Agradeço! É sempre bom saber que estou ajudando."
        ]
        self.negative_feedback_responses = [
            "Sinto muito que não tenha gostado. Estou sempre tentando melhorar.",
            "Desculpe por não ter atendido suas expectativas. Vou tentar melhorar.",
            "Lamento que minha resposta não tenha sido útil. Agradeço o feedback.",
            "Peço desculpas se não consegui ajudar. Estou sempre aprendendo.",
            "Sinto muito por não ter sido útil. Vou trabalhar para melhorar."
        ]

        self.gratitude_responses = [
            "De nada! Estou aqui para ajudar sempre que precisar.",
            "Você é muito gentil! Fico feliz em poder ajudar.",
            "Não há de quê! Estou sempre à disposição.",
            "Agradeço! É sempre bom saber que estou ajudando.",
            "Fico feliz em ouvir isso! Estou aqui para ajudar sempre que precisar."
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
            'tchau', 'até logo', 'até mais', 'adeus', 'bye', 'até a próxima', 'falou'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{farewell}\b", text_lower) for farewell in farewells)
    
    def is_how_are_you(self, text: str) -> bool:
        """Verifica se está perguntando como está"""
        questions = [
            'como está', 'como vai', 'como você está', 'tudo bem',
            'tudo ok', 'beleza', 'como anda', 'como tem passado', 'como você tem estado',
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{question}\b", text_lower) for question in questions)
    
    def is_how_are_you_answer(self, text: str) -> bool:
        """Verifica se está respondendo como está"""
        answers = [
            'estou bem', 'tudo bem', 'tudo ok', 'estou ótimo', 'estou legal',
            'estou feliz', 'estou tranquilo', 'estou de boa', 'tudo certo',
            'tudo tranquilo', 'tudo beleza', 'tudo jóia', 'tudo em paz', 'tudo'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{answer}\b", text_lower) for answer in answers)

    
    def is_help_request(self, text: str) -> bool:
        """Verifica se está pedindo ajuda"""
        help_keywords = [
            'pode me ajudar', 'poderia me ajudar', 'me ajuda', 'me ajude'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in help_keywords)
    
    def is_function_question(self, text: str) -> bool:
        """Verifica se está perguntando sobre as funções do bot"""
        function_keywords = [
            'o que você faz', 'para que serve', 'o que você pode fazer',
            'o que você sabe fazer', 'quais são suas funções',
            'quais são suas habilidades', 'o que você pode me ajudar',
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in function_keywords)
    
    def is_joke_request(self, text: str) -> bool:
        """Verifica se está pedindo uma piada"""
        joke_keywords = [
            'me conta uma piada', 'conte uma piada', 'faz uma piada',
            'conta uma piada', 'me faz rir', 'me faça rir', 'eu quero rir',
        ]

        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in joke_keywords)
    
    def is_positive_feedback(self, text: str) -> bool:
        """Verifica se é um feedback positivo"""
        positive_keywords = [
            'bom trabalho', 'ótimo trabalho', 'muito bom', 'excelente',
            'parabéns', 'legal', 'show de bola', 'incrível', 'fantástico',
            'maravilhoso', 'adorei', 'gostei muito'
        ]
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in positive_keywords)
    
    def is_negative_feedback(self, text: str) -> bool:
        """Verifica se é um feedback negativo"""
        negative_keywords = [
            'ruim', 'péssimo', 'horrível', 'não gostei', 'não é bom',
            'decepcionante', 'fraco', 'lixo', 'horrendo', 'terrível',
            'não funciona', 'não ajuda'
        ]
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in negative_keywords)

    def is_gratitude(self, text: str) -> bool:
        """Verifica se está agradecendo"""
        gratitude_keywords = [
            'obrigado', 'obrigada', 'valeu', 'agradeço', 'muito obrigado',
            'muito obrigada', 'grato', 'grata', 'agradecido', 'agradecida'
        ]
        
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{keyword}\b", text_lower) for keyword in gratitude_keywords)



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
            'how_are_you_answer': self.answer_for_how_are_you_responses,
            'help': self.help_responses,
            'unknown': self.unknown_responses,
            'activation': self.activation_responses,
            'function': self.function_responses,
            'joke': self.joke_responses,
            'positive_feedback': self.positive_feedback_responses,
            'negative_feedback': self.negative_feedback_responses,
            'gratitude': self.gratitude_responses
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
                self.is_how_are_you_answer(text) or
                self.is_help_request(text) or
                self.is_function_question(text) or
                self.is_joke_request(text) or
                self.is_positive_feedback(text) or
                self.is_negative_feedback(text) or
                self.is_gratitude(text)
                )

    
    def handle_social_interaction(self, text: str, is_farewell: bool = False) -> str:
        """Processa interações sociais e retorna resposta apropriada"""
        if self.is_greeting(text) and not is_farewell:
            return self.get_random_response('greeting')
        elif self.is_farewell(text) or is_farewell:
            return self.get_random_response('farewell')
        elif self.is_how_are_you(text) and not is_farewell:
            return self.get_random_response('how_are_you')
        elif self.is_how_are_you_answer(text) and not is_farewell:
            return self.get_random_response('how_are_you_answer')
        elif self.is_help_request(text) and not is_farewell:
            return self.get_random_response('help')
        elif self.is_function_question(text) and not is_farewell:
            return self.get_random_response('function')
        elif self.is_joke_request(text) and not is_farewell:
            return self.get_random_response('joke')
        elif self.is_positive_feedback(text) and not is_farewell:
            return self.get_random_response('positive_feedback')
        elif self.is_negative_feedback(text) and not is_farewell:
            return self.get_random_response('negative_feedback')
        elif self.is_gratitude(text) and not is_farewell:
            return self.get_random_response('gratitude')
        elif not is_farewell:
            return self.get_random_response('unknown')
