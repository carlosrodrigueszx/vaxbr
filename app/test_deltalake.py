import db

df = db.pd.DataFrame(
    {
        "vax_id": ["1", "2", "3"],
        "type": ["bacterian", "viral", "viral"],
        "manufacture_date": ["2021-01-01", "2022-03-03", "2023-04-04"],
        "qtt": [1, 1, 2],
        "available": [True, True, False]
    }
)

df.columns = df.columns.str.lower()

# print(df.head(100))

path_file = "/home/daniel/Projects/vaxbr/app/tmp/vacines"

db.write_deltalake(path_file, df)

# exibindo a tabela
dt = db.DeltaTable(path_file)
print(dt.to_pandas().head(100))