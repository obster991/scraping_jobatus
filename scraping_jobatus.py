import requests as req
import pandas as pd
from bs4 import BeautifulSoup
import re
import os
import logging

# creazione file logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.captureWarnings(False)
logging.basicConfig(format='%(asctime)s ~ %(process)d ~ %(name)s ~ %(levelname)s ~ %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='./file.log',
                    filemode='a')
f_handler = logging.FileHandler('file.log')
f_handler.setLevel(logging.INFO)

# sito web da cui si parte
url_di_base = 'https://www.jobatus.it/ricerca-cv'


# FUNZIONE CHE PERMETTE DI SCARICARE IL CONTENUTO DI UNA PAGINA
def getPage(link):
    data = ""
    try:
        data = req.get(link).content
    except Exception as e:
        logger.exception("\n\nfailed to download \n\n")

    return data


# SOTTOFUNZIONE UTILIZZATA PER EVITARE DI RIPETERE CODICE ALL'INTERNO DELLA FUNZIONE getLinkCurriculumAtPage
def getLinkCurriculum(soup):
    # trovo gli href che hanno la parte singolare di link delle pagine dei curriculum
    a_link = soup.findAll("a", {"class": "ver_empleo"}, href=True)

    # li metto in un array con un for
    href_persone = []
    for tag in a_link:
        href_persone.append(tag.get('href'))

    # creo un altro array per i link completi ai curriculum e lo riempio con il for
    link_curriculum = []
    for i in range(0, len(href_persone)):
        link_curriculum.append('https://www.jobatus.it' + href_persone[i])

    # ritorno l'array con i link dei curriculum
    return link_curriculum


# FUNZIONE CHE SCARICA IL CURRICULUM
def getLinkCurriculumAtPage(parola_chiave, luogo, page):
    # url di partenza a cui concatenerò il numero della pagina
    url_di_partenza = 'https://www.jobatus.it/cv?q=' + parola_chiave + '&l=' + luogo + "&page=" + str(page)

    print("Url pagine di partenza: " + url_di_partenza)
    # scarico il contenuto della pagina e lo metto in una variabile
    web_site_content = getPage(url_di_partenza)
    # parso il contenuto per renderlo un testo
    soup = BeautifulSoup(web_site_content, 'html.parser')

    # controllo se la parola chiave inserita è valida vedendo se una determinata immagine compare nella pagina
    if ('<img src="/static/image/jabali_cv_it_it.jpg" alt="Cerca un curriculum" class="javat">' in str(
            web_site_content)):
        return print('Parola chiave inserita non valida o luogo inserito non esistente')

    return getLinkCurriculum(soup)


# FUNZIONE CHE PRELEVA TUTTO IL TESTO DEL CURRICULUM
def getAllCurriculumText(n_pag, parola_chiave, luogo):
    url_di_partenza = 'https://www.jobatus.it/cv?q=' + parola_chiave + '&l=' + luogo
    # svuota il dataframe_cv
    global headers
    headers = ["url", "Esperienza", "Istruzione e formazione", "Lingue", "Informazioni addizionali"]
    dataframe_cv = pd.DataFrame(columns=headers, index=None)

    logger.info("Url di partenza: " + url_di_partenza)
    # scarico il contenuto della pagina e lo metto in una variabile
    web_site_content = getPage(url_di_partenza)
    # parso il contenuto per renderlo un testo
    soup = BeautifulSoup(web_site_content, 'html.parser')

    # prendo il numero di curriculum che mi serve per trovare il numero di pagine massimo per la parola chiave cercata
    tot_curriculum = soup.find_all("div", attrs={"class": "related_top col-xs-12 col-md-12"})
    tot_curriculum = str(tot_curriculum[0].text)
    tot_curriculum = re.findall('\d+', tot_curriculum)
    tot_curriculum = int(tot_curriculum[0])
    tot_pages = int(tot_curriculum / 20) + 1

    if n_pag < 1 or n_pag > tot_pages:
        logger.info("Il numero da inserire deve essere compreso tra 2 e " + str(tot_pages) + ". Se si inserisce " + str(
            tot_pages) + " verranno scaricati tutti i " + str(tot_curriculum) + " curriculum disponibili.")
        return dataframe_cv

    # In all curriculum metto tutti i curriculum presenti nelle varie liste
    # che mi vengono ritornate da getLinkCurriculumAtPage()
    all_curriculum = []
    for u in range(1, n_pag + 1):
        lista_cv = getLinkCurriculumAtPage(parola_chiave, luogo, u)

        for link_cv in lista_cv:
            all_curriculum.append(link_cv)

    logger.info("CV Trovati: " + str(tot_curriculum))

    for curr in all_curriculum:
        print("Url che sto scaricando: " + curr)
        # url del curriculum che scorre per le varie posizioni dell'array
        url_di_partenza = curr
        web_site_content = getPage(url_di_partenza)
        soup_4 = BeautifulSoup(web_site_content, 'html.parser')
        # prendo tutto il testo e lo stampo con il for (div è il contenitore che ha la classe block
        # che è quella che contiene le varie sezioni con i testi
        sezioni = soup_4.find_all("div", attrs={"class": "detail_block col-xs-12 col-md-12"})

        # settaggio varabili
        esperienza = ""

        istruzione = ""

        lingue = ""

        info_aggiuntive = ""

        # in sezione ci sono le singole card. In card ci va una card per volta
        for card in sezioni:

            # va a creare una lista con i figli delle card ma non con i figli dei figli
            hitChild = card.findChildren(recursive=False)

            title = hitChild[0].text
            informazioni = ""
            del hitChild[0]

            for hit in hitChild:
                informazioni += hit.text

            if title == "Lingue":
                lingue = informazioni
            elif title == "Informazioni addizionali":
                info_aggiuntive = informazioni
            elif title == "Istruzione e Formazione":
                istruzione = informazioni
            elif title == "Esperienza":
                esperienza = informazioni

        # riempie i campi vuoti con "n/a"
        if lingue == "":
            lingue = "n/a"
        if info_aggiuntive == "":
            info_aggiuntive = "n/a"
        if esperienza == "":
            esperienza = "n/a"
        if istruzione == "":
            istruzione = "n/a"

        # pulisce le sezioni dagli spazi inutili
        lingue = re.sub(r'(\s+|\n)', ' ', lingue)
        istruzione = re.sub(r'(\s+|\n)', ' ', istruzione)
        esperienza = re.sub(r'(\s+|\n)', ' ', esperienza)
        info_aggiuntive = re.sub(r'(\s+|\n)', ' ', info_aggiuntive)

        try:
            # dato che ci troviamo all'interno di una funzione
            # bisogna specificare che dataframe_cv è la variabile globale
            dataframe_cv = dataframe_cv.append(
                {
                    "url": curr,
                    "Esperienza": esperienza,
                    "Istruzione e formazione": istruzione,
                    "Lingue": lingue,
                    "Informazioni addizionali": info_aggiuntive
                },
                ignore_index=True)
        except Exception as e:
            logger.exception(e)

    return dataframe_cv


# MAIN
def __main__():
    logger.info("Start scraping test")
    dataframe_cv = getAllCurriculumText(2, 'project', '')
    try:
        if not os.path.isfile('scraping_jobatus.csv'):
            dataframe_cv.to_csv('scraping_jobatus.csv', header=headers, sep=";", index=False, encoding="utf-8-sig")
        else:
            dataframe_cv.to_csv('scraping_jobatus.csv', mode="a", header=False, sep=";", index=False,
                                encoding="utf-8-sig")

    except Exception as e:
        logger.exception("Errore scrittura su csv")

    logger.info("Programma terminato.")

__main__()