import pandas as pd
from tabula import read_pdf
import os

def infer_datatype(val, column):
    try:
        if val.count('/') == 2 or val.count('-') == 2:
            return 'DATE'
        elif int(val):
            return 'SMALLINT'
    except ValueError:
        pass
    max_length = column.astype(str).map(len).max()
    return f'VARCHAR({max_length})'
columns = ['KHUVUC', 'PHIEUCH', 'DONGVAT', 'CTCH']
pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

create_table_statements = []
insert_into_statements = []

for pdf_file in pdf_files:
    tables = read_pdf(pdf_file, pages='all', multiple_tables=True, lattice=True)
    tables.pop(0) 
    for i, table in enumerate(tables):
        headers = table.columns.tolist()
        create_table_sql = f"CREATE TABLE {columns[i]} (\n"
        create_table_sql += ",\n".join([f"\t{header} {infer_datatype(str(table.loc[0, header]), table[header])}" for header in headers])
        create_table_sql += ",\n);"
        create_table_statements.append(create_table_sql)

        for _, row in table.iterrows():
            insert_into_sql = f"INSERT INTO {columns[i]} VALUES ("
            insert_into_sql += ", ".join([f"'{cell}'" if infer_datatype(str(cell), table[header]) != 'SMALLINT' else str(cell) for cell, header in zip(row, headers)])
            insert_into_sql += ");"
            insert_into_statements.append(insert_into_sql)

with open('output.txt', 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(create_table_statements) + '\n')
    output_file.write('\n'.join(insert_into_statements) + '\n')
