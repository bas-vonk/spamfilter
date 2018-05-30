import fnmatch
import os
import sys
import json
import time
from class_databases import *
from datapreprocessing import *
from classification import *
from Queue import Queue
from threading import Thread


def save_email_to_mysql(
    metadata,
    subject,
    body,
    wordcount,
    is_spam,
    mysql_instance
):
    """
    This method actually persist the email by saving it to a mysql-instance
    """

    # Get a cursor
    cursor = mysql_instance.getCursor()

    # Use the Mysql instance to save the data
    # Use parameter binding to prevent SQL injection
    cursor.execute(
        """INSERT INTO emails_with_classification
        (
            email_metadata,
            email_subject,
            email_body,
            wordcount,
            is_spam
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (metadata, subject, body, wordcount, is_spam, )
    )

    # Commit the result to actually insert the data in the database
    mysql_instance.commit()


def save_email_to_elasticsearch(
    metadata,
    subject,
    body,
    wordcount,
    is_spam,
    elasticsearch_instance
):
    """
    This method indexes the document in ElasticSearch. From ElasticSearch
    a quick search in the documents / emails is possible.
    """

    # Define the document (document = elasticsearch slang)
    es_body = {
        'metadata': unicode(metadata, "utf-8", errors='replace'),
        'subject': unicode(subject, "utf-8", errors='replace'),
        'body': unicode(body, "utf-8", errors='replace'),
        'wordcount': int(wordcount),
        'is_spam': int(is_spam)
    }

    # Use the Elasticsearch instance to index the data
    res = elasticsearch_instance.index(index='pacmed',
                                       doc_type='email',
                                       body=es_body
                                       )


def save_email_to_storage(
    metadata,
    subject,
    body,
    wordcount,
    is_spam,
    mysql_instance,
    elasticsearch_instance
):
    """
    Save the parsed email to both mysql (for safety and persistance), and
    ElasticSearch for quick searchability. Don't use ElasticSearch alone,
    since documents are stored in the RAM, and instance failure may cause
    the data to be lost. ElasticSearch can always be rebuilt from the
    persistent data storage.

    The mysql and elasticsearch_instance are passed in here so that one worker
    (parallel job) re-uses the same connection. In a production environment
    a solution like connection pooling is possibly more appropriate.
    """

    # Save the data to mysql
    save_email_to_mysql(metadata,
                        subject,
                        body,
                        wordcount,
                        is_spam,
                        mysql_instance
                        )

    # Save the data to elasticsearch
    save_email_to_elasticsearch(metadata,
                                subject,
                                body,
                                wordcount,
                                is_spam,
                                elasticsearch_instance
                                )


def process_email(email, mysql_instance, elasticsearch_instance):
    """
    Process an email (get relevant information, classify it and persist it)
    """

    # Create an email object, which generates all kinds of characteristics
    # of the email, such as metadata, the body, subject, and so forth
    features = extract_email_features(email)
    if features is False:
        return

    # Get the classification for the email
    # This is actually a webhook, and needs to be made more fancy
    classification = get_classification()

    # Save email
    save_email_to_storage(features['metadata'],
                          features['subject'],
                          features['body'],
                          features['wordcount'],
                          classification,
                          mysql_instance,
                          elasticsearch_instance
                          )

    # Return
    return


def generator_emails(folder):
    """
    Generator: Recursively get all datafiles in a certain directory and
               make them an iterable (once every email is processed, this
               generator will be depleted).
    """

    # Use os.walk to recursively walk through all files and folders in a given
    # directory. Ideally the extenstion is used to parse (for example) only
    # .txt files, but here the extension is both .txt and missingself.
    # For each filename, read the contents of the email and yield it for
    # further processing

    for root, dirnames, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, '*'):
            email_plain = os.path.join(root, filename)
            with open(email_plain, 'r') as email:
                email = email.read()
                yield email


def worker(q, thread_name):
    """
    This is worker process to keep on consuming jobs / emails from the queue,
    and processing them
    """

    # Create instances for both mysql and elasticsearch
    # This is done once per job, and repeatedly used again
    # In production usage of a connection pool is probably more appropriate
    mysql_instance = MySQL()
    elasticsearch_instance = ElasticSearch()

    # Continuously keep on consuming from the queue. Threads are joined
    # when the queue is empty, so this function needs not to worry about it
    while True:

        # Get an email / job from the queue (if there are any)
        if not q.empty():
            item = q.get()

            # Process it
            process_email(item, mysql_instance, elasticsearch_instance)

            # Output (for development only)
            print thread_name + " has processed an email!"

            # Mark the task as done
            q.task_done()


def current_sec_time():
    """
    Return the current timestamp in seconds
    """

    return time.time()


def main():
    """
    This is the main code. The streaming system is based on parallel processes
    (threads). The generator that ensures the emails are flowing in the system
    actually places them in a queue (publisher), while to concurrent processes
    consume them from the queue. In a production environment this may partially
    be build with (for instance), async queuing systems like RabbitMQ, or even
    Redis. Another alternative would be using systems like Hadoop, where you
    can actually bring the processing code to the data, instead of vice versa.
    """

    # Define the start time to be able to track total duration
    start_time = current_sec_time()

    # Initialize a queue
    # For memory purposes, don't let the queue become to big (serves no
    # purpose anyway)
    q = Queue(maxsize=1000)

    # As a working example, use eight threads for parallel processing
    # This is mainly for illustrational purposes. Most local machines have
    # either 2 or 4 cores, so at most two/four concurrent processes
    # are used.
    threadcount = 8
    for i in range(threadcount):
        t = Thread(target=worker, args=(q, "Thread-" + str(i + 1)))
        t.daemon = True
        t.start()

    # Do the actual streaming and the processing
    for email in generator_emails('/www/data/emails'):
        q.put(email)

    # When the queue is empty, terminate the script
    q.join()
    print 'All finished in ' + str(int(current_sec_time() - start_time)) + \
        ' seconds! Enjoy working with your data.'


if __name__ == "__main__":
    main()
