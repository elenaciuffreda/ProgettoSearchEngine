# main.py
import os
import zipfile
import time
import shutil
from tqdm import tqdm

# Import motori di ricerca
import postgres_engine.main_postgres as Postgres
import pylucene_engine.pylucene_IR as Pylucene
import whoosh_engine.index as WhooshIndex
import whoosh_engine.IRmodel as WhooshIR

# Import creazione dataset
from create_dataset import create as create_dataset

# Path al dataset
DATA_PATH = "Dataset"

# 1. Download/estrazione dataset

def download_dataset():
    if os.path.isdir(DATA_PATH):
        print(f"{DATA_PATH} è già presente.")
    elif os.path.exists(DATA_PATH + '.zip'):
        print("Estrazione del dataset...")
        with zipfile.ZipFile(DATA_PATH + '.zip', 'r') as zip_ref:
            files = zip_ref.namelist()
            with tqdm(total=len(files), desc="Estrazione file") as pbar:
                for f in files:
                    zip_ref.extract(f)
                    pbar.update(1)
        print("Dataset estratto con successo!")
    else:
        print("Nessun archivio trovato, avvio creazione dataset...")
        create_dataset()

# 2. Setup e indicizzazione di tutti i motori

def setup_all():
    print("--- Setup motori di ricerca ---")
    time.sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')

    print("PostgreSQL: creazione tabella e indice...")
    Postgres.main_postgres()  # setup completo
    print("PostgreSQL configurato.")
    time.sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')

    print("PyLucene: indicizzazione...")
    Pylucene.build_index()
    print("PyLucene configurato.")
    time.sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')

    print("Whoosh: indicizzazione...")
    WhooshIndex.build_index()
    print("Whoosh configurato.")
    time.sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')

    print("Setup completato!")
    time.sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')

# Funzioni di esecuzione dei motori

def run_postgres():
    print("Selezionato motore PostgreSQL")
    Postgres.main_postgres()


def run_pylucene():
    print("Selezionato motore PyLucene")
    q = input("Inserisci query: ")
    for title, score in Pylucene.search(q):
        print(f"{score:.3f}  {title}")


def run_whoosh():
    print("Selezionato motore Whoosh")
    q = input("Inserisci query: ")
    for title, score in WhooshIR.search_weighted(q):
        print(f"{score:.3f}  {title}")


def exit_program():
    print("Uscita dal programma...")
    time.sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')
    exit()

# Mappatura scelta
handlers = {
    1: run_postgres,
    2: run_pylucene,
    3: run_whoosh,
    4: exit_program
}

# Main

def main():
    os.system('cls' if os.name=='nt' else 'clear')
    print("=== Gestione dell'Informazione ===")
    download_dataset()
    setup_all()

    while True:
        print("Scegli motore di ricerca:")
        print("  1) PostgreSQL")
        print("  2) PyLucene")
        print("  3) Whoosh")
        print("  4) Esci")
        try:
            choice = int(input("> "))
            handlers.get(choice, lambda: print("Scelta non valida."))()
        except ValueError:
            print("Inserisci un numero valido.")

if __name__ == '__main__':
    main()
