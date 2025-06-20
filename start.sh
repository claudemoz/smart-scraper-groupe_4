#!/bin/bash

# Script de démarrage pour Smart Scraper
echo "🏗️  Démarrage de Smart Scraper avec Docker..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker Desktop."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Arrêter les conteneurs existants s'ils existent
echo "Arrêt des conteneurs existants..."
docker-compose down

# Construire et démarrer les services
echo  Construction et démarrage des services..."
docker-compose up --build -d

# Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 30

# Vérifier le statut des services
echo "Vérification du statut des services..."
docker-compose ps

echo ""
echo "Smart Scraper est maintenant disponible !"
echo ""
echo "Application web : http://localhost"
echo "API Backend : http://localhost:5000"
echo " phpMyAdmin : http://localhost:8080"
echo ""
echo "Identifiants de connexion :"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Pour voir les logs : docker-compose logs -f"
echo "Pour arrêter : docker-compose down" 