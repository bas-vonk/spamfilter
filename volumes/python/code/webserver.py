from flask import *
from config import Config
from forms import SearchForm
from class_databases import *
from elasticsearch import Elasticsearch
import os
import sys

# Initialize the flask app and load the required pug extension
# Also, initialize a DB class
app = Flask(__name__)
app.config.from_object(Config)

# fixes trailing slashes leading to 404's
# https://stackoverflow.com/questions/33241050/trailing-slash-triggers-404-in-flask-path-rule
app.url_map.strict_slashes = False


# For each request, obtain a database connection
@app.before_request
def get_db_instance():
    g.db_instance = MySQL()


# After each request, close the database connection
@app.teardown_request
def destroy_db_instance(exception=None):
    g.db_instance.closeConnection()


# Healthcheck Endpoint
@app.route('/healthcheck')
def healthcheck():
    return 'Up and running!', 200


# Index Endpoint
@app.route('/index')
def index():
    return render_template('index.html')


# Endpoint for shared learning material
@app.route("/search_email_in_elasticsearch", methods=['GET', 'POST'])
def search_email_in_elasticsearch():
    """
    This function shows emails that match a keyword (in the subject),
    including their classification.
    """

    form = SearchForm()

    if form.validate_on_submit():

        es = Elasticsearch([{'host': 'pacmed-elasticsearch', 'port': 9200}])

        query = {
          "query": {
            "bool": {
              "should": [
                {"match": {
                    "subject":  {
                      "query": form.query.data,
                      "boost": 3
                    }
                  }
                 },
                {"match": {
                    "metadata":  {
                      "query": form.query.data,
                      "boost": 2
                    }
                  }
                 },
                {"match": {
                    "body":  {
                      "query": form.query.data,
                      "boost": 1
                    }
                  }
                 }
              ]
            }
          }
        }

        result = es.search(index="pacmed", body=query)

        data = []
        for hit in result['hits']['hits']:
            data.append({
                "id": str(hit['_id']),
                "relevance": str(hit['_score']),
                "metadata": hit['_source']['metadata'][:200],
                "subject": hit['_source']['subject'],
                "body": hit['_source']['body'][:200],
                "isSpam": ("yes" if hit['_source']['is_spam'] is 1 else "no")
            }.copy())

        return render_template('search_results.html', title='Results:', data=data)

    return render_template('search_email_in_elasticsearch.html', form=form)


@app.route("/search_email_in_mysql", methods=['GET', 'POST'])
def search_email_in_mysql():
    """
    This function shows emails that match a keyword, including their
    classification
    """

    form = SearchForm()

    if form.validate_on_submit():

        # Create a cursor object for the database
        cursor = g.db_instance.getCursor()

        # Execute a query to retrieve the shared activity.
        cursor.execute(
            """SELECT
                *
            FROM emails_with_classification
            WHERE email_subject LIKE %s
            """,
            ("%" + form.query.data + "%",)
        )
        # Fetch the results
        result = cursor.fetchall()

        data = []
        for row in result:
            data.append({
                "id": str(row['id']),
                "relevance": "n/a",
                "metadata": row['email_metadata'][:200],
                "subject": row['email_subject'],
                "body": row['email_body'][:200],
                "isSpam": ("yes" if row['is_spam'] is 1 else "no")
            }.copy())

        return render_template('search_results.html', data=data)

    return render_template('search_email_in_mysql.html', title='Search in MySQL:', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
