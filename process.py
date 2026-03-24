import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv
import re

from queries import SELECT_ALL_OKRES_OBEC_ID_QUERY, INSERT_DATA_CINZOVNI_DOMY_QUERY

def load_xlsx(file_path):
    try:
        data = pd.read_excel(file_path, sheet_name=0)
        return data
    except Exception as e:
        print(f"Error reading the XLSX file: {e}")
        return None

def get_okres_obec_id_mapping(cursor):
    cursor.execute(SELECT_ALL_OKRES_OBEC_ID_QUERY)
    mapping = {row[1]: row[0] for row in cursor.fetchall()}
    return mapping

if __name__ == "__main__":
    load_dotenv()
    cinzdomy = load_xlsx("data/cinzdomy.xlsx")

    # 1. Create a new column "OKRES_OBEC" by combining "Okres" and "MČ"
    cinzdomy["OKRES_OBEC"] = cinzdomy["Okres"] + "-" + cinzdomy["MČ"]
    # 2. Extract latitude and longitude from the "GPS" column using regular expressions
    cinzdomy[["LATITUDE", "LONGITUDE"]] = cinzdomy["GPS"].str.extract(r'N\s*([\d.,]+)\s*E\s*([\d.,]+)')
    

    with mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("PASSWORD"),
        database="domy") as conn:
        with conn.cursor() as cursor:
            # 3. Get the mapping of "OKRES_OBEC" to "ID" from the "okres_obec" table
            okres_obec_id_mapping = get_okres_obec_id_mapping(cursor)

            # 4. Map the "OKRES_OBEC" column to the corresponding "ID" from the "okres_obec" table
            cinzdomy["OKRES_OBEC_ID"] = cinzdomy["OKRES_OBEC"].map(okres_obec_id_mapping)
            
            # 5. Adjust the column names and data types
            cinzdomy_final = cinzdomy[["ID", "ID Subjektu", "Využití budovy", "OKRES_OBEC_ID", "Ulice č.p./č.e.", "MČ", "PSČ", "Vymezené byty", "Vlastnictví", "Typ budovy", "LONGITUDE", "LATITUDE"]]
            cinzdomy_final = cinzdomy_final.fillna("")
            cinzdomy_final["Vymezené byty"] = cinzdomy_final["Vymezené byty"].apply(lambda x: True if x == "Ano" else False)
            data = cinzdomy_final.values.tolist()

            # 6. Insert the data into the "cinzovni_domy" table using the INSERT_DATA_CINZOVNI_DOMY_QUERY
            cursor.executemany(INSERT_DATA_CINZOVNI_DOMY_QUERY, data)

            conn.commit()