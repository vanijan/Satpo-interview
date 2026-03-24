
DROP_OKRES_OBEC_QUERY = """DROP TABLE IF EXISTS okres_obec"""
DROP_ADRESY_KATASTRALNICH_URADU_QUERY = """DROP TABLE IF EXISTS adresy_katastralnich_uradu"""
DROP_CINZOVNI_DOMY_QUERY = """DROP TABLE IF EXISTS cinzovni_domy"""

CREATE_TABLE_ADRESY_QUERY = """
CREATE TABLE adresy_katastralnich_uradu (
                KOD_PRACOVISTE INT PRIMARY KEY,
                NAZEV VARCHAR(255),
                ADRESA VARCHAR(255),
                TELEFON VARCHAR(255)
            );
            """

CREATE_TABLE_OKRES_OBEC_QUERY = """
            CREATE TABLE okres_obec (
                ID INT PRIMARY KEY,
                OKRES_OBEC VARCHAR(255),
                KOD_PRACOVISTE INT,
                KRAJ_NAZEV VARCHAR(255),
                FOREIGN KEY (KOD_PRACOVISTE)
                    REFERENCES adresy_katastralnich_uradu(KOD_PRACOVISTE)
            );
            """

INSERT_DATA_QUERY_ADRESY_QUERY = """
                INSERT INTO adresy_katastralnich_uradu (KOD_PRACOVISTE, NAZEV, ADRESA, TELEFON)
                VALUES (%s, %s, %s, %s); """

INSERT_DATA_OKRES_OBEC_QUERY = """
                INSERT INTO okres_obec (ID, OKRES_OBEC, KOD_PRACOVISTE, KRAJ_NAZEV)
                VALUES (%s, %s, %s, %s); """

CREATE_TABLE_CINZOVNI_DOMY_QUERY = """
            CREATE TABLE cinzovni_domy (
                ID INT PRIMARY KEY,
                ID_SUBJEKTU BIGINT,
                VYUZITI VARCHAR(255),
                OKRES_OBEC_ID INT,
                ULICE_CP VARCHAR(255),
                MESTO VARCHAR(255),
                PSC VARCHAR(255),
                VYMEZENE_BYTY BOOLEAN,
                VLASTNICTVI VARCHAR(255),
                TYP_BUDOVY VARCHAR(255),
                LONGITUDE FLOAT,
                LATITUDE FLOAT,
                FOREIGN KEY (OKRES_OBEC_ID)
                    REFERENCES okres_obec(ID)
            );
            """

INSERT_DATA_CINZOVNI_DOMY_QUERY = """
                INSERT INTO cinzovni_domy (
                ID, ID_SUBJEKTU, VYUZITI, OKRES_OBEC_ID, ULICE_CP,
                MESTO, PSC, VYMEZENE_BYTY, VLASTNICTVI,
                TYP_BUDOVY, LONGITUDE, LATITUDE
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                ID_SUBJEKTU = VALUES(ID_SUBJEKTU),
                VYUZITI = VALUES(VYUZITI),
                OKRES_OBEC_ID = VALUES(OKRES_OBEC_ID),
                ULICE_CP = VALUES(ULICE_CP),
                MESTO = VALUES(MESTO),
                PSC = VALUES(PSC),
                VYMEZENE_BYTY = VALUES(VYMEZENE_BYTY),
                VLASTNICTVI = VALUES(VLASTNICTVI),
                TYP_BUDOVY = VALUES(TYP_BUDOVY),
                LONGITUDE = VALUES(LONGITUDE),
                LATITUDE = VALUES(LATITUDE);
                """

SELECT_ALL_OKRES_OBEC_ID_QUERY = """SELECT ID, OKRES_OBEC FROM okres_obec"""