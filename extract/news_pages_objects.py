import requests
import bs4
from common import config
#la clase madre NewsPage tiene las funciones seleccionar los articulos,
#visitar y obtener el html
#NewsPage obtiene (eltiempo),(https://www.eltiempo.com/)
class NewsPage:
    def __init__(self,news_site_uid,url):
        #se accede a las  configuraciones del sitio url y queries
        self._config = config()['news_sites'][news_site_uid]
        #dentro de queries estan los links de la pagina principal y los titulos y articulos
        self._queries = self._config['queries']
        #html aun no se ha solicitado
        #para ello esta la funcion visit
        self._html = None

        self._visit(url)
    #selecionara la clase que se ingrese ya sea para obtener links, titulo o articulos
    def _select(self, query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        #solicitud a la url de la pagina web
        response = requests.get(url)
        #mandar un estado de si la solicitud fue concluida correctamente
        response.raise_for_status()
        #se obtiene el html de la pagina
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')
#pagina principal del sitio web
class HomePage(NewsPage):
    #recibirá los mismos parametros que NewsPage
    def __init__(self,news_site_uid,url):
        #super permite invocar el metodo de la clase NewsPage con todos sus atributos
        super().__init__(news_site_uid,url)
#con @property , article_links se convierte en una proiedad
    @property
    def article_links(self):
        link_list = []
        for link in self._select(self._queries['homepage_article_links']):
            if  link and link.has_attr('href'):
                link_list.append(link)
        #retornar el link list sin ningun elemento repetido
        return set(link['href'] for link in link_list)

class ArticlePage(NewsPage):
    def __init__(self, news_site_uid,url):
        super().__init__(news_site_uid,url)

    @property
    def body(self):
        result = self._select(self._queries['article_body'])

        return result[0].text if len(result) else ''

    @property
    def title(self):
        result = self._select(self._queries['article_title'])

        return result[0].text if len(result) else ''
