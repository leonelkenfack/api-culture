# API Rotation des Cultures

Ce projet est une API REST construite avec Flask et deploye sur Docker. 
Elle vous permet d'obtenir une liste de culture eligible a la rotation avec un score d'eligibilite detaille.

## Installation et Lancement de l'application

```bash
docker-compose up -d
```
## Ajout des donnes dans la base

Une fois le serveur lance, suivez les etapes suivantes : 

1. Creer un repository nomme `cultures`.
2. Allez dans import et importez tous les fichiers rdf dans rdf-data. (`rotations.rdf` et `relations.rdf` en derniers)


NB: Lors de l'import des fichiers `.rdf`, renseigner le `Base IRI` avec la valeur ` http://example.org/cultures#`




## Liste des serveurs

* Flask DOC : http://localhost:5200/api/doc
* GraphDB : http://localhost:7200 

