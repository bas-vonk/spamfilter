import MySQLdb
from MySQLdb import cursors
from elasticsearch import Elasticsearch
import os
import sys

"""
These classes enable the code to build connections to both Mysql
and ElasticSearch, and perform basic operations using these connections
"""


class MySQL():

    def __init__(self):

        # Connection parameters are obtained from the environment
        # (in a production environment these should be safely stored in
        # secrets (when Kubernetes is used))
        MYSQL_HOST = os.environ['db_host']
        MYSQL_USER = os.environ['db_username']
        MYSQL_PASSWORD = os.environ['db_password']
        MYSQL_DATABASE = os.environ['db_database']

        self.mysql = MySQLdb.connect(host=MYSQL_HOST,
                                     user=MYSQL_USER,
                                     passwd=MYSQL_PASSWORD,
                                     db=MYSQL_DATABASE,
                                     use_unicode=True,
                                     cursorclass=MySQLdb.cursors.DictCursor
                                     )

    def getCursor(self):

        return self.mysql.cursor()

    def commit(self):

        return self.mysql.commit()

    def closeConnection(self):

        return self.mysql.close()


class ElasticSearch():

    def __init__(self):

        # Connection parameters are obtained from the environment
        # (in a production environment these should be safely stored in
        # secrets (when Kubernetes is used))
        ELASTICSEARCH_HOST = os.environ['es_host']
        ELASTICSEARCH_PORT = os.environ['es_port']

        self.elasticsearch = Elasticsearch([{
            "host": ELASTICSEARCH_HOST,
            "port": ELASTICSEARCH_PORT
        }])

    def index(self, **kwargs):

        return self.elasticsearch.index(**kwargs)

    def search(self, **kwargs):

        return self.elasticsearch.search(**kwargs)
