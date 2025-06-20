import requests
import mysql.connector
from mysql.connector import Error
import json
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional
import os
from dataclasses import dataclass
import hashlib

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collector.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    database: str = 'paris_opendata'
    user: str = 'root'
    password: str = 'root'

class ParisOpenDataCollector:
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Paris-OpenData-Collector/1.0',
            'Accept': 'application/json'
        })
    
    def drop_existing_table(self):
        """Supprime la table existante si elle existe pour éviter les conflits de schéma"""
        try:
            connection = mysql.connector.connect(**self.db_config.__dict__)
            cursor = connection.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS paris_projects")
            cursor.execute("DROP TABLE IF EXISTS collection_logs")
            
            connection.commit()
            logging.info("Tables existantes supprimées")
            
        except Error as e:
            logging.error(f"Erreur lors de la suppression des tables: {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def create_database_schema(self):
        """Crée les tables nécessaires dans la base de données"""
        try:
            connection = mysql.connector.connect(**self.db_config.__dict__)
            cursor = connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paris_projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    record_id VARCHAR(255) UNIQUE,
                    nom_projet TEXT,
                    description TEXT,
                    categorie VARCHAR(255),
                    sous_categorie VARCHAR(255),
                    arrondissement VARCHAR(50),
                    adresse TEXT,
                    code_postal VARCHAR(10),
                    coordonnees_geo POINT NOT NULL,
                    latitude DECIMAL(10, 8) NOT NULL,
                    longitude DECIMAL(11, 8) NOT NULL,
                    etat_avancement VARCHAR(100),
                    date_debut DATE,
                    date_fin DATE,
                    budget DECIMAL(15, 2),
                    maitre_ouvrage VARCHAR(255),
                    url_parisfr TEXT,
                    url_photo TEXT,
                    credit_photo VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_arrondissement (arrondissement),
                    INDEX idx_code_postal (code_postal),
                    INDEX idx_categorie (categorie),
                    INDEX idx_sous_categorie (sous_categorie),
                    INDEX idx_etat (etat_avancement),
                    INDEX idx_lat_lng (latitude, longitude),
                    SPATIAL INDEX idx_geo (coordonnees_geo)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    dataset_name VARCHAR(255),
                    records_collected INT,
                    collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('success', 'error', 'partial'),
                    error_message TEXT
                )
            """)
            
            connection.commit()
            logging.info("Schéma de base de données créé avec succès")
            
        except Error as e:
            logging.error(f"Erreur lors de la création du schéma: {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def fetch_paris_projects(self, limit: int = 100, offset: int = 0) -> Dict:
        """Récupère les données des projets Paris se transforme"""
        url = f"{self.base_url}/parissetransforme/records"
        params = {
            'limit': limit,
            'offset': offset,
            'timezone': 'Europe/Paris'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur lors de la récupération des données: {e}")
            raise
    
    def process_project_record(self, record: Dict) -> Dict:
        """Traite un enregistrement de projet pour l'insertion en base"""
        
        # Extraction des coordonnées géographiques
        geo_point = record.get('geo_point_2d')
        latitude = longitude = None
        if geo_point and isinstance(geo_point, dict):
            latitude = geo_point.get('lat')
            longitude = geo_point.get('lon')
        
        # Traitement des dates
        date_debut = self.parse_date(record.get('date_debut'))
        date_fin = self.parse_date(record.get('date_fin'))
        
        # Nettoyage du budget
        budget = None
        if record.get('budget'):
            try:
                budget = float(str(record['budget']).replace('€', '').replace(',', '.').strip())
            except (ValueError, AttributeError):
                pass
        
        # Extraction de l'arrondissement depuis le code postal
        arrondissement = None
        code_postal = record.get('code_postal')
        if code_postal and code_postal.startswith('750'):
            try:
                arr_num = int(code_postal[-2:])
                if 1 <= arr_num <= 20:
                    arrondissement = f"{arr_num}e arrondissement"
            except (ValueError, TypeError):
                pass
        
        # Génération d'un record_id unique basé sur le titre et l'adresse
        record_id = None
        titre = record.get('titre_descriptif', '')
        adresse = record.get('adresse', '')
        if titre or adresse:
            unique_string = f"{titre}_{adresse}_{code_postal}"
            record_id = hashlib.md5(unique_string.encode()).hexdigest()
        
        return {
            'record_id': record_id,
            'nom_projet': record.get('titre_descriptif'),
            'description': record.get('corps_descriptif'),
            'categorie': record.get('categorie'),
            'sous_categorie': record.get('sous_categorie'),
            'arrondissement': arrondissement,
            'adresse': record.get('adresse'),
            'code_postal': record.get('code_postal'),
            'latitude': latitude,
            'longitude': longitude,
            'etat_avancement': record.get('sous_categorie'),
            'date_debut': date_debut,
            'date_fin': self.parse_date(record.get('date_liv')),
            'budget': budget,
            'maitre_ouvrage': record.get('categorie'),
            'url_parisfr': record.get('url_parisfr'),
            'url_photo': record.get('url_pj'),
            'credit_photo': record.get('credit_photo')
        }
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse une date depuis différents formats"""
        if not date_str:
            return None
        
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S%z']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.split('T')[0], fmt.split('T')[0])
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        logging.warning(f"Format de date non reconnu: {date_str}")
        return None
    
    def insert_projects(self, projects: List[Dict]) -> int:
        """Insert les projets dans la base de données"""
        if not projects:
            return 0
        
        try:
            connection = mysql.connector.connect(**self.db_config.__dict__)
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO paris_projects 
                (record_id, nom_projet, description, categorie, sous_categorie, arrondissement, adresse, 
                 code_postal, latitude, longitude, etat_avancement, date_debut, date_fin, 
                 budget, maitre_ouvrage, url_parisfr, url_photo, credit_photo, coordonnees_geo)
                VALUES (%(record_id)s, %(nom_projet)s, %(description)s, %(categorie)s, %(sous_categorie)s, 
                        %(arrondissement)s, %(adresse)s, %(code_postal)s, %(latitude)s, %(longitude)s, 
                        %(etat_avancement)s, %(date_debut)s, %(date_fin)s, %(budget)s, %(maitre_ouvrage)s, 
                        %(url_parisfr)s, %(url_photo)s, %(credit_photo)s, POINT(%(longitude)s, %(latitude)s))
                ON DUPLICATE KEY UPDATE
                nom_projet = VALUES(nom_projet),
                description = VALUES(description),
                categorie = VALUES(categorie),
                sous_categorie = VALUES(sous_categorie),
                arrondissement = VALUES(arrondissement),
                adresse = VALUES(adresse),
                code_postal = VALUES(code_postal),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                etat_avancement = VALUES(etat_avancement),
                date_debut = VALUES(date_debut),
                date_fin = VALUES(date_fin),
                budget = VALUES(budget),
                maitre_ouvrage = VALUES(maitre_ouvrage),
                url_parisfr = VALUES(url_parisfr),
                url_photo = VALUES(url_photo),
                credit_photo = VALUES(credit_photo),
                coordonnees_geo = VALUES(coordonnees_geo),
                updated_at = CURRENT_TIMESTAMP
            """
            
            # Préparer les données pour l'insertion
            insert_data = []
            for project in projects:
                # Créer une copie pour éviter les modifications sur l'original
                data = project.copy()
                # Vérifier que les coordonnées sont valides
                if data['latitude'] is None or data['longitude'] is None:
                    logging.warning(f"Projet {data.get('record_id', 'unknown')} ignoré: coordonnées manquantes")
                    continue
                # Vérifier que les coordonnées sont dans des plages valides
                if not (-90 <= data['latitude'] <= 90) or not (-180 <= data['longitude'] <= 180):
                    logging.warning(f"Projet {data.get('record_id', 'unknown')} ignoré: coordonnées invalides ({data['latitude']}, {data['longitude']})")
                    continue
                insert_data.append(data)
            
            cursor.executemany(insert_query, insert_data)
            connection.commit()
            
            inserted_count = cursor.rowcount
            logging.info(f"{inserted_count} projets traités dans la base de données")
            
            return inserted_count
            
        except Error as e:
            logging.error(f"Erreur lors de l'insertion: {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def log_collection(self, dataset_name: str, records_count: int, 
                      status: str, error_message: str = None):
        """Enregistre le résultat d'une collecte"""
        try:
            connection = mysql.connector.connect(**self.db_config.__dict__)
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO collection_logs 
                (dataset_name, records_collected, status, error_message)
                VALUES (%s, %s, %s, %s)
            """, (dataset_name, records_count, status, error_message))
            
            connection.commit()
            
        except Error as e:
            logging.error(f"Erreur lors de l'enregistrement du log: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def collect_all_data(self):
        """Collecte toutes les données disponibles avec pagination"""
        logging.info("Début de la collecte des données Paris se transforme")
        
        try:
            offset = 0
            limit = 100
            total_collected = 0
            
            while True:
                logging.info(f"Récupération des enregistrements {offset} à {offset + limit}")
                
                response_data = self.fetch_paris_projects(limit=limit, offset=offset)
                records = response_data.get('results', [])
                
                if not records:
                    logging.info("Aucun enregistrement supplémentaire trouvé")
                    break
                
                # Traitement des enregistrements
                processed_projects = []
                for record in records:
                    try:
                        processed_project = self.process_project_record(record)
                        processed_projects.append(processed_project)
                    except Exception as e:
                        logging.warning(f"Erreur lors du traitement de l'enregistrement {record.get('record_id', 'unknown')}: {e}")
                
                # Insertion en base
                if processed_projects:
                    inserted = self.insert_projects(processed_projects)
                    total_collected += len(processed_projects)
                
                # Vérification s'il y a plus de données
                total_count = response_data.get('total_count', 0)
                if offset + limit >= total_count:
                    break
                
                offset += limit
                time.sleep(1)  # Pause pour ne pas surcharger l'API
            
            self.log_collection('parissetransforme', total_collected, 'success')
            logging.info(f"Collecte terminée avec succès. {total_collected} projets collectés")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Erreur lors de la collecte: {error_msg}")
            self.log_collection('parissetransforme', total_collected, 'error', error_msg)
            raise

def main():
    """Fonction principale"""
    # Configuration de la base de données
    db_config = DatabaseConfig(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'paris_opendata'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root')
    )
    
    # Initialisation du collecteur
    collector = ParisOpenDataCollector(db_config)
    
    try:
        # Suppression des tables existantes
        collector.drop_existing_table()
        
        # Création du schéma de base de données
        collector.create_database_schema()
        
        # Collecte des données
        collector.collect_all_data()
        
        logging.info("Processus de collecte terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())