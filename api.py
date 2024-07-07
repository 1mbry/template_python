from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt
from typing import Optional
from sqlite3 import Error
from io import BytesIO
import pandas as pd
import sqlite3

app = FastAPI()

# Funzione che crea la connessione con il db
def create_connection():
    try:
        conn = sqlite3.connect('cartella_database/cartella_sqlite/pesca.db')

        return conn
    except Error as e:
        print(e)
        return None

@app.get("/get_media_percentuale_valore_aggiunto_pesca_piscicoltura/")
async def get_media_percentuale_valore_aggiunto_pesca_piscicoltura(year_a: Optional[int] = None,
                                                                   year_b: Optional[int] = None,
                                                                   plot_graph: Optional[bool] = False):
    # Controllo sugli anni
    if year_a is not None and year_b is not None:
        if year_a >= year_b:
            raise HTTPException(status_code=400, detail="Anno A deve essere più piccolo di Anno B")
        
    # Query da utilizzare
    conn = create_connection()
    query = """
    SELECT *
    FROM importanza_economica
    """

    df = pd.read_sql_query(query, conn)


    # Definizione delle aree geografiche
    nord_ovest = ["Valle d'Aosta", "Piemonte", "Liguria", "Lombardia"]
    nord_est = ["Trentino-Alto Adige", "Veneto", "Friuli-Venezia Giulia", "Emilia-Romagna"]
    centro = ["Toscana", "Umbria", "Marche", "Lazio", "Abruzzo"]
    sud = ["Molise", "Campania", "Puglia", "Basilicata", "Calabria"]
    isole = ["Sicilia", "Sardegna"]

    # Lista delle aree
    aree = [nord_ovest, nord_est, centro, sud, isole]
    nomi_aree = ['Nord-Ovest', 'Nord-Est', 'Centro', 'Sud', 'Isole']


    # Inizializza una lista di dizionari per i risultati
    results = []
    for anno in df['Anno'].unique():
        # Inizializza il dizionario per salvare le medie percentuali per l'anno corrente
        medie_percentuali_anno = {'Anno': anno}
        
        # Itera per ogni area geografica
        for area, nome_area in zip(aree, nomi_aree):
            # Seleziona le righe del DataFrame corrispondenti all'anno e all'area geografica
            subset = df[(df['Anno'] == anno) & (df['Regione'].isin(area))]
            
            # Calcola la media percentuale del valore aggiunto della pesca e piscicoltura per l'area e l'anno correnti
            media_percentuale = subset['Percentuale_valore_aggiunto_pesca-piscicoltura-servizi'].mean()
            
            # Salva la media percentuale nel dizionario
            medie_percentuali_anno[nome_area] = media_percentuale
        
            # Crea un dizionario per il risultato corrente
            result = {
                'Anno': anno,
                'Aree': nome_area,
                'Media percentuale valore aggiunto pesca piscicoltura': media_percentuale
            }
            
            # Aggiungi il dizionario alla lista dei risultati
            results.append(result)

    # Converti la lista di dizionari in un DataFrame
    media_percentuale_valore_aggiunto_pesca_piscicoltura = pd.DataFrame(results)

    # Visualizza il DataFrame dei risultati finali
    #display(media_percentuale_valore_aggiunto_pesca_piscicoltura)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = media_percentuale_valore_aggiunto_pesca_piscicoltura[
            (media_percentuale_valore_aggiunto_pesca_piscicoltura['Anno'] >= year_a) &
            (media_percentuale_valore_aggiunto_pesca_piscicoltura['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = media_percentuale_valore_aggiunto_pesca_piscicoltura[
            (media_percentuale_valore_aggiunto_pesca_piscicoltura['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = media_percentuale_valore_aggiunto_pesca_piscicoltura[
            (media_percentuale_valore_aggiunto_pesca_piscicoltura['Anno'] <= year_b)
        ]
    else:
        filtered_data = media_percentuale_valore_aggiunto_pesca_piscicoltura
        
    # Chiudi la connessione al database
    conn.close()
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        for area in nomi_aree:
            area_data = filtered_data[filtered_data['Aree'] == area]
            plt.plot(area_data['Anno'], area_data['Media percentuale valore aggiunto pesca piscicoltura'], marker='o', label=area)
        plt.xlabel('Anno')
        plt.ylabel('Media percentuale valore aggiunto pesca piscicoltura')
        plt.title('Media percentuale valore aggiunto pesca piscicoltura per area geografica')
        plt.legend()
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')

    
    return filtered_data.to_dict(orient="records")