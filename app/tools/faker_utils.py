from faker import Faker
import random
import csv

fake = Faker('pt_BR')

def gerar_vacinas(quantidade=1000):
    regras = {
        'Tuberculose': {
            'nomes': ['BCG-ID', 'BCG Moreau'],
            'publicos': ['Recém-nascidos']
        },
        'Hepatite B': {
            'nomes': ['Engerix B', 'Euvax B', 'Recombivax HB'],
            'publicos': ['Recém-nascidos, Adultos, Profissionais da Saúde']
        },
        'Poliomielite': {
            'nomes': ['VIP (Salk)', 'VOP (Sabin)', 'Imovax Polio'],
            'publicos': ['Crianças (até 5 anos)']
        },
        'Rotavírus': {
            'nomes': ['Rotarix', 'Rotateq'],
            'publicos': ['Bebês (2 a 6 meses)']
        },
        'Meningite C': {
            'nomes': ['Meningocócica C', 'Menjugate', 'Meningitec'],
            'publicos': ['Crianças, Adolescentes']
        },
        'Meningite ACWY': {
            'nomes': ['Menveo', 'Nimenrix', 'Menquadfi'],
            'publicos': ['Adolescentes, Viajantes']
        },
        'Meningite B': {
            'nomes': ['Bexsero', 'Trumenba'],
            'publicos': ['Crianças, Adolescentes']
        },
        'Pneumonia (Pneumocócica)': {
            'nomes': ['Pneumo 10v', 'Pneumo 13v', 'Pneumo 15v'],
            'publicos': ['Crianças, Idosos']
        },
        'Pneumonia (Idosos/Risco)': {
            'nomes': ['Pneumovax 23'],
            'publicos': ['Idosos, Imunossuprimidos']
        },
        'Sarampo, Caxumba, Rubéola': {
            'nomes': ['Tríplice Viral (SCR)', 'Priorix', 'MMR-II'],
            'publicos': ['Crianças, Adultos']
        },
        'Varicela (Catapora)': {
            'nomes': ['Varivax', 'Varilrix'],
            'publicos': ['Crianças (15 meses), Adultos suscetíveis']
        },
        'Hepatite A': {
            'nomes': ['Havrix', 'Avaxim', 'Vaqta'],
            'publicos': ['Crianças, Viajantes']
        },
        'Difteria, Tétano e Coqueluche': {
            'nomes': ['Pentavalente', 'DTP (Tríplice Bacteriana)'],
            'publicos': ['Crianças']
        },
        'Haemophilus influenzae tipo b': {
            'nomes': ['Act-Hib', 'Hiberix'],
            'publicos': ['Crianças']
        },
        'HPV (Papilomavírus)': {
            'nomes': ['Gardasil 4', 'Gardasil 9', 'Cervarix'],
            'publicos': ['Meninos e Meninas (9 a 14 anos), Imunossuprimidos']
        },
        'Difteria e Tétano (Reforço)': {
            'nomes': ['Dupla Adulto (dt)'],
            'publicos': ['Adultos (reforço a cada 10 anos)']
        },
        'Coqueluche (Gestante)': {
            'nomes': ['dTpa (Adacel)', 'Boostrix'],
            'publicos': ['Gestantes, Profissionais de berçário']
        },
        'Febre Amarela': {
            'nomes': ['Stamaril', 'FA (Bio-Manguinhos)'],
            'publicos': ['Residentes em áreas de risco, Viajantes']
        },
        'Gripe Influenza (Trivalente)': {
            'nomes': ['Influvac', 'Fluarix'],
            'publicos': ['Idosos, Gestantes, Crianças']
        },
        'Gripe Influenza (Quadrivalente)': {
            'nomes': ['FluQuadri', 'Vaxigrip Tetra'],
            'publicos': ['População Geral (acima de 6 meses)']
        },
        'Gripe (Alta Concentração)': {
            'nomes': ['Efluelda'],
            'publicos': ['Idosos']
        },
        'Herpes Zóster': {
            'nomes': ['Shingrix'],
            'publicos': ['Adultos (50+), Imunossuprimidos']
        },
        'Dengue': {
            'nomes': ['Qdenga', 'Dengvaxia'],
            'publicos': ['Crianças e Adolescentes (4 a 14 anos)']
        },
        'COVID-19 (mRNA)': {
            'nomes': ['Comirnaty (Pfizer)', 'Spikevax (Moderna)'],
            'publicos': ['População Geral, Grupos de Risco']
        },
        'COVID-19 (Vetor Viral)': {
            'nomes': ['Janssen', 'Vaxzevria (AstraZeneca)'],
            'publicos': ['Adultos']
        },
        'COVID-19 (Inativada)': {
            'nomes': ['CoronaVac'],
            'publicos': ['Crianças, Adultos']
        },
        'Febre Tifoide': {
            'nomes': ['Typhim Vi', 'Vivotif'],
            'publicos': ['Viajantes para áreas endêmicas']
        },
        'Cólera': {
            'nomes': ['Dukoral'],
            'publicos': ['Viajantes, Zonas de surto']
        },
        'Raiva Humana (Pré-exposição)': {
            'nomes': ['Verorab', 'Vacina Antirrábica Humana'],
            'publicos': ['Veterinários, Espeleólogos']
        },
        'Raiva Humana (Pós-exposição)': {
            'nomes': ['Vacina + Soro Antirrábico'],
            'publicos': ['Pessoas mordidas por animais']
        },
        'Malária': {
            'nomes': ['Mosquirix', 'R21'],
            'publicos': ['Crianças em áreas endêmicas']
        },
        'Varíola dos Macacos (Mpox)': {
            'nomes': ['Jynneos', 'Imvanex'],
            'publicos': ['Grupos de alto risco, Contatos próximos']
        },
        'Meningite A, C, W, Y, B (Combinada)': {
            'nomes': ['MenACWY + Bexsero'],
            'publicos': ['Adolescentes em surtos']
        },
        'Pneumonia 20-valente': {
            'nomes': ['Prevenar 20'],
            'publicos': ['Idosos']
        },
        'Vírus Sincicial Respiratório (VSR)': {
            'nomes': ['Arexvy', 'Abrysvo'],
            'publicos': ['Idosos, Gestantes']
        },
        'Hepatite A + B (Combinada)': {
            'nomes': ['Twinrix'],
            'publicos': ['Adultos, Viajantes']
        },
        'Difteria, Tétano, Coqueluche, Polio e Hib': {
            'nomes': ['Pentavalente Acellular'],
            'publicos': ['Crianças']
        },
        'Difteria, Tétano, Coqueluche, Polio, Hib e HepB': {
            'nomes': ['Hexavalente'],
            'publicos': ['Crianças']
        }
    }

    cnpjs_fabricantes = [fake.cnpj() for _ in range(50)]
    
    lista_vacinas = []
    doencas_disponiveis = list(regras.keys())

    print(f"Gerando {quantidade} registros com lógica de saúde...")

    for _ in range(quantidade):
        doenca_sorteada = random.choice(doencas_disponiveis)
        opcoes = regras[doenca_sorteada]
        nome_base = random.choice(opcoes['nomes'])
        
        # Adiciona um sufixo de lote para não ficarem 1000 nomes idênticos
        nome_final = f"{nome_base} ({fake.bothify(text='LT-####')})"
        
        publico_final = ', '.join(opcoes['publicos'])

        vacina = {
            'name': nome_final, # sem lote fica nome_base
            'target': publico_final,
            'illness': doenca_sorteada,
            'quantity': random.randint(50, 2000),
            'id_manufac': random.choice(cnpjs_fabricantes)
        }
        lista_vacinas.append(vacina)
    
    return lista_vacinas

dados_vacinas = gerar_vacinas(1000)

nome_arquivo = 'vacinas_populadas.csv'
with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=dados_vacinas[0].keys())
    escritor.writeheader()
    escritor.writerows(dados_vacinas)

print(f"Sucesso! Arquivo '{nome_arquivo}' gerado.")