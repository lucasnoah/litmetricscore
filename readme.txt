Litmetrics is an API frontend for a variety of NLP and topic modeling services.  I't allows you to upload texts, normalize their spelling and parse them into labled tokens via the stanford CoreNLP server.  These tokens are then stored in a Postgres relational database so that you can select only what you need when you send data to topic modeling software.  

You can find litmetrics with a frontend at www.litmetrics.com , but If you are going to use this for a class or do "Extensive" processing.  You can run a version of the server yourself using docker and docker-compose. 

STEPS:

1. Install Docker and Docker-Compose
  https://docs.docker.com/compose/install/
  
2. Clone this repo, navigatae to the directory and run docker-compose up.  Thats it!  You now will be able to interact with your own version of the document processing server at localhost:8000.
