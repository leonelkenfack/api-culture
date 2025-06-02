# API Flask

Ce projet est une API REST construite avec Flask.

## Installation

### Méthode 1 : Installation locale

1. Créez un environnement virtuel :
```bash
python -m venv venv
```

2. Activez l'environnement virtuel :
- Windows :
```bash
venv\Scripts\activate
```
- Linux/Mac :
```bash
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Méthode 2 : Utilisation de Docker

#### Option 1 : Docker simple
1. Construisez l'image Docker :
```bash
docker build -t api-flask .
```

2. Lancez le conteneur :
```bash
docker run -p 5000:5000 api-flask
```

#### Option 2 : Docker Compose (recommandé)
1. Lancez l'application avec Docker Compose :
```bash
docker-compose up
```

Pour lancer en arrière-plan :
```bash
docker-compose up -d
```

Pour arrêter l'application :
```bash
docker-compose down
```

## Lancement de l'application

### Sans Docker
Pour lancer l'application en mode développement :
```bash
python app.py
```

### Avec Docker
L'application sera automatiquement lancée lors du démarrage du conteneur.

L'API sera accessible à l'adresse : http://localhost:5000 