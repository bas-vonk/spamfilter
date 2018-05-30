FROM ubuntu:latest

# Install Python2.7
RUN apt-get update
RUN apt-get -y install wget
RUN apt-get -y install python2.7
RUN apt-get -y install python-pip
RUN apt-get -y install python-dev
RUN apt-get -y install python-mysqldb
RUN python2.7 -V

# Install the required modules
RUN pip install requests
RUN pip install Flask
RUN pip install flask-mysqldb
RUN pip install flask-wtf
RUN pip install tensorflow
RUN pip install elasticsearch

# Expose port 5000
EXPOSE 5000

COPY run.sh /

CMD ["/run.sh"]
