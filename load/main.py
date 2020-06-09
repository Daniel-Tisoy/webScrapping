import argparse
import logging
logging.basicConfig(level=logging.INFO)

import pandas as pd

from article import Article
from base import Base, engine, Session


logger = logging.getLogger(__name__)


def main(filename):
	Base.metadata.create_all(engine)
	session = Session()

	articles = pd.read_csv(filename)
	# iterrow permite generar un loop en cada una de las filas del datagrame
	#portanto lo que devolvera sera el indice y la columna
	for index, row in articles.iterrows():
		logger.info('cargando el articulo uid {} en la DB'. format(row['uid']))
		article = Article(row['uid'],
						row['body'],
						row['host'],
						row['newspaper_uid'],
						row['n_tokenise_body'],
						row['n_tokenise_title'],
						row['title'],
						row['url'])
		#ingresando articulos a la base de datos
		session.add(article)

	session.commit()
	session.close()



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('filename',help = 'Ingrese archivo que desea cargar a la bd', type= str)

	args = parser.parse_args()

	main(args.filename)