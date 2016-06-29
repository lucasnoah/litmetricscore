Litmetrics
==========

Litmetrics is an API and webapp frontend for a variety of NLP and topic modeling services.  I't allows you to upload texts, normalize their spelling and parse them into labled tokens via the stanford CoreNLP server.  These tokens are then stored in a Postgres relational database so that you can select only what you need when you send data to topic modeling software.

You can find litmetrics with a frontend at [www.litmetrics.com](www.litmetrics.com) , but If you are going to use this for a class or do "Extensive" processing.  You can run a version of the server yourself using docker and docker-compose.

Features
--------

- Document processing and parsing via Standford coreNLP
- Spelling standardization with Vard
- A variety of methods for topic modeling made accessible via an API and web app
- The ability to filter by POS tags, stopwords and variety of other fields before sending your data to the topic modeling
- Fine grain control of a variety of topic modeling algorithms
- Async celery workers for processing heavy tasks

Running Your Own Sever
----------------------

The Litmetrics server is deployed using Docker-Compose.  It is extremely easy to run your own instance! This is recommended in instances where many students will be using the project and the server will be under a high computational load. 

1.  Install Docker and docker-compose
[https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
2.  Clone the repo, navigate to the directory and run:
    ```
    docker-compose up
    ```
3. If you wish to use the Angular JS frontend, install and run it here:
[https://github.com/lucasnoah/litmetricsfrontend](https://github.com/lucasnoah/litmetricsfrontend)

API documentation
-----------------

If you wish to implement your own frontend for the Litmetrics Server, a [swagger](https://github.com/marcgibbons/django-rest-swagger) generated documentation can be found at [api.litmetrics.com/docs](api.litmetrics.com/docs).  Be warned that this is a work in progress though.

    
The Document Parsing Process
----------------------------

Litmetrics is run using a Django/Postgres server stack.  As documents are uploaded they are parsed into Django ORM models and saved to the database.

1. Texts are uploaded to the server
2. Document parsing celery task is triggered 
3. Spelling is standardized using [Vard 2](http://ucrel.lancs.ac.uk/vard/about/).
4. The Document is parsed into Sentence and Word Tokens objects using the [Standford CoreNLP Server](http://stanfordnlp.github.io/CoreNLP/corenlp-server.html)
    These objects are described in more detail further on in the documentation.
5. Once parsing is done objects are made available as CorpusItems to be gathered in Collections and sent to topic modeling services

The Core Data Models
--------------------

As documents are uploaded and processed they are saved as standard Django Orm Models.  This outlines the most basic of those
models.  More details can be found by viewing the models.py files included in the source code.

#### TextFile

This represents an unparsed uploaded TextFile and contains the following fields.
- user - Django user instance
- file - a raw .txt file

#### CorpusItem
Corpus Items represent an uploaded text that has been normalized and parsed.  This is the PK that Sentence and Word Token objects link to. 

#### Sentence 
Sentences represent a sentence as parsed by the Stanford coreNLP server, they link back to the corpus item.

#### WordToken
Word Tokens represent individual word tokens containing the various parsing information a returned by the coreNLP sever. Each token is processed in the context of an individual sentence.
- after: the token directly before this one
- before: the token directly after this one.
- index: the token index in the sentence.  
- lemma: lemma of the word token
- ner: Boolean flag for labling this token as a [Named Entity](en.wikipedia.org/wiki/Named_entity)  
- original_text: the non lemmatized original token text
- pos: the pos tag from the [Penn Treebank Tag system](https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html)
- sentence: The PK of the sentence this token is attached to
- wordnet_id: The [Wordnet](wordnet.princeton.edu) words sense as an integer 

Topic Modeling Methods
----------------------

Most of the topic modeling in Litmetrics is done using the awesome Topic Modeling package [Gensim](https://radimrehurek.com/gensim/). This describes the different types of modeling and how they are achieved on the server.

#### LDA 

LDA or [Latent Dirichlet Allocation](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) is the bread and butter topic modeling method used in most cases by most people.  We provide two methods of doing this.  The [Gensim standard LDA Model](https://radimrehurek.com/gensim/models/ldamodel.html) and the [Mallet](http://mallet.cs.umass.edu/) implementation of LDA.  Mallet has been traditionally used in academic humanities papers that address topic modeling in literature. We enable you to send identical and standardized data models to both methods in the hopes that this will improve academic rigor while using topic modeling in papers. 

#### HDP

HDP or [Hierarchical Dirichlet Process](https://en.wikipedia.org/wiki/Hierarchical_Dirichlet_process) is an iteration upon LDA that uses math to help predetermine the ideal number of topics for your data set.  We implement this with the [Gensim HDP model](https://radimrehurek.com/gensim/models/hdpmodel.html).

#### near neighbor LSA/LSI
LSA/ LSI or [Latent Semantic Analysis](https://en.wikipedia.org/wiki/Latent_semantic_analysis) allows you to find words similar to a queried search terms.  This is much like the [service](http://lsa.colorado.edu/) offered by The University Of Colorado, Except that we allow you to build your own Corpus Context to conduct the search in as opposed to the static set of Corpus Collection options that they offer. This is implemented using the [Gensim LSI Model](https://radimrehurek.com/gensim/models/lsimodel.html).

Obvious Factors That Greatly Affect Topic Modeling Outcomes
-----------------------------------------------------------

Litmetrics was created for two main reasons.

1. So that humanities academics could have easy access to topic modeling while have to learn the minimum of technical skills
2. To highlight the huge variance of results that can be achieved by making relatively minor tweaks to the process of topic modeling and the data being sent to the algorithms

Here are some of the low hanging fruit that we have found while looking for small changes that drastically afffect the outcome of topic modeling process.

#### Chunking
The size and amount of documents that you send to topic modeling has a huge effect on outcomes. We allow you to chunk your Collections in several different ways before sending them off to modeling.  
1. by word count
2. by breakword
3. not at all

#### Filtering Stopwords
Removing common [stopwords](https://en.wikipedia.org/wiki/Stop_words) that have no bearing on the meaning of the text leads to much better results.

#### Filtering by POS Tokens
Removing all words of certain POS types is an advanced mehthod of stopword filtering and can allow you to explore different types of relationships in a Corpus Collection.

#### Filtering 
We find that removing Named Entities and replacing words with their Lemmas can have a profound effect on outcomes.  

Contribute
----------

- Issue Tracker: [github.com/lucasnoah/litmetricscore/issues](github.com/lucasnoah/litmetricscore/issues)
- Source Code: [github.com/lucasnoah/litmetricscore](github.com/lucasnoah/litmetricscore)

Support
-------

If you are having issues, please let us know.
The project technical manager can be reached at : lucas.bird.noah@gmail.com
The projects academic manager can be reached at : jf@rasputinmusic.com

License
-------

The project is licensed under the BSD license.