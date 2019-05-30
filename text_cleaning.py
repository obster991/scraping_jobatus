from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
import nltk
import gensim
import pickle
from collections import Counter

tokenizer = RegexpTokenizer(r'\w+')
nltk.data.path.append("data")


# Aggiungo nuove stop_word a quelle già presenti nella libreria nltk
def stop_word(other_stop=None):
    word = stopwords.words('italian')
    word = word + stopwords.words('english')
    word += ['il', 'di', 'e', 'a', 'un', 'in', 'che', 'non', 'si', 'da', 'lo', 'per', 'con', 'ma', 'come', 'su', 'mi',
             'anche', 'o',
             'io', 'se', 'perché', 'li', 'ci', 'ne', 'lei', 'ancora', 'tu', 'lui', 'senza', 'bene', 'cui', 'chi', 'già',
             'dopo',
             'uno', 'noi', 'dove', 'qui', 'no', 'allora', 'tra', 'vi', 'ora', 'fra', 'prima', 'forse', 'sì', 'sotto',
             'voi',
             'fino', 'oggi', 'quasi', 'pure', 'egli', 'mentre', 'contro', 'invece', 'esso', 'là', 'però', 'né',
             'subito', 'verso',
             'ciò', 'ecco', 'loro', 'essa', 'fuori', 'meno', 'adesso', 'niente', 'cioè', 'male', 'nulla', 'ah', 'oh',
             'quindi', 'appena',
             'insieme', 'dunque', 'dentro', 'durante', 'almeno', 'secondo', 'anzi', 'oramai', 'oltre', 'intorno',
             'sopra', 'dietro',
             'davanti', 'soltanto', 'infatti', 'qualcosa', 'spesso', 'accordo', 'ieri', 'davvero', 'lì', 'qualcuno',
             'avanti', 'assai',
             'presto', 'qua', 'domani', 'circa', 'giù', 'soprattutto', 'nemmeno', 'grazie', 'tuttavia', 'appunto',
             'neppure', 'eh',
             'veramente', 'tardi', 'insomma', 'presso', 'intanto', 'lungo', 'neanche', 'piuttosto', 'stasera', 'perciò',
             'naturalmente',
             'accanto', 'eppure', 'eccetera', 'finalmente', 'infine', 'poiché', 'comunque', 'dinanzi', 'abbastanza',
             'peccato',
             'certamente', 'coloro', 'attorno', 'magari', 'oppure', 'inoltre', 'indietro', 'addosso', 'addirittura',
             'finché', 'perfino',
             'affatto', 'stamattina', 'completamente', 'probabilmente', 'chissà', 'sino', 'ognuno', 'entro', 'così',
             'quindi', 'far',
             'aver', 'fare', 'avere', 'essere', 'come', 'gennaio', 'febbraio', 'marzo', 'aprle', 'maggio', 'giugno',
             'luglio', 'agosto',
             'settembre', 'ottobre', 'novembre', 'dicembre', 'umomo', 'donna', 'italia', 'cosa', 'anno', 'volta',
             'italia', 'italiano',
             'italiana', 'uno', 'due', 'tre', 'quattro', 'cinque', 'sei', 'sette', 'otto', 'nove', 'dieci', 'solo',
             'dopo',
             'quale', 'quali', 'questo', 'quello', 'quelli', 'quelle', 'con', 'anni', 'può', 'poi', 'mai', 'quando',
             'dove',
             'molto', 'stata', 'sempre', 'nuovo', 'nuova', 'mila', 'via', 'stai', 'fatto', 'far', 'fare', 'fanno',
             'dice', 'dire',
             'detto', 'stati', 'stato', 'persone', 'parte', 'proprio', 'ogni', 'primo', 'secondo', 'minuto', 'vita',
             'alcuni', 'ore', 'altri', 'quel', 'poco', 'italiano', 'modo', 'potrebbe', 'altra', 'tutta', 'tutto',
             'tutte', 'mesi', 'posto', 'deve', 'devono', 'dover', 'dato', 'dati', 'visto', 'visti', 'casa', 'grandi',
             'state', 'italiani', 'ultimo', 'qualche', 'continua', 'news']
    if not other_stop is None:
        word += other_stop
    return list(set(word))


# Funzione che riceve un testo e lo resituisce senza le stop_word, eliminando le parole di lunghezza minore di 2
#  e caratteri non letterali
def delete_word(text, other_stop=None):
    text = re.sub('[^a-zA-Zàèìòùé]', ' ', text)
    text = text.lower()
    stop = stop_word(other_stop=other_stop)
    token = tokenizer.tokenize(text)
    token = [x for x in token if x not in stop and len(x) > 2]
    text = ' '.join(token)

    return text


# Funzione che unisce le parole che si presentano spesso in coppia (es. new york)
def bigram_text(titles):
    # il token è la singola parola
    token = [tokenizer.tokenize(x) for x in titles]
    bigram = gensim.models.Phrases(token, min_count=10, threshold=20)
    trigram = gensim.models.Phrases(bigram[token], min_count=10, threshold=20)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    token = [trigram_mod[x] for x in token]
    titles = [' '.join(x) for x in token]
    pickle.dump(trigram_mod, open("C:\\Users\\andre\\PycharmProjects\\prove\\Training Testing - Bucket - Classificazione Bayesiana\\news_category\model.pickle", 'wb'))
    return titles
