#!/usr/bin/env python3
"""
Scheduler pour les tâches automatiques de scraping
"""

import os
import sys
import time
import logging
import schedule
import subprocess
from datetime import datetime
from typing import Optional
import requests
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScrapingScheduler:
    def __init__(self):
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
        self.admin_token = None
        self.last_scrape_time = None
        
    def authenticate(self) -> bool:
        """Authentifie l'utilisateur admin pour pouvoir déclencher le scraper"""
        try:
            auth_url = f"{self.api_base_url}/auth/login"
            credentials = {
                'username': os.getenv('ADMIN_USERNAME', 'admin'),
                'password': os.getenv('ADMIN_PASSWORD', 'admin123')
            }
            
            response = requests.post(auth_url, json=credentials, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('token'):
                    self.admin_token = data['data']['token']
                    logger.info("Authentification réussie")
                    return True
                else:
                    logger.error("Réponse d'authentification invalide")
                    return False
            else:
                logger.error(f"Erreur d'authentification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return False
    
    def trigger_scraping(self) -> bool:
        """Déclenche le scraping via l'API"""
        try:
            if not self.admin_token:
                logger.warning("Token d'authentification manquant, tentative de reconnexion...")
                if not self.authenticate():
                    logger.error("Impossible de s'authentifier")
                    return False
            
            scrape_url = f"{self.api_base_url}/scrape"
            headers = {
                'Authorization': f'Bearer {self.admin_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(scrape_url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.last_scrape_time = datetime.now()
                    logger.info("Scraping déclenché avec succès")
                    return True
                else:
                    logger.error(f"Erreur API: {data.get('error', 'Erreur inconnue')}")
                    return False
            elif response.status_code == 401:
                logger.warning("Token expiré, tentative de reconnexion...")
                self.admin_token = None
                return self.trigger_scraping()  # Retry avec nouvelle authentification
            else:
                logger.error(f"Erreur HTTP: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du déclenchement du scraping: {e}")
            return False
    
    def check_scraper_status(self) -> Optional[dict]:
        """Vérifie le statut du scraper"""
        try:
            status_url = f"{self.api_base_url}/scrape/status"
            response = requests.get(status_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du statut: {e}")
            return None
    
    def scheduled_scraping(self):
        """Fonction appelée par le scheduler pour le scraping automatique"""
        logger.info("Début du scraping automatique planifié")
        
        # Vérifier si un scraping est déjà en cours
        status = self.check_scraper_status()
        if status and status.get('is_running'):
            logger.info("Un scraping est déjà en cours, passage du tour")
            return
        
        # Déclencher le scraping
        success = self.trigger_scraping()
        
        if success:
            logger.info("Scraping automatique déclenché avec succès")
        else:
            logger.error("Échec du scraping automatique")
    
    def health_check(self):
        """Vérifie la santé de l'API"""
        try:
            health_url = f"{self.api_base_url}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Health check: API opérationnelle")
            else:
                logger.warning(f"Health check: API non disponible (status: {response.status_code})")
                
        except Exception as e:
            logger.error(f"Health check échoué: {e}")
    
    def setup_schedules(self):
        """Configure les tâches planifiées"""
        # Scraping automatique
        scrape_frequency = os.getenv('SCRAPE_FREQUENCY', 'daily')
        scrape_time = os.getenv('SCRAPE_TIME', '02:00')
        
        if scrape_frequency == 'hourly':
            schedule.every().hour.do(self.scheduled_scraping)
            logger.info("Scraping planifié: toutes les heures")
        elif scrape_frequency == 'daily':
            schedule.every().day.at(scrape_time).do(self.scheduled_scraping)
            logger.info(f"Scraping planifié: tous les jours à {scrape_time}")
        elif scrape_frequency == 'weekly':
            day = os.getenv('SCRAPE_DAY', 'monday')
            getattr(schedule.every(), day.lower()).at(scrape_time).do(self.scheduled_scraping)
            logger.info(f"Scraping planifié: tous les {day} à {scrape_time}")
        else:
            logger.warning(f"Fréquence de scraping non reconnue: {scrape_frequency}")
        
        # Health check toutes les 5 minutes
        schedule.every(5).minutes.do(self.health_check)
        logger.info("Health check planifié: toutes les 5 minutes")
    
    def run(self):
        """Lance le scheduler"""
        logger.info("Démarrage du scheduler de scraping")
        
        # Authentification initiale
        if not self.authenticate():
            logger.error("Impossible de s'authentifier au démarrage")
            sys.exit(1)
        
        # Configuration des tâches
        self.setup_schedules()
        
        # Health check initial
        self.health_check()
        
        # Boucle principale
        logger.info("Scheduler en cours d'exécution...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # Vérifier toutes les 30 secondes
            except KeyboardInterrupt:
                logger.info("Arrêt du scheduler demandé")
                break
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {e}")
                time.sleep(60)  # Attendre 1 minute avant de reprendre

def main():
    """Point d'entrée principal"""
    scheduler = ScrapingScheduler()
    scheduler.run()

if __name__ == "__main__":
    main() 