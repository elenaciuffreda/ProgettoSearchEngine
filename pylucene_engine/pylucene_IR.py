
import os
import json
import shutil
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.it import ItalianAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanQuery
from org.apache.lucene.search.similarities import BM25Similarity, ClassicSimilarity
from org.apache.lucene.search.spell import SpellChecker, LuceneDictionary
from org.apache.lucene.queryparser.classic import QueryParser
from tqdm import tqdm

# Inizializza la JVM per PyLucene

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Percorsi dataset e indici
BASE_DIR     = os.path.dirname(__file__)
DATASET_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'data', 'wiki_med_150.jsonl'))
INDEX_DIR    = os.path.join(BASE_DIR, 'lucene_index')
MAIN_IDX     = os.path.join(INDEX_DIR, 'main')
SPELL_IDX    = os.path.join(INDEX_DIR, 'spell')

class PyLuceneIR:
    @staticmethod
    def prepare_dirs():
        if os.path.exists(INDEX_DIR):
            shutil.rmtree(INDEX_DIR)
        os.makedirs(MAIN_IDX, exist_ok=True)
        os.makedirs(SPELL_IDX, exist_ok=True)

    @staticmethod
    def create_index():
        if os.path.exists(MAIN_IDX) and os.listdir(MAIN_IDX):
            print("Indice già presente, skipping indicizzazione.")
            return
        PyLuceneIR.prepare_dirs()

        main_dir = FSDirectory.open(Paths.get(MAIN_IDX))
        analyzer = ItalianAnalyzer()
        config = IndexWriterConfig(analyzer)
        writer = IndexWriter(main_dir, config)

        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="Indicizzazione PyLucene"):
                data = json.loads(line)
                doc = Document()
                doc.add(TextField('title', data.get('title', ''), Field.Store.YES))
                doc.add(TextField('content', data.get('text', ''), Field.Store.YES))
                writer.addDocument(doc)
        writer.commit()
        writer.close()

        # Spellchecker
        spell_dir = FSDirectory.open(Paths.get(SPELL_IDX))
        spell_checker = SpellChecker(spell_dir)
        reader = DirectoryReader.open(main_dir)
        spell_checker.indexDictionary(LuceneDictionary(reader, 'title'), config, True)
        reader.close()
        spell_checker.close()

        print('✅ PyLucene: indicizzazione completata.')

    @staticmethod
    def check_spelling(query):
        spell_dir = FSDirectory.open(Paths.get(SPELL_IDX))
        spell_checker = SpellChecker(spell_dir)
        corrected = []
        for token in query.split():
            sug = spell_checker.suggestSimilar(token, 1)
            corrected.append(sug[0] if sug else token)
        spell_checker.close()
        return ' '.join(corrected)

    @staticmethod
    def build_query(query_str):
        analyzer = ItalianAnalyzer()
        parser = QueryParser('content', analyzer)
        return parser.parse(query_str)

    @staticmethod
    def search_index(query_str, top_k=10, ranking='bm25'):
        main_dir = FSDirectory.open(Paths.get(MAIN_IDX))
        reader = DirectoryReader.open(main_dir)
        searcher = IndexSearcher(reader)
        if ranking == 'tfidf':
            searcher.setSimilarity(ClassicSimilarity())
        else:
            searcher.setSimilarity(BM25Similarity())

        query = PyLuceneIR.build_query(query_str)
        hits = searcher.search(query, top_k).scoreDocs
        results = [(searcher.doc(h.doc).get('title'), h.score) for h in hits]
        reader.close()
        return results

    @staticmethod
    def main_pylucene():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(' 🖥️    PyLucene IR - Dataset medico')
        print('1) Indicizza')
        print('2) Cerca')
        choice = input('Scelta: ').strip()
        if choice == '1':
            PyLuceneIR.create_index()
        elif choice == '2':
            q = input('Query: ')
            q_corr = PyLuceneIR.check_spelling(q)
            print(f"Query corretta: {q_corr}")
            m = input('Ranking - 1 BM25, 2 TF-IDF: ').strip()
            ranking = 'tfidf' if m == '2' else 'bm25'
            for title, score in PyLuceneIR.search_index(q_corr, ranking=ranking):
                print(f"{score:.3f}  {title}")
        else:
            print('Uscita.')

if __name__ == '__main__':
    PyLuceneIR.main_pylucene()
