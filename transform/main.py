# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
import argparse
import hashlib
import logging
logging.basicConfig(level=logging.INFO)

from urllib.parse import urlparse

import pandas as pd
import nltk
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

def main(filename):
    logger.info('starting cleaning process')
    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines(df)
    df = _tokenize_column(df)
    df = _remove_duplicate_entries(df, 'title')
    df = _delete_empty_rows(df)

    _save_data(df,filename)
    


def _read_data(filename):
    logger.info('reading file {}'.format(filename))
    return pd.read_csv(filename)

def _extract_newspaper_uid(filename):
    logger.info('extracting newspaper uid')
    newspaper_uid =filename.split('_')[0]

    logger.info('Newspaper uid: {}'.format(newspaper_uid))
    return newspaper_uid

def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('filling newspaper_uid colum with {}'.format(newspaper_uid))
    df['newspaper_uid'] = newspaper_uid
    return df

def _extract_host(df):
    logger.info('extracting host from urls')

    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df

def _fill_missing_titles(df):
    logger.info('filling missing titles')
    #se crea una mascara que separa las filas que no tienen datos
    missing_titles_mask = df['title'].isna()
    #con los datos cuyo valor corresponda a la anterior mascara
    #se accede a la url de su fila se le da un nombre al grupo que será extraido
    #y se le dice que busque un string sin / al final y que lo tome todo
    #las funicones permiten dividir el texto en una lista y despues volverla a unir
    #con espacios en ves de -
    missing_titles = (df[missing_titles_mask]['url']
                        .str.extract(r'(?P<missing_titles>[^/]+)$')
                        .applymap(lambda title: title.split('-'))
                        .applymap(lambda title_word: ' '.join(title_word))
                        )

    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:,'missing_titles']


    return df

def _generate_uids_for_rows(df):
     logger.info('generando uids para cada fila')

     uids =(df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
     df['uid'] = uids
     return df.set_index('uid')

def _remove_new_lines(df):
    logger.info('removiendo los new lines del body')
    stripped_body = (df
                        .apply(lambda row: row['body'], axis=1)
                        .apply(lambda body: list(body))
                        .apply(lambda letters: list(map(lambda letter: letter
                        .replace('\n', ' '), letters)))
                        .apply(lambda letters: ''.join(letters))
                    )
    df['body'] = stripped_body

    return df

def _tokenize_column(df):
    logger.info('tokenizando columnas')
    stop_words = set(stopwords.words('spanish'))

    def tokenize_column(df, column_name):
        return(df
                .dropna()
                .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                .apply(lambda valid_word_list: len(valid_word_list))
                )
    df['n_tokenise_title'] = tokenize_column(df, 'title')
    df['n_tokenise_body'] = tokenize_column(df, 'body')
    print(df['n_tokenise_title'])
    return df
def _remove_duplicate_entries(df, column_title):
    logger.info('Eliminando filas duplicadas')
    df.drop_duplicates(subset=[column_title], keep='first', inplace=True)

    return df
def _delete_empty_rows(df):
    logger.info('Eliminando filas vacias')
    df.dropna()

    return df
def _save_data(df, filename):
    clean_filename = 'clean_{}'.format(filename)
    logger.info('guardando dataframe como: {}'.format(clean_filename))
    df.to_csv(clean_filename, encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The path to dirty data',
                        type=str)

    args = parser.parse_args()

    df = main(args.filename)

