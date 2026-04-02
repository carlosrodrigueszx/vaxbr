import csv
from faker import Faker

fake = Faker()

# Criando dados falsos para um banco de dados de usuários
with open('vaccines.csv', 'w', newline="") as csv_f:
    # names = ["Moderna", "Sputnik V", "Covaxin"]
    manufacturers = ["Pfizer", "Moderna", "AstraZeneca", "Johnson & Johnson", "Sinovac"]
    targets = ["SARS-CoV-2", "Influenza", "Rinovírus", "Sincicial", "HPV"]
    illnesses = ["COVID-19", "Flu", "HPV", "MMR"]

    fieldnames = ['name', 'target', 'illness', 'quantity', 'id_manufac']

    writer = csv.DictWriter(csv_f, fieldnames=fieldnames)


    writer.writeheader()

    for _ in range(1000):
        writer.writerow({
            'name': fake.random_choices(manufacturers),
            'target': fake.random_choices(targets),
            'illness': fake.random_choices(illnesses),
            'quantity': fake.random_number(fix_len=True, digits=4),
            'id_manufac': fake.random_digit()
        })

