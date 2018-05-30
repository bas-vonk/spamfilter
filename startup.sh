#!/bin/bash

echo "Bring up all the required docker containers:"
docker-compose up -d --build

echo "Sleep for 10 seconds, to ensure the mysql server is up and running:"
sleep 10

echo "Create the proper users in the mysql database:"
docker exec pacmed-mysql mysql -uroot -prootpass -e \
"CREATE DATABASE IF NOT EXISTS pacmed; \
GRANT USAGE ON *.* TO pacmed@'%' IDENTIFIED BY 'pacmed_password'; \
GRANT ALL PRIVILEGES ON pacmed.* TO pacmed@'%'; \
FLUSH PRIVILEGES;"

echo "Create the database to persist the emails:"
docker exec pacmed-mysql mysql -uroot -prootpass -e \
"CREATE TABLE IF NOT EXISTS pacmed.emails_with_classification ( id INT NOT NULL AUTO_INCREMENT , email_metadata MEDIUMTEXT NOT NULL , email_subject MEDIUMTEXT NOT NULL , email_body MEDIUMTEXT NOT NULL , is_spam BOOLEAN NOT NULL , PRIMARY KEY (id)) ENGINE = InnoDB;"

echo "Add the data to the folder:"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/ham/beck-s.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/ham/farmer-d.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/ham/kaminski-v.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/ham/kitchen-l.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/ham/lokay-m.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/ham/williams-w3.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/spam/BG.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/spam/GP.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"
docker exec pacmed-python-application sh -c "wget http://www.aueb.gr/users/ion/data/enron-spam/raw/spam/SH.tar.gz -O /www/data/emails/temp.tar.gz && tar xf /www/data/emails/temp.tar.gz && rm /www/data/emails/temp.tar.gz"

echo "The mini-cluster is al set up: "
echo "Access phpMyAdmin at http://localhost/8080"
echo "Use credentials: pacmed / pacmed_password."
echo "Access kibana (ElasticSearch interface) at http://localhost:5601"
echo "Access the search interface at http://localhost:5000/index"
echo "Check the health of ElasticSearch at http://localhost:9200/_cat/health"

echo "Now the streaming starts, feel free to look around!"
docker exec -it pacmed-python-application python /www/code/dataprocessing.py
