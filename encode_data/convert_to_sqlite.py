import sqlite3
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Path to the CSV file
CSV_FILE = ".\encode_data\manga.csv"

# SQLite database file
DB_FILE = "manga.sqlite3"

connection_obj = sqlite3.connect('manga.sqlite3')
model = SentenceTransformer('semantic_model')

# Create SQLite database and table
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manga (
            manga_id TEXT PRIMARY KEY,
            encode_data TEXT
        );
    """)
    connection.commit()

def populate_database(connection, csv_file):
    df = pd.read_csv(csv_file)

    df = df.drop(['type', 'score', 'scored_by', 'status', 'volumes', 'chapters', 'start_date', 
              'end_date', 'members', 'favorites', 'approved', 'created_at_before', 'updated_at', 
              'real_start_date', 'real_end_date', 'main_picture', 'url', 'serializations', 'title_english', 'title_japanese'], axis=1)
    
    df = df.map(lambda x: np.nan if x == '[]' else x)
    df = df.dropna()

    df['sfw'] = df['sfw'].astype(bool)
    df = df.dropna()

    df['combined'] = df.drop(columns=['manga_id']).apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    df['embedding'] = df['combined'].apply(lambda x: model.encode(x, convert_to_tensor=True))
    df['embedding_str'] = df['embedding'].apply(lambda emb: ','.join(map(str, emb)))
    df = df.drop(['combined', 'sfw', 'genres', 'themes', 'demographics', 'authors', 'synopsis', 'background', 'title_synonyms', "embedding"], axis=1)
    df = df.dropna()
    df = df.drop_duplicates()
    df.to_sql('manga', connection, if_exists='replace', index=False)

def main():
    connection = sqlite3.connect(DB_FILE)

    try:
        create_table(connection)
        populate_database(connection, CSV_FILE)
        print(f"Data from '{CSV_FILE}' successfully inserted into '{DB_FILE}'")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()