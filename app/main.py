import tools, csv

fake = tools.Faker()

# Aqui o Faker gera um .csv de 1000 linhas e preenche com dados fictícios, é necessário configurar os fields e localização
with open('fakeusers.csv', 'w', newline='') as csv_file:
    fieldnames = ['nome', 'email', 'data_nascimento']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for _ in range(1000):
        writer.writerow({
            'nome': fake.name(),
            'email': fake.email(),
            'data_nascimento': fake.date_of_birth()
        })
