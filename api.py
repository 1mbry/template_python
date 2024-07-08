from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt
from typing import Optional
from sqlite3 import Error
from io import BytesIO
import pandas as pd
import sqlite3

app = FastAPI()

# Definizione delle aree geografiche
nord_ovest = ["Valle d'Aosta", "Piemonte", "Liguria", "Lombardia"]
nord_est = ["Trentino-Alto Adige", "Veneto", "Friuli-Venezia Giulia", "Emilia-Romagna"]
centro = ["Toscana", "Umbria", "Marche", "Lazio", "Abruzzo"]
sud = ["Molise", "Campania", "Puglia", "Basilicata", "Calabria"]
isole = ["Sicilia", "Sardegna"]

# Lista delle aree
aree = [nord_ovest, nord_est, centro, sud, isole]
nomi_aree = ['Nord-Ovest', 'Nord-Est', 'Centro', 'Sud', 'Isole']


# Funzione che crea la connessione con il db
def create_connection():
    try:
        conn = sqlite3.connect('cartella_database/cartella_sqlite/pesca.db')

        return conn
    except Error as e:
        print(e)
        return None

# Get Importanza Economica
@app.get("/get_importanza_economica/")
async def get_importanza_economica(year_a: Optional[int] = None,
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

    importanza_economica = pd.read_sql_query(query, conn)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = importanza_economica[
            (importanza_economica['Anno'] >= year_a) &
            (importanza_economica['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = importanza_economica[
            (importanza_economica['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = importanza_economica[
            (importanza_economica['Anno'] <= year_b)
        ]
    else:
        filtered_data = importanza_economica
        
    # Chiudi la connessione al database
    conn.close()
    
    # Interpolazione dei dati
    filtered_data = filtered_data.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        for regione in filtered_data['Regione'].unique():
            regione_data = filtered_data[filtered_data['Regione'] == regione]
            plt.plot(regione_data['Anno'], regione_data['Percentuale_valore_aggiunto_pesca_piscicoltura_servizi'], marker='o', label=regione)
        plt.xlabel('Anno')
        plt.ylabel('Percentuale valore aggiunto pesca piscicoltura servizi')
        plt.title('Percentuale valore aggiunto pesca piscicoltura servizi per area geografica')
        plt.legend()
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    return filtered_data.to_dict(orient="records")

# Get Andamento Occupazione
@app.get("/get_andamento_occupazione/")
async def get_andamento_occupazione(year_a: Optional[int] = None,
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
    FROM andamento_occupazione
    """

    andamento_occupazione = pd.read_sql_query(query, conn)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = andamento_occupazione[
            (andamento_occupazione['Anno'] >= year_a) &
            (andamento_occupazione['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = andamento_occupazione[
            (andamento_occupazione['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = andamento_occupazione[
            (andamento_occupazione['Anno'] <= year_b)
        ]
    else:
        filtered_data = andamento_occupazione
        
    # Chiudi la connessione al database
    conn.close()
    
    # Interpolazione dei dati
    filtered_data = filtered_data.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        for regione in filtered_data['Regione'].unique():
            regione_data = filtered_data[filtered_data['Regione'] == regione]
            plt.plot(regione_data['Anno'], regione_data['Variazione_percentuale_unità_di_lavoro_della_pesca'], marker='o', label=regione)
        plt.xlabel('Anno')
        plt.ylabel('Variazione percentuale unità di lavoro della pesca')
        plt.title('Variazione percentuale unità di lavoro della pesca per regione')
        plt.legend()
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    filtered_data = filtered_data.where(pd.notnull(filtered_data), 0)
    
    return filtered_data.to_dict(orient="records")

# Get Produttivita del Settore
@app.get("/get_produttivita_del_settore/")
async def get_produttivita_del_settore(year_a: Optional[int] = None,
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
    FROM produttivita_del_settore
    """

    produttivita_del_settore = pd.read_sql_query(query, conn)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = produttivita_del_settore[
            (produttivita_del_settore['Anno'] >= year_a) &
            (produttivita_del_settore['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = produttivita_del_settore[
            (produttivita_del_settore['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = produttivita_del_settore[
            (produttivita_del_settore['Anno'] <= year_b)
        ]
    else:
        filtered_data = produttivita_del_settore
        
    # Chiudi la connessione al database
    conn.close()
    
    # Interpolazione dei dati
    filtered_data = filtered_data.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        for regione in filtered_data['Regione'].unique():
            regione_data = filtered_data[filtered_data['Regione'] == regione]
            plt.plot(regione_data['Anno'], regione_data['Produttività_in_migliaia_di_euro'], marker='o', label=regione)
        plt.xlabel('Anno')
        plt.ylabel('Produttività in migliaia di euro')
        plt.title('Produttività in migliaia di euro per regione')
        plt.legend()
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    filtered_data = filtered_data.where(pd.notnull(filtered_data), 0)
    
    return filtered_data.to_dict(orient="records")

# Get Media percentuale valore aggiunto pesca piscicoltura delle 5 Aree Nord-ovest, Nord-est, Centro, Sud, Isole
@app.get("/get_media_percentuale_valore_aggiunto_pesca_piscicoltura_delle_5_aree/")
async def get_media_percentuale_valore_aggiunto_pesca_piscicoltura_delle_5_aree(year_a: Optional[int] = None,
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
    
    # Interpolazione dei dati
    df = df.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
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
            media_percentuale = subset['Percentuale_valore_aggiunto_pesca_piscicoltura_servizi'].mean()
            
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

# Get Produttività totale in migliaia di euro delle 5 Aree Nord-ovest, Nord-est, Centro, Sud, Isole
@app.get("/get_produttivita_totale_delle_5_aree/")
async def get_produttivita_totale_delle_5_aree(year_a: Optional[int] = None,
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
    FROM produttivita_del_settore
    """

    df = pd.read_sql_query(query, conn)

    # Interpolazione dei dati
    df = df.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    # Inizializza una lista di dizionari per i risultati
    results = []
    
    for anno in df['Anno'].unique():
        # Inizializza il dizionario per salvare le medie percentuali per l'anno corrente
        produttivita_totale_anno = {'Anno': anno}
        
        # Itera per ogni area geografica
        for area, nome_area in zip(aree, nomi_aree):
            # Seleziona le righe del DataFrame corrispondenti all'anno e all'area geografica
            subset = df[(df['Anno'] == anno) & (df['Regione'].isin(area))]
            
            # Calcola la somma del valore aggiunto della pesca e piscicoltura per l'area e l'anno correnti
            produttivita_totale = subset['Produttività_in_migliaia_di_euro'].sum()
            
            # Salva la media percentuale nel dizionario
            produttivita_totale_anno[nome_area] = produttivita_totale
        
            # Crea un dizionario per il risultato corrente
            result = {
                'Anno': anno,
                'Aree': nome_area,
                'Produttività in migliaia di euro': produttivita_totale
            }
            
            # Aggiungi il dizionario alla lista dei risultati
            results.append(result)

    # Converti la lista di dizionari in un DataFrame
    produttivita_totale_delle_5_aree = pd.DataFrame(results)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = produttivita_totale_delle_5_aree[
            (produttivita_totale_delle_5_aree['Anno'] >= year_a) &
            (produttivita_totale_delle_5_aree['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = produttivita_totale_delle_5_aree[
            (produttivita_totale_delle_5_aree['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = produttivita_totale_delle_5_aree[
            (produttivita_totale_delle_5_aree['Anno'] <= year_b)
        ]
    else:
        filtered_data = produttivita_totale_delle_5_aree
        
    # Chiudi la connessione al database
    conn.close()
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        for area in nomi_aree:
            area_data = filtered_data[filtered_data['Aree'] == area]
            plt.plot(area_data['Anno'], area_data['Produttività in migliaia di euro'], marker='o', label=area)
        plt.xlabel('Anno')
        plt.ylabel('Produttività in migliaia di euro')
        plt.title('Produttività totale in migliaia di euro delle 5 Aree')
        plt.legend()
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    return filtered_data.to_dict(orient="records")

# Get Produttività totale in migliaia di euro NAZIONALE
@app.get("/get_produttivita_totale_nazionale/")
async def get_produttivita_totale_nazionale(year_a: Optional[int] = None,
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
    FROM produttivita_del_settore
    """

    df = pd.read_sql_query(query, conn)
    
    # Interpolazione dei dati
    df = df.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    # Inizializza una lista di dizionari per i risultati
    results = []
    
    for anno in df['Anno'].unique():
        # Inizializza il dizionario per salvare le medie percentuali per l'anno corrente
        produttivita_totale = df[df['Anno'] == anno]['Produttività_in_migliaia_di_euro'].sum()
        result = {
                'Anno': anno,
                'Produttività in migliaia di euro Nazionale': produttivita_totale
            }
        results.append(result)

    # Converti la lista di dizionari in un DataFrame
    produttivita_totale_nazionale = pd.DataFrame(results)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = produttivita_totale_nazionale[
            (produttivita_totale_nazionale['Anno'] >= year_a) &
            (produttivita_totale_nazionale['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = produttivita_totale_nazionale[
            (produttivita_totale_nazionale['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = produttivita_totale_nazionale[
            (produttivita_totale_nazionale['Anno'] <= year_b)
        ]
    else:
        filtered_data = produttivita_totale_nazionale
        
    # Chiudi la connessione al database
    conn.close()
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data['Anno'], filtered_data['Produttività in migliaia di euro Nazionale'], marker='o')
        plt.xlabel('Anno')
        plt.ylabel('Produttività in migliaia di euro Nazionale')
        plt.title('Produttività totale nazionale in migliaia di euro')
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    return filtered_data.to_dict(orient="records")

# Get Media Variazione percentuale occupazione NAZIONALE
@app.get("/get_media_variazione_percentuale_occupazione_nazionale/")
async def get_media_variazione_percentuale_occupazione_nazionale(year_a: Optional[int] = None,
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
    FROM andamento_occupazione
    """

    df = pd.read_sql_query(query, conn)

    # Interpolazione dei dati
    df = df.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    # Inizializza una lista di dizionari per i risultati
    results = []
    
    for anno in df['Anno'].unique():
        # Inizializza il dizionario per salvare le medie percentuali per l'anno corrente
        media_variazione = df[df['Anno'] == anno]['Variazione_percentuale_unità_di_lavoro_della_pesca'].mean()
        result = {
                'Anno': anno,
                'Media variazione percentuale unità di lavoro della pesca nazionale': media_variazione
            }
        results.append(result)

    # Converti la lista di dizionari in un DataFrame
    media_variazione_percentuale_nazionale = pd.DataFrame(results)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = media_variazione_percentuale_nazionale[
            (media_variazione_percentuale_nazionale['Anno'] >= year_a) &
            (media_variazione_percentuale_nazionale['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = media_variazione_percentuale_nazionale[
            (media_variazione_percentuale_nazionale['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = media_variazione_percentuale_nazionale[
            (media_variazione_percentuale_nazionale['Anno'] <= year_b)
        ]
    else:
        filtered_data = media_variazione_percentuale_nazionale
        
    # Chiudi la connessione al database
    conn.close()
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data['Anno'], filtered_data['Media variazione percentuale unità di lavoro della pesca nazionale'], marker='o')
        plt.xlabel('Anno')
        plt.ylabel('Media variazione percentuale unità di lavoro della pesca nazionale')
        plt.title('Media variazione percentuale unità di lavoro della pesca nazionale')
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    return filtered_data.to_dict(orient="records")

# Media Variazione percentuale occupazione delle 5 Aree Nord-ovest, Nord-est, Centro, Sud, Isole
@app.get("/get_media_variazione_percentuale_occupazione_nazionale_delle_5_aree/")
async def get_media_variazione_percentuale_occupazione_nazionale_delle_5_aree(year_a: Optional[int] = None,
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
    FROM andamento_occupazione
    """

    df = pd.read_sql_query(query, conn)

    # Interpolazione dei dati
    df = df.groupby('Regione').apply(lambda group: group.set_index('Anno').interpolate(method='linear').reset_index())
    
    # Inizializza una lista di dizionari per i risultati
    results = []
    
    for anno in df['Anno'].unique():
        # Inizializza il dizionario per salvare le medie percentuali per l'anno corrente
        media_variazione_anno = {'Anno': anno}
        
        # Itera per ogni area geografica
        for area, nome_area in zip(aree, nomi_aree):
            # Seleziona le righe del DataFrame corrispondenti all'anno e all'area geografica
            subset = df[(df['Anno'] == anno) & (df['Regione'].isin(area))]
            
            # Calcola la somma del valore aggiunto della pesca e piscicoltura per l'area e l'anno correnti
            media_variazione = subset['Variazione_percentuale_unità_di_lavoro_della_pesca'].mean()
            
            # Salva la media percentuale nel dizionario
            media_variazione_anno[nome_area] = media_variazione
        
            # Crea un dizionario per il risultato corrente
            result = {
                'Anno': anno,
                'Aree': nome_area,
                'Media variazione percentuale unità di lavoro della pesca': media_variazione
            }
            
            # Aggiungi il dizionario alla lista dei risultati
            results.append(result)

    # Converti la lista di dizionari in un DataFrame
    media_variazione_delle_5_aree = pd.DataFrame(results)
    
    # Filtra i dati in base ai parametri year_a e year_b
    if year_a is not None and year_b is not None:
        filtered_data = media_variazione_delle_5_aree[
            (media_variazione_delle_5_aree['Anno'] >= year_a) &
            (media_variazione_delle_5_aree['Anno'] <= year_b)
        ]
    elif year_a is not None and year_b is None:
        filtered_data = media_variazione_delle_5_aree[
            (media_variazione_delle_5_aree['Anno'] >= year_a)
        ]
    elif year_a is None and year_b is not None:
        filtered_data = media_variazione_delle_5_aree[
            (media_variazione_delle_5_aree['Anno'] <= year_b)
        ]
    else:
        filtered_data = media_variazione_delle_5_aree
        
    # Chiudi la connessione al database
    conn.close()
    
    if plot_graph:
        plt.figure(figsize=(10, 6))
        for area in nomi_aree:
            area_data = filtered_data[filtered_data['Aree'] == area]
            plt.plot(area_data['Anno'], area_data['Media variazione percentuale unità di lavoro della pesca'], marker='o', label=area)
        plt.xlabel('Anno')
        plt.ylabel('Media variazione percentuale unità di lavoro della pesca')
        plt.title('Media variazione percentuale unità di lavoro della pesca delle 5 Aree')
        plt.legend()
        plt.grid(True)

        # Salva il grafico in un buffer BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Ritorna il grafico come risposta HTTP
        return Response(content=buffer.getvalue(), media_type='image/png')
    
    return filtered_data.to_dict(orient="records")