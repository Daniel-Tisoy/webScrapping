from sqlalchemy import Column, String, Integer

from base import Base

class Article(Base):
	__tablename__= 'articles'

	uid = Column(String, primary_key=True)
	body = Column(String)
	host = Column(String)
	title = Column(String)
	newspaper_uid = Column(String)
	n_tokenise_body = Column(Integer)
	n_tokenise_title = Column(Integer)
	url = Column(String, unique=True)


	def __init__(self,
				uid,
				body,
				host,
				newspaper_uid,
				n_tokenise_body,
				n_tokenise_title,
				url,
				title):
		self.uid = uid
		self.body = body
		self.host = host
		self.newspaper_uid = newspaper_uid
		self.n_tokenise_body = n_tokenise_body
		self.n_tokenise_title = n_tokenise_title
		self.url = url
		self.title = title