# main.py
import os
import zipfile
import time
from tqdm import tqdm


from postgres_engine.main_postgres import main_postgres as run_postgres_setup
import whoosh_engine.index as WhooshIndex
import whoosh_engine.IRmodel as WhooshIR
from create_dataset import create as create_dataset


DATA_PATH = "data"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# download/estrazione dataset

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


# setup e indicizzazione di tutti i motori

def setup_all():
    print("--- Setup motori di ricerca ---")
    time.sleep(1)
    clear_screen()

    print("PostgreSQL: creazione tabella e indice...")
    run_postgres_setup()  # setup completo
    print("PostgreSQL configurato.")
    time.sleep(1)
    clear_screen()

    print("Whoosh: indicizzazione...")
    WhooshIndex.build_index()
    print("Whoosh configurato.")
    time.sleep(1)
    clear_screen()

    print("Setup completato!")
    time.sleep(1)
    clear_screen()


# esecuzione dei motori

def run_postgres():
    print("Selezionato motore PostgreSQL")
    run_postgres_setup()


def run_whoosh():
    print("Selezionato motore Whoosh")
    q = input("Inserisci query: ")
    for title, score in WhooshIR.search_weighted(q):
        print(f"{score:.3f}  {title}")


def exit_program():
    print("Uscita dal programma...")
    time.sleep(1)
    clear_screen()
    exit()


# Mappatura scelta
handlers = {
    1: run_postgres,
    2: run_whoosh,
    3: exit_program
}


# Main

def main():
    clear_screen()
    print("=== Gestione dell'Informazione ===")
    download_dataset()
    setup_all()

    while True:
        print("Scegli motore di ricerca:")
        print("  1) PostgreSQL")
        print("  2) Whoosh")
        print("  3) Esci")
        try:
            choice = int(input("> "))
            handlers.get(choice, lambda: print("Scelta non valida."))()
        except ValueError:
            print("Inserisci un numero valido.")


if __name__ == '__main__':
    main()