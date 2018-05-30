#!/bin/bash

echo "Bring up all the required docker containers."
docker-compose up -d --build

echo "Sleep for 10 seconds, to ensure the mysql server is up and running."
sleep 10

echo "Create the proper users in the mysql database."
docker exec pacmed-mysql mysql -uroot -prootpass -e \
"CREATE DATABASE IF NOT EXISTS pacmed; \
GRANT USAGE ON *.* TO pacmed@'%' IDENTIFIED BY 'pacmed_password'; \
GRANT ALL PRIVILEGES ON pacmed.* TO pacmed@'%'; \
FLUSH PRIVILEGES;"

echo "Create the database to persist the emails"
docker exec pacmed-mysql mysql -uroot -prootpass -e \
"CREATE TABLE IF NOT EXISTS pacmed.emails_with_classification ( id INT NOT NULL AUTO_INCREMENT , email_metadata MEDIUMTEXT NOT NULL , email_subject MEDIUMTEXT NOT NULL , email_body MEDIUMTEXT NOT NULL , is_spam BOOLEAN NOT NULL , PRIMARY KEY (id)) ENGINE = InnoDB;"

echo "The mini-cluster is al set up: "
echo "Access phpMyAdmin at http://localhost/8080"
echo "Use credentials: pacmed / pacmed_password."
echo "Access kibana (ElasticSearch interface) at http://localhost:5601"
echo "Access the search interface at http://localhost:5000/index"
echo "Check the health of ElasticSearch at http://localhost:9200/_cat/health"

echo "Now the streaming starts, feel free to look around!"
docker exec -it pacmed-python-application python /www/code/dataprocessing.py
