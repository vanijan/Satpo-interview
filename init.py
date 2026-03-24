import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

from queries import CREATE_TABLE_CINZOVNI_DOMY_QUERY, DROP_ADRESY_KATASTRALNICH_URADU_QUERY, DROP_CINZOVNI_DOMY_QUERY, DROP_OKRES_OBEC_QUERY, CREATE_TABLE_ADRESY_QUERY, CREATE_TABLE_OKRES_OBEC_QUERY, INSERT_DATA_QUERY_ADRESY_QUERY, INSERT_DATA_OKRES_OBEC_QUERY

load_dotenv()

def read_csv(file_path):
    try:
        data = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
        return data
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None

if __name__ == "__main__":
    adresy_katastalnich_uradu = read_csv("data/SC_PRACRES_DOTAZ.csv")
    seznam_katastalnich_uradu = read_csv("data/SC_SEZNAMKUKRA_DOTAZ.csv")
    ########
    # 1 - Create a table with the names of the cadastral offices adresses and their codes, with mapping of the codes to the names of the cadastral offices
    # 1.1 - Create a new column "CISLO_POPISNE_CELE" by combining "CISLO_DOMOVNI" and "CISLO_ORIENTACNI"
    print(adresy_katastalnich_uradu.head())
    adresy_katastalnich_uradu["CISLO_POPISNE_CELE"] = (
        adresy_katastalnich_uradu["CISLO_DOMOVNI"].astype(str)
        + "/"
        + adresy_katastalnich_uradu["CISLO_ORIENTACNI"].fillna('').astype(str)
    ).str.rstrip('/')
    
    # 1.2 - Create a new column "ADRESA" by combining "NAZEV_ULICE", "CISLO_POPISNE_CELE", "NAZEV_OBCE", and "PSC"
    adresy_katastalnich_uradu["ADRESA"] = (
        adresy_katastalnich_uradu["NAZEV_ULICE"] 
        + " " + adresy_katastalnich_uradu["CISLO_POPISNE_CELE"] 
        + ", " + adresy_katastalnich_uradu["OBEC"] 
        + ", " + adresy_katastalnich_uradu["PSC"].astype(str)
    )
    
    # 1.3 Create a mapping from column "NAZEV" to "KOD"
    mapping_nazev_to_kod = dict(zip(adresy_katastalnich_uradu["NAZEV"], adresy_katastalnich_uradu["KOD"]))

    # 1.4 Keep only the relevant columns for the final table
    adresy_katastalnich_uradu_final = adresy_katastalnich_uradu[["KOD", "NAZEV", "ADRESA", "TELEFON"]]
    adresy_katastalnich_uradu_final.rename(columns={"KOD": "KOD_PRACOVISTE"}, inplace=True)
    adresy_katastalnich_uradu_final.to_csv("adresy_katastalnich_uradu_final.csv", index=False)
    

    ########
    # 2 - Create a table that maps combination of OKRES and OBEC to the code of the cadastral office
    # 2.1 - Create a new column "OKRES_OBEC" by combining "OKRES" and "OBEC"
    seznam_katastalnich_uradu["OKRES_NAZEV"] = seznam_katastalnich_uradu["OKRES_NAZEV"].fillna('Praha').astype(str)
    seznam_katastalnich_uradu["OKRES_OBEC"] = seznam_katastalnich_uradu["OKRES_NAZEV"] + "-" + seznam_katastalnich_uradu["OBEC_NAZEV"]

    # 2.2 - Map the "KOD_PRACOVISTE" to the "OKRES_OBEC" using the mapping created in step 1.3
    seznam_katastalnich_uradu["KOD_PRACOVISTE"] = seznam_katastalnich_uradu["PRARES_NAZEV"].map(mapping_nazev_to_kod)

    # 2.3 - Create a mapping from "OKRES_OBEC" to "KU_KOD"
    mapping_okresobec_to_kod = dict(zip(seznam_katastalnich_uradu["OKRES_OBEC"], seznam_katastalnich_uradu["KU_KOD"]))
    
    # 2.4 - Keep only the relevant columns for the final table
    
    seznam_katastalnich_uradu_final = seznam_katastalnich_uradu[["OKRES_OBEC", "KOD_PRACOVISTE", "KRAJ_NAZEV"]]
    seznam_katastalnich_uradu_final = seznam_katastalnich_uradu_final.drop_duplicates().reset_index(drop=True)
    seznam_katastalnich_uradu_final["ID"] = seznam_katastalnich_uradu_final.index
    seznam_katastalnich_uradu_final = seznam_katastalnich_uradu_final[["ID", "OKRES_OBEC", "KOD_PRACOVISTE", "KRAJ_NAZEV"]]
    seznam_katastalnich_uradu_final.to_csv("seznam_katastalnich_uradu_final.csv", index=False)


    ########
    # 3 - Create a MySQL database and insert the data from the two tables created

    with mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("PASSWORD"),
        database="domy"
    ) as conn:
        with conn.cursor() as cursor:
            # 3.1 - Create the tables in the MySQL database
            cursor.execute(DROP_CINZOVNI_DOMY_QUERY)
            cursor.execute(DROP_OKRES_OBEC_QUERY)
            cursor.execute(DROP_ADRESY_KATASTRALNICH_URADU_QUERY)
            cursor.execute(CREATE_TABLE_ADRESY_QUERY)
            cursor.execute(CREATE_TABLE_OKRES_OBEC_QUERY)
            cursor.execute(CREATE_TABLE_CINZOVNI_DOMY_QUERY)
            
            # 3.2 - Insert the data into adresy_katastralnich_uradu
            data = adresy_katastalnich_uradu_final[["KOD_PRACOVISTE", "NAZEV", "ADRESA", "TELEFON"]].values.tolist()

            cursor.executemany(INSERT_DATA_QUERY_ADRESY_QUERY, data)

            # 3.3 - Insert the data into seznam_katastralnich_uradu
            data = seznam_katastalnich_uradu_final[["ID", "OKRES_OBEC", "KOD_PRACOVISTE", "KRAJ_NAZEV"]].values.tolist()
            cursor.executemany(INSERT_DATA_OKRES_OBEC_QUERY, data)

        conn.commit()
