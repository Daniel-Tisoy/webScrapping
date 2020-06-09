import csv
import datetime
import re
import argparse
import logging
logging.basicConfig(level=logging.INFO)

from requests.exceptions import  HTTPError
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ContentDecodingError

from common import config
import news_pages_objects as news

logger = logging.getLogger(__name__)
#se determina la forma de los links
is_well_formed_link = re.compile(r'^https?://.+/.+$') #https://example.com/hello
is_root_path = re.compile(r'^/.+$') #/some-text

#funcion que scrapea utillizando el input del usuario
def _news_scrapper(news_site_uid):
    #una ves importado la funcion config de common.py se obtiene la url del sitio
    #que esta en comfig.yaml
    host = config()['news_sites'][news_site_uid]['url']

    logging.info('Beginning scraper for {}'.format(host))
#se importa la clase que obtiene los vinculos de la pagina web y se inicializa
    homepage = news.HomePage(news_site_uid, host)
    #articles contendra los articulos
    articles = []

    for link in homepage.article_links:
        article = _fetch_article(news_site_uid,host,link)

        if article:
            logger.info('Article fected!!!!!!!!!')
            articles.append(article)
            break



    print(type(dir(articles[0])))

    #_save_articles(news_site_uid,articles)


def _save_articles(news_site_uid,articles):
    now = datetime.datetime.now().strftime('%y_%m_%d')
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(news_site_uid=news_site_uid,datetime=now)

    csv_headers = list(filter(lambda property: not property.startswith('_'),dir(articles[0])))


    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)


def _fetch_article(news_site_uid,host,link):
    logger.info('start fetching article at {}'. format(link))


    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError, ContentDecodingError) as e:
        logger.warning('Error fetching the article', exc_info=False)


    if article and not article.body:
        logger.warning('Invalid article. There is no body')
        return None
    return article

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host,link)
    else:
        return '{host}/{url}'.format(host=host, url=link)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web scraper de algunos periodicos')
    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site', help='The news site that you want scrape',type = str,choices=news_site_choices)

    args = parser.parse_args()

    _news_scrapper(args.news_site)
