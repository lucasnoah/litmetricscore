############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM python:2.7-slim

RUN apt-get update && apt-get install -y \
		gcc \
		gettext \
		mysql-client libmysqlclient-dev \
		postgresql-client libpq-dev \
		sqlite3 \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set the file maintainer (your name - the file's author)
MAINTAINER lucas noah

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=./
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/code

# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python python-pip
RUN apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran -y
RUN apt-get install python-numpy -y
RUN apt-get install python-scipy -y

RUN apt-get update && apt-get install -y wget

ENV DOCKERIZE_VERSION v0.2.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN pip install scipy
RUN pip install numpy

RUN pip install gensim
RUN pip install redis
RUN pip install sendgrid-django

RUN \
    echo "===> add webupd8 repository..."  && \
    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list  && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list  && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886  && \
    apt-get update  && \
    \
    \
    echo "===> install Java"  && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections  && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections  && \
    DEBIAN_FRONTEND=noninteractive  apt-get install -y --force-yes oracle-java8-installer oracle-java8-set-default  && \
    \
    \
    echo "===> clean up..."  && \
    rm -rf /var/cache/oracle-jdk8-installer  && \
    apt-get clean  && \
    rm -rf /var/lib/apt/lists/*

# Define working directory.
WORKDIR /data

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle
# Copy application source code to SRCDIR
ADD $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Install Python dependencies

RUN pip install -r $DOCKYARD_SRVPROJ/requirements.txt
RUN python -m nltk.downloader -d /usr/share/nltk_data stopwords
RUN python -m nltk.downloader -d /usr/share/nltk_data names
RUN python -m nltk.downloader -d /usr/share/nltk_data wordnet



# Deal with java8 install



# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir media static logs
VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

# Port to expose
EXPOSE 8000

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ
#ENTRYPOINT ["/docker-entrypoint.sh"]