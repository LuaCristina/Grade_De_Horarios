import random
import pandas as pd
from tabulate import tabulate


# ATRIBUTOS DE CADA AULA
class Aula:
    def __init__(self, disciplina, professor, periodo, dia, horario):
        self.disciplina = disciplina
        self.professor = professor
        self.periodo = periodo
        self.dia = dia
        self.horario = horario

    def __repr__(self):
        return f"Aula({self.disciplina}, {self.professor}, Sem{self.periodo}, D{self.dia}, H{self.horario})"


# REGRAS/ATRIBUTOS DEFINIDAS PARA A CONSTRUÇAO DO HORÁRIO
class Horario:
    def __init__(self, disciplinas, professores, geracao=0, cromossomo=None):
        self.disciplinas = disciplinas
        self.professores = professores
        self.periodos = [1, 2, 3, 4, 5]
        self.dias = [1, 2, 3, 4, 5]
        self.horarios_por_dia = 4
        self.geracao = geracao
        self.cromossomo = cromossomo if cromossomo is not None else []
        self.nota_avaliacao = 0

        if not self.cromossomo:
            self.gerar_cromossomo_inicial()

#GERA O CROMOSSOMO INICIAL: AULAS E PROFESSORES ALEATÓRIOS
#PRIMEIRA POP
    def gerar_cromossomo_inicial(self):
        for periodo in self.periodos:
            for dia in self.dias:
                for horario in range(1, self.horarios_por_dia + 1):
                    disciplina = random.choice(self.disciplinas)
                    professor = random.choice(self.professores)
                    self.cromossomo.append(Aula(disciplina, professor, periodo, dia, horario))

    def avaliacao(self):
        nota = 0
        conflitos_professor = 0
        aulas_professor_dia = {prof: {dia: 0 for dia in self.dias} for prof in self.professores}
        aulas_disciplina_periodo = {disc: {periodo: 0 for periodo in self.periodos} for disc in self.disciplinas}

        for aula in self.cromossomo:
            aulas_professor_dia[aula.professor][aula.dia] += 1
            if aulas_professor_dia[aula.professor][aula.dia] > 1:
                conflitos_professor += 1

            aulas_disciplina_periodo[aula.disciplina][aula.periodo] += 1

        nota -= conflitos_professor

        for periodos in aulas_disciplina_periodo.values():
            for aulas in periodos.values():
                if aulas > 1:
                    nota -= 1

        self.nota_avaliacao = nota

    def crossover(self, outro_horario):
        ponto_de_corte = 10
        filho1_cromossomo = self.cromossomo[:ponto_de_corte] + outro_horario.cromossomo[ponto_de_corte:]
        filho2_cromossomo = outro_horario.cromossomo[:ponto_de_corte] + self.cromossomo[ponto_de_corte:]

        filho1 = Horario(self.disciplinas, self.professores, geracao=self.geracao + 1, cromossomo=filho1_cromossomo)
        filho2 = Horario(self.disciplinas, self.professores, geracao=self.geracao + 1, cromossomo=filho2_cromossomo)

        return [filho1, filho2]

    def to_dataframe(self):
        data = {
            'Disciplina': [aula.disciplina for aula in self.cromossomo],
            'Professor': [aula.professor for aula in self.cromossomo],
            'Período': [aula.periodo for aula in self.cromossomo],
            'Dia': [aula.dia for aula in self.cromossomo],
            'Horário': [aula.horario for aula in self.cromossomo],
        }
        df = pd.DataFrame(data)
        return df

    def __repr__(self):
        return f"Horario(G{self.geracao}, Cromossomo: {self.cromossomo}, Avaliação: {self.nota_avaliacao})"

def main():
    disciplinas = ["MAT101", "POR102", "HIS103", "GEO104", "CIE105", "ING106", "EDF107", "ART108", "BIO109", "QUI110", "FIS111", "SOC112", "FIL113", "INF114", "MUS115", "TEA116", "DES117", "LIT118", "RED119", "ESP120", "FRA121", "ALE122", "EAM123", "ROB124", "AST125"]
    professores = ["Prof_A", "Prof_B", "Prof_C", "Prof_D", "Prof_E", "Prof_F", "Prof_G", "Prof_H", "Prof_I", "Prof_J", "Prof_K", "Prof_L"]

    # Criar dois horários iniciais
    horario_inicial_1 = Horario(disciplinas, professores)
    horario_inicial_2 = Horario(disciplinas, professores)

    # Imprimir os horários iniciais em forma de tabela

    # Gerar a primeira população
    tamanho_populacao = 50
    populacao_inicial = [Horario(disciplinas, professores) for _ in range(tamanho_populacao)]

    # Avaliar cada horário
    for horario in populacao_inicial:
        horario.avaliacao()

    # Exibir a população inicial e suas avaliações
    for i, horario in enumerate(populacao_inicial, start=1):
        print(f"\nHorário {i} - Avaliação: {horario.nota_avaliacao}")
        # Converter as aulas para um DataFrame
        df = pd.DataFrame([vars(aula) for aula in horario.cromossomo])
        print(tabulate(df, headers='keys', tablefmt='psql'))




    # print("Horário Inicial 1:")
    # print(tabulate(horario_inicial_1.to_dataframe(), headers='keys', tablefmt='psql'))
    #
    # print("\nHorário Inicial 2:")
    # print(tabulate(horario_inicial_2.to_dataframe(), headers='keys', tablefmt='psql'))
    #
    # # Realizar o crossover e gerar filhos
    # filhos = horario_inicial_1.crossover(horario_inicial_2)
    #
    # # Imprimir os filhos em forma de tabela
    # for i, filho in enumerate(filhos, start=1):
    #     print(f"\nFilho {i}:")
    #     print(tabulate(filho.to_dataframe(), headers='keys', tablefmt='psql'))

if __name__ == "__main__":
    main()
