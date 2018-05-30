# Spamfilter

This is the code for a mini-cluster that processes emails from the [Enron-Spam](http://www.aueb.gr/users/ion/data/enron-spam/) database. It streams data into both MySQL and ElasticSearch and uses Flask to create a minor web interface to search through the processed emails.

## Prerequisites:

- [Docker](https://www.docker.com)

## Characteristics:

- It reads data (emails) item by item using a generator function and a Queue system to allow for parallel processing.

- It then processes the text of the emails. Some basic features (word count) are extracted, as well as the body of the email, metadata and the subject.

- It then hits a hook to classify the email as either spam or ham. In this code, this is just a random assessment.

- The emails are persistently stored in a MySQL database and quickly searchable indexed in ElasticSearch. In MySQL the user is able to search in the subject, while in ElasticSearch the whole content of the email is indexed and thus searchable.

- On localhost:5000/index a search engine is running that enables the user to search either in the ElasticSearch instance or the MySQL database.

## Usage

- Run startup.sh ```./startup.sh``` to fire up the the cluster and start streaming the data. If you choose not to, ensure the data (txt-files are in volumes/python/data/emails)

- Code is to be found in the ```volumes/python/code``` folder. The data is predownloaded in the ```volumes/python/data``` folder by the startup script.
