import random
import pandas as pd

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
    def __init__(self, disciplinas_por_periodo, professores, geracao=0, cromossomo=None):
        self.disciplinas_por_periodo = disciplinas_por_periodo
        self.professores = professores
        self.periodos = list(disciplinas_por_periodo.keys())
        self.dias = [1, 2, 3, 4, 5]
        self.horarios_por_dia = 4
        self.geracao = geracao
        self.cromossomo = cromossomo if cromossomo is not None else []
        self.nota_avaliacao = 0

        if not self.cromossomo:
            self.gerar_cromossomo_inicial()

    # GERA O CROMOSSOMO INICIAL: AULAS E PROFESSORES ALEATÓRIOS
    def gerar_cromossomo_inicial(self):
        for periodo in self.periodos:
            for dia in self.dias:
                for horario in range(1, self.horarios_por_dia + 1):
                    disciplina = random.choice(self.disciplinas_por_periodo[periodo])
                    professor = random.choice(self.professores)
                    self.cromossomo.append(Aula(disciplina, professor, periodo, dia, horario))

    def avaliacao(self):
        nota = 0

        # Define o peso da penalidade para conflitos de horário do professor
        peso_conflito_professor = 1

        # Inicializa o contador de conflitos de professor
        conflitos_professor = 0

        # Cria um dicionário para contar as aulas que cada professor tem por dia e horário específico
        aulas_professor_dia_horario = {
            prof: {dia: {horario: 0 for horario in range(1, self.horarios_por_dia + 1)} for dia in self.dias}
            for prof in self.professores
        }

        # Percorre cada aula no cromossomo
        for aula in self.cromossomo:
            # Incrementa o contador de aulas do professor no dia e horário específicos
            aulas_professor_dia_horario[aula.professor][aula.dia][aula.horario] += 1
            # Se o professor tem mais de uma aula no mesmo dia e horário, conta como um conflito
            if aulas_professor_dia_horario[aula.professor][aula.dia][aula.horario] > 1:
                conflitos_professor += 1

        # Subtrai da nota a penalidade para conflitos de professor
        nota -= peso_conflito_professor * conflitos_professor

        # Atualiza a nota de avaliação do horário
        self.nota_avaliacao = nota

    @staticmethod
    def crossover(horario1, horario2):
        ponto_de_corte = 5
        filho1_cromossomo = horario1.cromossomo[:ponto_de_corte] + horario2.cromossomo[ponto_de_corte:]
        filho2_cromossomo = horario2.cromossomo[:ponto_de_corte] + horario1.cromossomo[ponto_de_corte:]

        filho1 = Horario(horario1.disciplinas_por_periodo, horario1.professores, geracao=horario1.geracao + 1, cromossomo=filho1_cromossomo)
        filho2 = Horario(horario2.disciplinas_por_periodo, horario2.professores, geracao=horario2.geracao + 1, cromossomo=filho2_cromossomo)

        return [filho1, filho2]

    @staticmethod
    def mutacao(horario, taxa_mutacao):
        for i in range(len(horario.cromossomo)):
            if random.random() < taxa_mutacao:
                disciplina = random.choice(horario.disciplinas_por_periodo[horario.cromossomo[i].periodo])
                professor = random.choice(horario.professores)
                periodo = horario.cromossomo[i].periodo
                dia = horario.cromossomo[i].dia
                horario_cromossomo = horario.cromossomo[i].horario
                horario.cromossomo[i] = Aula(disciplina, professor, periodo, dia, horario_cromossomo)

    @staticmethod
    def proxima_geracao(populacao, taxa_mutacao):
        nova_populacao = []
        selecionados = Horario.selecao_torneio(populacao)

        for i in range(0, len(selecionados), 2):
            pai1 = selecionados[i]
            pai2 = selecionados[i + 1]
            filhos = Horario.crossover(pai1, pai2)
            nova_populacao.extend(filhos)

        for horario in nova_populacao:
            Horario.mutacao(horario, taxa_mutacao)

        return nova_populacao

    @staticmethod
    def selecao_torneio(populacao, tamanho_torneio=3):
        vencedores = []
        for _ in range(len(populacao)):
            torneio = random.sample(populacao, tamanho_torneio)
            vencedor = max(torneio, key=lambda horario: horario.nota_avaliacao)
            vencedores.append(vencedor)
        return vencedores

    def to_dataframe_with_conflicts(self):
        data = {
            'Disciplina': [aula.disciplina for aula in self.cromossomo],
            'Professor': [aula.professor for aula in self.cromossomo],
            'Período': [aula.periodo for aula in self.cromossomo],
            'Dia': [aula.dia for aula in self.cromossomo],
            'Horário': [aula.horario for aula in self.cromossomo],
        }
        df = pd.DataFrame(data)

        # Identificando conflitos
        df['Conflito'] = False
        aulas_professor_dia = {prof: {dia: 0 for dia in self.dias} for prof in self.professores}

        for idx, row in df.iterrows():
            professor = row['Professor']
            dia = row['Dia']
            aulas_professor_dia[professor][dia] += 1
            if aulas_professor_dia[professor][dia] > 1:
                df.at[idx, 'Conflito'] = True

        return df

    def __repr__(self):
        return f"Horario(G{self.geracao}, Cromossomo: {self.cromossomo}, Avaliação: {self.nota_avaliacao})"


def ordenar_por_avaliacao(populacao):
    return sorted(populacao, key=lambda x: x.nota_avaliacao, reverse=True)


def main():
    disciplinas_por_periodo = {
        1: ["MAT101", "POR102", "HIS103", "GEO104", "CIE105"],
        2: ["ING106", "EDF107", "ART108", "BIO109", "QUI110"],
        3: ["FIS111", "SOC112", "FIL113", "INF114", "MUS115"],
        4: ["TEA116", "DES117", "LIT118", "RED119", "ESP120"],
        5: ["FRA121", "ALE122", "EAM123", "ROB124", "AST125"]
    }
    professores = ["Prof_A", "Prof_B", "Prof_C", "Prof_D", "Prof_E", "Prof_F", "Prof_G", "Prof_H", "Prof_I", "Prof_J", "Prof_K", "Prof_L"]

    # Gerar a primeira população
    tamanho_populacao = 200
    populacao_inicial = [Horario(disciplinas_por_periodo, professores) for _ in range(tamanho_populacao)]

    # Avaliar cada horário
    for horario in populacao_inicial:
        horario.avaliacao()

    # Ordenar a população inicial por avaliação
    populacao_ordenada = ordenar_por_avaliacao(populacao_inicial)

    # Exibir a população inicial e suas avaliações
    for i, horario in enumerate(populacao_ordenada, start=1):
        print(f"\nHorário {i} - Avaliação: {horario.nota_avaliacao}")
        df = horario.to_dataframe_with_conflicts()

        # Imprimir a tabela destacando conflitos
        for _, row in df.iterrows():
            conflict_mark = " (Conflito)" if row['Conflito'] else ""
            print(f"{row['Disciplina']} | {row['Professor']} | Período {row['Período']} | Dia {row['Dia']} | Horário {row['Horário']}{conflict_mark}")

if __name__ == "__main__":
    main()
