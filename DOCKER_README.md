# Smart Scraper - Déploiement Docker

Ce guide explique comment déployer l'application Smart Scraper avec Docker et Docker Compose.

## Prérequis

- Docker Desktop installé sur votre machine
- Docker Compose (inclus avec Docker Desktop)
- Au moins 4 GB de RAM disponible

## Architecture

L'application est composée de 5 services :

- **db** : Base de données MySQL 8.0
- **backend** : API Flask Python
- **scheduler** : Service de tâches planifiées pour le scraping automatique
- **frontend** : Application React servie par Nginx
- **phpmyadmin** : Interface web pour gérer la base de données

## Démarrage rapide

### 1. Cloner le projet et naviguer dans le répertoire

```bash
git clone <repository-url>
cd smart-scraper-groupe_4
```

### 2. Construire et démarrer tous les services

```bash
docker-compose up --build
```

Cette commande va :
- Construire les images Docker pour le backend, scheduler et frontend
- Télécharger les images MySQL et phpMyAdmin
- Créer et démarrer tous les conteneurs
- Initialiser la base de données avec le schéma
- Démarrer le scheduler automatique

### 3. Accéder à l'application

Une fois tous les services démarrés :

- **Application web** : http://localhost
- **API Backend** : http://localhost:5000
- **phpMyAdmin** : http://localhost:8080
- **Base de données** : localhost:3306

## Scheduler Automatique

Le scheduler automatique permet d'exécuter le scraping de manière régulière sans intervention manuelle.

### Configuration

Le scheduler peut être configuré via les variables d'environnement dans `docker-compose.yml` :

```yaml
scheduler:
  environment:
    - SCRAPE_FREQUENCY=daily  # hourly, daily, weekly
    - SCRAPE_TIME=02:00       # Format HH:MM (pour daily et weekly)
    - SCRAPE_DAY=monday       # Pour weekly: monday, tuesday, etc.
    - ADMIN_USERNAME=admin
    - ADMIN_PASSWORD=admin123
```

### Fréquences disponibles

- **hourly** : Scraping toutes les heures
- **daily** : Scraping tous les jours à l'heure spécifiée
- **weekly** : Scraping toutes les semaines le jour et à l'heure spécifiés

### Surveillance

- Les logs du scheduler sont disponibles dans l'interface d'administration
- Le statut et la prochaine exécution sont affichés en temps réel
- Les logs sont également sauvegardés dans `backend/scheduler.log`

## Commandes utiles

### Démarrer en arrière-plan
```bash
docker-compose up -d
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f scheduler
```

### Arrêter les services
```bash
docker-compose down
```

### Arrêter et supprimer les volumes (⚠️ supprime les données)
```bash
docker-compose down -v
```

### Reconstruire les images
```bash
docker-compose build --no-cache
```

### Redémarrer un service spécifique
```bash
docker-compose restart backend
docker-compose restart scheduler
```

## Configuration

### Variables d'environnement

Vous pouvez modifier les variables d'environnement dans le fichier `docker-compose.yml` :

#### Backend
- `DB_HOST` : Hôte de la base de données (par défaut: db)
- `DB_NAME` : Nom de la base de données (par défaut: paris_opendata)
- `DB_USER` : Utilisateur MySQL (par défaut: root)
- `DB_PASSWORD` : Mot de passe MySQL (par défaut: root)
- `SECRET_KEY` : Clé secrète pour JWT (⚠️ changez en production)

#### Frontend
- `REACT_APP_API_URL` : URL de l'API backend

### Ports

Les ports par défaut peuvent être modifiés dans `docker-compose.yml` :

```yaml
ports:
  - "80:80"      # Frontend (host:container)
  - "5000:5000"  # Backend
  - "3306:3306"  # MySQL
  - "8080:80"    # phpMyAdmin
```

## Développement

### Mode développement avec hot reload

Pour le développement, vous pouvez monter les volumes source :

```yaml
# Ajouter dans docker-compose.yml pour le backend
volumes:
  - ./backend:/app
  - /app/venv  # Exclure le venv

# Pour le frontend, utilisez plutôt npm run dev localement
```

### Débugger

Pour débugger un conteneur :

```bash
# Accéder au shell du conteneur
docker-compose exec backend bash
docker-compose exec frontend sh

# Voir les processus
docker-compose exec backend ps aux
```

## Production

### Sécurité

Avant de déployer en production :

1. **Changez les mots de passe par défaut**
2. **Générez une nouvelle SECRET_KEY**
3. **Configurez HTTPS**
4. **Limitez l'exposition des ports**
5. **Utilisez des secrets Docker**

### Exemple de configuration production

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  backend:
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
    # Ne pas exposer le port directement
    # ports:
    #   - "5000:5000"

  db:
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
    # Ne pas exposer le port directement
    # ports:
    #   - "3306:3306"
```

### Reverse Proxy

En production, utilisez un reverse proxy (Nginx, Traefik) :

```nginx
# Configuration Nginx
upstream backend {
    server localhost:5000;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://backend;
    }

    location / {
        proxy_pass http://localhost:80;
    }
}
```

## Dépannage

### Problèmes courants

#### Erreur de connexion à la base de données
```bash
# Vérifier que MySQL est démarré
docker-compose ps

# Vérifier les logs
docker-compose logs db

# Redémarrer la base de données
docker-compose restart db
```

#### Port déjà utilisé
```bash
# Voir les ports utilisés
netstat -tulpn | grep :80

# Modifier le port dans docker-compose.yml
ports:
  - "8080:80"  # Au lieu de "80:80"
```

#### Problème de permissions
```bash
# Nettoyer les volumes
docker-compose down -v
docker system prune -a

# Reconstruire
docker-compose up --build
```

### Logs et monitoring

```bash
# Surveiller les ressources
docker stats

# Inspecter un conteneur
docker inspect smart-scraper-backend

# Voir l'utilisation des volumes
docker volume ls
docker volume inspect smart-scraper-groupe_4_db_data
```

## Support

Pour toute question ou problème :

1. Vérifiez les logs avec `docker-compose logs`
2. Consultez la documentation Docker
3. Ouvrez une issue sur le repository

## Nettoyage

Pour nettoyer complètement Docker :

```bash
# Arrêter tous les conteneurs
docker-compose down

# Supprimer les images du projet
docker rmi smart-scraper-groupe_4_backend smart-scraper-groupe_4_frontend

# Nettoyer le système Docker (⚠️ supprime tout)
docker system prune -a --volumes
``` 