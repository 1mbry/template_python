import pandas as pd
import sqlite3
import requests
from io import StringIO

url_importanza_economica_csv = 'http://www.datiopen.it/export/csv/Importanza-economica-del-settore-della-pesca-per-regione.csv'
url_andamento_occupazione_csv = 'http://www.datiopen.it/export/csv/Andamento-occupazione-del-settore-della-pesca-per-regione.csv'
url_produttivita_del_settore_csv = 'http://www.datiopen.it/export/csv/Produttivita-del-settore-della-pesca-per-regione.csv'

try:
    response_importanza_economica_csv = requests.get(url_importanza_economica_csv)
    response_andamento_occupazione_csv = requests.get(url_andamento_occupazione_csv)
    response_produttivita_del_settore_csv = requests.get(url_produttivita_del_settore_csv)
    
    response_importanza_economica_csv.raise_for_status()
    response_andamento_occupazione_csv.raise_for_status()
    response_produttivita_del_settore_csv.raise_for_status()
    
    importanza_economica = pd.read_csv(StringIO(response_importanza_economica_csv.text), sep=';')
    andamento_occupazione = pd.read_csv(StringIO(response_andamento_occupazione_csv.text), sep=';')
    produttivita_del_settore = pd.read_csv(StringIO(response_produttivita_del_settore_csv.text), sep=';')
    
    importanza_economica.columns = importanza_economica.columns.str.replace(' ', '_')
    importanza_economica.columns = importanza_economica.columns.str.replace('-', '_')
    
    andamento_occupazione.columns = andamento_occupazione.columns.str.replace(' ', '_')
    
    produttivita_del_settore.columns = produttivita_del_settore.columns.str.replace(' ', '_')
    
    db_path = 'cartella_database/cartella_sqlite/pesca.db'
    
    conn = sqlite3.connect(db_path)
    importanza_economica.to_sql('importanza_economica', conn, index=False, if_exists='replace')
    andamento_occupazione.to_sql('andamento_occupazione', conn, index=False, if_exists='replace')
    produttivita_del_settore.to_sql('produttivita_del_settore', conn, index=False, if_exists='replace')
    conn.close()
    
except requests.exceptions.HTTPError as http_error:
    print(f"Errore HTTP: {http_error}")
except Exception as error:
    print(f"Errore imprevisto: {error}")