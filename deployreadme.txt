###CORENLP SERVER####
The core nlp server lives in a docker container.
This can be found here:
https://github.com/akiomik/stanford-corenlp-server

You need good github ssh creds to follow the directions in t akiomik's directions
otherwise, You have to go and manualy download the corenlp files and place them in /lib directory
you can find those at the coreNLP github: https://github.com/stanfordnlp/CoreNLP

download the repo, set up your annotator settings and build the docker container, and run it.

EDIT THIS FILE TO THE ANNOTATORS
src/main/resources/application.properties.
annotators=tokenize,ssplit,pos,lemma,ner,coreference

sudo docker build -t akiomik/stanford-corenlp-server .
sudo docker run -d -p 8081:8081 -p 9990:9990 akiomik/stanford-corenlp-server


###DATABASE SERVER###
We run the latest image of postgres.  Just pull it from docker and run it.

sudo docker pull postgres
sudo docker -p 127.0.0.1:5431:5432