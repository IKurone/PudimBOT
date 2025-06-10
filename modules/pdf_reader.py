"""
Módulo para leitura e processamento de arquivos PDF
"""
import os
import re
from typing import List, Dict, Optional
import pdfplumber
import pandas as pd
from rapidfuzz import process, fuzz
import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)


class PDFReader:
    """Gerenciador de leitura de PDFs"""
    
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.pdf_contents = {}
        self.load_pdfs()
    
    def load_pdfs(self):
        """Carrega todos os PDFs da pasta data"""
        if not os.path.exists(self.data_folder):
            print(f"⚠️ Pasta {self.data_folder} não encontrada")
            return
        
        pdf_files = [f for f in os.listdir(self.data_folder) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"⚠️ Nenhum arquivo PDF encontrado em {self.data_folder}")
            return
        
        for pdf_file in pdf_files:
            try:
                file_path = os.path.join(self.data_folder, pdf_file)
                if "horario_" in pdf_file:
                    key = pdf_file.replace("horario_", "").split(".")[0]
                else:
                    key = pdf_file.split(".")[0]
                content = self._extract_tables_from_pdfs(file_path)
                self.pdf_contents[key] = content
                print(f"✅ PDF carregado: {pdf_file}")
            except Exception as e:
                print(f"❌ Erro ao carregar {pdf_file}: {e}")
    
    def _extract_tables_from_pdfs(self, pdf_path):
        """Extrai tabelas e executa limpeza de um PDF e retorna como DataFrame"""
        dataframe = None
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            table = first_page.extract_table()

            # Converte a tabela extraída em um DataFrame
            df = pd.DataFrame(table)

            # Encontra a primeira linha não vazia para definir os nomes das colunas
            for i, row in df.iterrows():
                if all(cell is not None and cell.strip() != '' for cell in row):
                    df.columns = row  # Coloca a primeira linha valida como cabeçalho
                    df = df.iloc[i + 1:]  # Remove as linhas acima do cabeçalho
                    break

            # Adiciona uma nova coluna 'SOURCE' com o nome do arquivo PDF
            # df['ORIGEM'] = key

            # Guarda o DataFrame em um dicionário com o nome do arquivo PDF como chave
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace(r"\bI\b", "1", regex=True)
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace(r"\bII\b", "2", regex=True)
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace(r"\bIII\b", "3", regex=True)
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace(r"\bIV\b", "4", regex=True)
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace(r"\bV\b", "5", regex=True)
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace(",", "")
            df['DISCIPLINA'] = df['DISCIPLINA'].str.replace("  ", " ", regex=True)
            df['DISCIPLINA'] = df['DISCIPLINA'].str.strip()
            dataframe = df

        return dataframe

    def clear_text(self, text: str) -> str:
        """Limpa o texto removendo espaços extras e caracteres especiais"""
        palavras_proibidas = [
            'horário','horario', 'aula', 'disciplina', 'matéria', 'turma', 'curso',
            'professor', 'sala', 'localização', 'local', 'qual',
            'é'
        ]
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)  # Remove caracteres especiais
        text = re.sub(r'\b([a-zA-Z]{1,2})\b', '', text) # Remove palavras de 1 ou 2 letras
        text = re.sub(r'\bum\b', '1', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdois\b', '2', text, flags=re.IGNORECASE)
        text = re.sub(r'\btres\b', '3', text, flags=re.IGNORECASE)
        text = re.sub(r'\bquatro\b', '4', text, flags=re.IGNORECASE)
        text = re.sub(r'\bcinco\b', '5', text, flags=re.IGNORECASE)
        text = ' '.join(word for word in text.split() if word.lower() not in palavras_proibidas)
        text = text.strip()
        return text
        

    def answer_question(self, question: str) -> Optional[str]:
        """Responde uma pergunta baseada nos PDFs"""
        question_lower = question.lower()
        # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
        if self.is_horario_question(question_lower):
            question_lower = self.clear_text(question_lower)
            # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
            return self.response_horario_question(question_lower)
        
        elif self.is_qual_professor_question(question_lower):
            question_lower = self.clear_text(question_lower)
            # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
            return self.response_professor_question(question_lower)
        
        elif self.is_sala_question(question_lower):
            question_lower = self.clear_text(question_lower)
            # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
            return self.response_sala_question(question_lower)
        
        else:
            return "❌ Pergunta não reconhecida. Tente reformular novamente."



    def is_horario_question(self, text: str) -> bool:
        """Verifica se está perguntando como está"""
        questions = [
            'horário','horario','qual o horário', 'qual horário', 'horário da aula', 'horário da disciplina',
            'horário da matéria', 'horário da turma', 'horário do curso', 'qual o horário da aula de', 'qual o horário da disciplina de','qual o horário da matéria de', 
            'qual o horário da turma de', 'qual é o horário',  'qual é o horário da aula', 'qual é o horário da disciplina', 'qual é o horário da matéria', 
            'qual é o horário da turma', 'qual é o horário do curso', 'horário de aula', 'horário de disciplina', 'horário de matéria', 
            'horário de turma', 'horário de curso', 'qual é o horário da disciplina de','qual é o horário da matéria de', 'qual é o horário da turma de'
        ]
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{question}\b", text_lower) for question in questions)
    
    def is_qual_professor_question(self, text: str) -> bool:
        """Verifica se está perguntando como está"""
        questions = [
            'professor de','professor da', 'professor do','qual o professor', 'qual o professor da aula', 'qual o professor da disciplina', 'qual é o professor', 'qual professor', 'que professor', 'qual o professor da matéria', 'professor da aula de', 'professor da disciplina de', 'professor da matéria de', 'professor da turma de'
        ]
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{question}\b", text_lower) for question in questions)

    def is_sala_question(self, text: str) -> bool:
        """Verifica se está perguntando como está"""
        questions = [
            'sala', 'qual a sala', 'qual a sala da aula', 'qual a sala da disciplina', 'qual é a sala', 'qual sala', 'que sala', 'sala da aula', 
            'sala da disciplina', 'sala da matéria', 'sala da turma', 'qual a sala da matéria', 'sala da aula de', 
            'sala da disciplina de', 'sala da matéria de', 'sala da turma de'
        ]
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{question}\b", text_lower) for question in questions)
            
    def is_locate_professor_question(self, text: str) -> bool:
        """Verifica se está perguntando como está"""
        questions = [
            'onde está o professor', 'onde está a professora', 'onde fica o professor',
            'onde fica a professora', 'localização do professor', 'localização da professora',
            'onde encontro o professor', 'onde encontro a professora'
        ]
        text_lower = text.lower().strip()
        return any(re.search(rf"\b{question}\b", text_lower) for question in questions)



    def gerar_combinacoes(self, texto, max_ngram=6):
        """Gera combinações de n-gramas a partir de um texto"""
        palavras = texto.lower().split()
        return [" ".join(palavras[i:i+n]) for i in range(len(palavras)) for n in range(1, max_ngram+1) if i + n <= len(palavras)]


    def _search_course(self, question: str):
        """Procura o curso na pergunta e retorna o código, nome completo e palavra original"""
        courses = {
            'cc': 'ciência da computação',
            'ema': 'engenharia de materiais',
            'emp': 'engenharia de produção',
            'emt': 'engenharia de mecatrônica',
            'tads': 'tecnologia em análise de desenvolvimento',
            'tcn': 'tecnologia de construção naval'
        }
        best_match = ""
        best_score = 0
        original_word = ""
        palavras = self.gerar_combinacoes(question)
        full_list = list(courses.values()) + list(courses.keys())
        for palavra in palavras:
            match, score, _ = process.extractOne(palavra, full_list, scorer=fuzz.ratio)
            # print(f"🔍 DEBUG - Verificando palavra: '{palavra}' -> Match: '{match}' com score: {score}")
            if score > best_score:
                best_score = score
                original_word = palavra
                best_match = match
        
        if best_score >= 40:
            # print(f"🔍 DEBUG - Melhor match encontrado: '{best_match}' com score: {best_score}")
            for code, full_name in courses.items():
                if best_match.lower() == code or best_match.lower() == full_name.lower():
                    return code, full_name, original_word
        else:
            return None, None, original_word




    def response_horario_question(self, question: str) -> str:
        """Responde perguntas sobre horários de disciplinas"""
        best_match = [None, 0]
        question_lower = question.lower()
        code, full_name, original_word = self._search_course(question)
        # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
        if code and full_name:
            question_lower = question_lower.replace(original_word, "", 1).strip()
            palavras = self.gerar_combinacoes(question_lower)
            list_lower = [x.lower() for x in self.pdf_contents[code]['DISCIPLINA'].unique().tolist()]
            for palavra in palavras:
                match = process.extractOne(palavra, list_lower, scorer=fuzz.ratio)
                if match[1] > 40 and match[1] > best_match[1]:
                    best_match = match

            if best_match[0]:
                df = self.pdf_contents[code]
                result = df[df['DISCIPLINA'] == best_match[0].upper()]['HORÁRIO'].to_string(index=False)
                time_start, time_end = result.split(" - ")
                return f"O horário da disciplina {best_match[0]} de {full_name} começa às {time_start} e termina às {time_end}."
            else:
                return f"⚠️ Disciplina não encontrado na pergunta: {question}"

        else:
            return f"⚠️ Curso não encontrado na pergunta: {question}"
        
    def response_professor_question(self, question: str) -> str:
        """Responde perguntas sobre professores de disciplinas"""
        best_match = [None, 0]
        question_lower = question.lower()
        code, full_name, original_word = self._search_course(question)
        # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
        if code and full_name:
            question_lower = question_lower.replace(original_word, "", 1).strip()
            palavras = self.gerar_combinacoes(question_lower)
            list_lower = [x.lower() for x in self.pdf_contents[code]['DISCIPLINA'].unique().tolist()]
            for palavra in palavras:
                match = process.extractOne(palavra, list_lower, scorer=fuzz.ratio)
                if match[1] > 40 and match[1] > best_match[1]:
                    best_match = match
            if best_match[0]:
                df = self.pdf_contents[code]
                result = df[df['DISCIPLINA'] == best_match[0].upper()]['PROFESSOR(A)'].to_string(index=False)
                return f"O professor da disciplina {best_match[0]} de {full_name} é {result.strip()}"
            else:
                return f"⚠️ Disciplina não encontrado na pergunta: {question}"

        else:
            return f"⚠️ Curso não encontrado na pergunta: {question}"

        
    def response_sala_question(self, question: str) -> str:
        """Responde perguntas sobre salas de disciplinas"""
        best_match = [None, 0]
        question_lower = question.lower()
        code, full_name, original_word = self._search_course(question)
        # print(f"🔍 DEBUG - Pergunta processada: '{question_lower}'")
        if code and full_name:
            question_lower = question_lower.replace(original_word, "", 1).strip()
            palavras = self.gerar_combinacoes(question_lower)
            list_lower = [x.lower() for x in self.pdf_contents[code]['DISCIPLINA'].unique().tolist()]
            for palavra in palavras:
                match = process.extractOne(palavra, list_lower, scorer=fuzz.ratio)
                # print(f"🔍 DEBUG - Verificando: {palavra} (match: {match[0]}, score {match[1]})")
                if match[1] > 40 and match[1] > best_match[1]:
                    best_match = match
            if best_match[0]:
                # print(f"🔍 DEBUG - Melhor match encontrado: {best_match[0]} com score {best_match[1]}")
                df = self.pdf_contents[code]
                result = df[df['DISCIPLINA'] == best_match[0].upper()]['SALA'].to_string(index=False)
                return f"A sala da disciplina {best_match[0]} de {full_name} é {result.strip()}"
            else:
                return f"⚠️ Disciplina não encontrado na pergunta: {question}"

        else:
            return f"⚠️ Curso não encontrado na pergunta: {question}"


if __name__ == "__main__":
    # Teste rápido do PDFReader
    pdf =  PDFReader(data_folder="data")
    # Exemplo de perguntas, DESCOMENTE PARA TESTAR

    # x = pdf.answer_question("Qual o horário da topicos especiais de filiencias da computação")
    # x = pdf.answer_question("Qual o horário da topicos especiais de defensores computação")
    # x = pdf.answer_question("Qual é o professor da disciplina inteligencia 1 do ciência da computação?")
    # x = pdf.answer_question("qual o horário da disciplina entre a gente é computacional, um fim é a computação")
    # x = pdf.answer_question("Qual o horário da disciplina entre a gente é computacional, um fim é a computação.")
    # x = pdf.answer_question("qual a sala da disciplina inteligente é computacional 1?")
    # x = pdf.answer_question("qual a sala da disciplina introdução à ciência da comtação é ciência da comtação?")
    # x = pdf.answer_question("Qual o horário da aula de sistas digitais de filisias da computação")
    # x = pdf.answer_question("qual a sala de introdução do que é a indústria na vál de offshore. defene.")
    print(x)