# PudimBOT

**PudimBOT** é um chatbot leve desenvolvido para rodar em um **Raspberry Pi 4 (4 GB de RAM)**, criado especialmente para o **robô Pudim**, do laboratório **LABMOV** da **UERJ/Zona Oeste**.

Este projeto visa oferecer uma interface de conversa natural com foco em comandos básicos, integração acadêmica e fácil implantação em ambientes embarcados.

---

## Funcionalidades

- **Conversas sociais básicas**  
  Responde a cumprimentos, perguntas sobre bem-estar e conta piadas.

- **Informações contextuais**  
  Entende e responde perguntas sobre **hora**, **data** e **clima**.

- **Assistência acadêmica**  
  Interpreta comandos relacionados a **disciplinas** e **cursos** da faculdade, como:  
  > "Que sala é usada em Física 2 de Ciência da Computação?"

---

## Como usar

O código foi desenvolvido para ser simples de entender, implementar e ativar. Basta importar e iniciar o assistente com o tempo de conversa desejado (em minutos):

```python
from chatbot import start_conversation

start_conversation(duration_minutes=1)
