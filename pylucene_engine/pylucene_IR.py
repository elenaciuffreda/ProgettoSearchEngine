import os
import sys
import json
import shutil
import lucene # type: ignore
from java.nio.file import Paths # type: ignore
from org.apache.lucene.analysis.it import ItalianAnalyzer # type: ignore
from org.apache.lucene.document import Document, Field, TextField # type: ignore
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader # type: ignore
from org.apache.lucene.store import FSDirectory # type: ignore
from org.apache.lucene.search import IndexSearcher, BooleanQuery # type: ignore
from org.apache.lucene.search.similarities import BM25Similarity, ClassicSimilarity # type: ignore
from org.apache.lucene.search.spell import SpellChecker, LuceneDictionary # type: ignore
from org.apache.lucene.queryparser.classic import QueryParser # type: ignore
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser # type: ignore



# inizializzo  la JVM per PyLucene
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# percorsi dataset i
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
            print("Indice già presente, procedere con la ricerca.")
            return
        PyLuceneIR.prepare_dirs()

        # 1) creo indice principale
        main_dir = FSDirectory.open(Paths.get(MAIN_IDX))
        analyzer = ItalianAnalyzer()
        config   = IndexWriterConfig(analyzer)
        writer   = IndexWriter(main_dir, config)

        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="Indicizzazione PyLucene"):
                data = json.loads(line)
                doc = Document()
                doc.add(TextField('title', data.get('title', ''), Field.Store.YES))
                doc.add(TextField('content', data.get('text', ''), Field.Store.YES))
                writer.addDocument(doc)
        writer.commit()
        writer.close()

        # 2) Spellchecker: uso una nuova config e un nuovo writer
        spell_dir = FSDirectory.open(Paths.get(SPELL_IDX))
        # NON riutilizzare 'config' di sopra, ma crearne uno nuovo:
        spell_analyzer = ItalianAnalyzer()
        spell_config   = IndexWriterConfig(spell_analyzer)
        spell_checker  = SpellChecker(spell_dir)

        # uso un reader sul main index
        reader = DirectoryReader.open(main_dir)
        # IndexDictionary richiede solo il reader e il nome del campo
        spell_checker.indexDictionary(LuceneDictionary(reader, 'title'),
                                      spell_config,
                                      True)
        reader.close()
        spell_checker.close()

        print(' PyLucene: indicizzazione completata.')

    
    @staticmethod
    def check_spelling(query):
        """
        propone correzioni ortografiche, ma NON applica lo stemming.
        """
        spell_dir = FSDirectory.open(Paths.get(SPELL_IDX))
        spell_checker = SpellChecker(spell_dir)
        corrected = []
        for token in query.split():
            # suggerisci correzioni sul token "raw"
            sugg = spell_checker.suggestSimilar(token, 1)
            corrected.append(sugg[0] if sugg else token)
        spell_checker.close()
        return ' '.join(corrected)


    @staticmethod
    def build_query(query_str):
        analyzer = ItalianAnalyzer()
        parser = QueryParser('content', analyzer)
        parser.setDefaultOperator(QueryParser.Operator.AND)
        return parser.parse(query_str)
    
    @staticmethod
    def search_index(query_str, top_k=10, ranking='bm25'):
        """
        Esegue una query sul main index: 
        - se AND restituisce risultati, li usa;
        - altrimenti fa fallback su OR.
        """
        main_dir = FSDirectory.open(Paths.get(MAIN_IDX))
        reader   = DirectoryReader.open(main_dir)
        searcher = IndexSearcher(reader)

        # ranking
        if ranking == 'tfidf':
            searcher.setSimilarity(ClassicSimilarity())
        else:
            searcher.setSimilarity(BM25Similarity())

        # 1) query AND
        parser = QueryParser('content', ItalianAnalyzer())
        parser.setDefaultOperator(QueryParser.Operator.AND)
        lucene_and = parser.parse(query_str)
        hits = searcher.search(lucene_and, top_k).scoreDocs

        # 2) se AND non porta nulla, riprova con OR
        if not hits:
            print("⚠️ No hit con AND, ripiego su OR")
            parser.setDefaultOperator(QueryParser.Operator.OR)
            lucene_or = parser.parse(query_str)
            hits = searcher.search(lucene_or, top_k).scoreDocs

        # estrazione dei documenti
        stored = searcher.storedFields()
        results = []
        seen = set()
        for hit in hits:
            title = stored.document(hit.doc).get('title')
            if title in seen: 
                continue
            seen.add(title)
            results.append((title, hit.score))

        reader.close()
        return results

    @staticmethod
    def main_pylucene():
        os.system('cls' if os.name == 'nt' else 'clear')
        print('     PyLucene IR - Dataset medico')
        print('1) Indicizza')
        print('2) Cerca')
        choice = input('Scelta: ').strip()
        if choice == '1':
            PyLuceneIR.create_index()
        elif choice == '2':
            q = input('Query: ').strip()
            m = input('Ranking - 1 BM25, 2 TF-IDF: ').strip()
            ranking = 'tfidf' if m == '2' else 'bm25'

            # Debug: mostra la query parsata e il numero di hit
            parsed = PyLuceneIR.build_query(q)
            # print(f"DEBUG: parsed query = {parsed}")
            hits = PyLuceneIR.search_index(q, ranking=ranking)
            # print(f"DEBUG: numero di hit = {len(hits)}")

            for title, score in hits:
                print(f"{score:.3f}  {title}")
        else:
            print('Uscita.')


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '1':
        PyLuceneIR.create_index()
    elif len(sys.argv) >= 4 and sys.argv[1] == '2':
        q       = sys.argv[2]
        ranking = 'tfidf' if sys.argv[3] == '2' else 'bm25'
        q_corr  = PyLuceneIR.check_spelling(q)
        results = PyLuceneIR.search_index(q_corr, ranking=ranking)
        for title, score in results:
            print(f"{score:.3f}  {title}")
    else:
        print("Uso: pylucene_IR.py 1            # indicizza")
        print("     pylucene_IR.py 2 <query> <1|2>  # cerca con BM25=1 o TF-IDF=2")
