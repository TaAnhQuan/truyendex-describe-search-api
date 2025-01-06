import sqlite3
from sentence_transformers import SentenceTransformer
import json

connection_obj = sqlite3.connect('./describe_search/manga_embedding.sqlite3')
model = SentenceTransformer('semantic_model')

cursor_obj = connection_obj.cursor() 

get_data_statement = '''SELECT * FROM manga'''
  
cursor_obj.execute(get_data_statement) 

output = cursor_obj.fetchall() 

embedding_data = []
for row in output: 
    temp = list(row[1:])
    temp_embedding =  model.encode(temp, convert_to_tensor=True)
    tensor_as_json = json.dumps(temp_embedding.tolist())
    embedding_data.append(tensor_as_json)

print("Write embedding data to table")
create_table_statement = '''ALTER TABLE manga ADD COLUMN embedding TEXT'''
cursor_obj.execute(create_table_statement)
for i in embedding_data:
    cursor_obj.executemany('''INSERT INTO manga (embedding) VALUES (?)''', i)
print("Finish write embedding data to table")

connection_obj.commit() 
  
# Close the connection 
connection_obj.close()