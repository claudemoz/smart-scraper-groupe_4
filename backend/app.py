from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
from mysql.connector import Error
import jwt  # PyJWT
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import os
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import re
import threading
import subprocess
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    secret_key: str = os.getenv('SECRET_KEY', '00a741ee-239a-4993-bf19-8f25c5a6cd9d')
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_name: str = os.getenv('DB_NAME', 'paris_opendata')
    db_user: str = os.getenv('DB_USER', 'root')
    db_password: str = os.getenv('DB_PASSWORD', 'root')
    jwt_expiration_hours: int = 24
    allowed_origins: List[str] = None

    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost:5173',
                'http://127.0.0.1:5173'
            ]

class DatabaseManager:
    def __init__(self, config: APIConfig):
        self.config = config
    
    def get_connection(self):
        """Obtient une connexion à la base de données"""
        return mysql.connector.connect(
            host=self.config.db_host,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password
        )
    
    def execute_query(self, query: str, params: tuple = None, fetchall: bool = True):
        """Exécute une requête SQL de manière sécurisée"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetchall:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            
            connection.commit()
            return result
            
        except Error as e:
            logger.error(f"Erreur base de données: {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

class ScraperManager:
    def __init__(self):
        self.is_running = False
        self.last_run = None
        self.last_status = None
        self.last_error = None
    
    def run_scraper(self):
        """Lance le scraper dans un thread séparé"""
        if self.is_running:
            return False, "Le scraper est déjà en cours d'exécution"
        
        def scraper_thread():
            try:
                self.is_running = True
                self.last_run = datetime.now()
                self.last_status = "running"
                self.last_error = None
                
                # Déterminer le chemin de l'interpréteur Python
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Essayer d'utiliser l'interpréteur de l'environnement virtuel
                venv_python = os.path.join(script_dir, 'venv', 'Scripts', 'python.exe')
                if os.path.exists(venv_python):
                    python_executable = venv_python
                else:
                    # Fallback vers l'interpréteur système
                    python_executable = 'python'
                
                # Exécuter le scraper
                result = subprocess.run(
                    [python_executable, 'scraper.py'],
                    cwd=script_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    self.last_status = "success"
                    logger.info("Scraper exécuté avec succès")
                else:
                    self.last_status = "error"
                    self.last_error = result.stderr
                    logger.error(f"Erreur du scraper: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.last_status = "timeout"
                self.last_error = "Le scraper a dépassé le délai d'attente"
                logger.error("Timeout du scraper")
            except Exception as e:
                self.last_status = "error"
                self.last_error = str(e)
                logger.error(f"Erreur lors de l'exécution du scraper: {e}")
            finally:
                self.is_running = False
        
        thread = threading.Thread(target=scraper_thread)
        thread.daemon = True
        thread.start()
        
        return True, "Scraper démarré"
    
    def get_status(self):
        """Retourne le statut du scraper"""
        return {
            'is_running': self.is_running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'last_status': self.last_status,
            'last_error': self.last_error
        }

class AuthManager:
    def __init__(self, config: APIConfig):
        self.config = config
        self.secret_key = config.secret_key
    
    def generate_token(self, user_id: str) -> str:
        """Génère un token JWT"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=self.config.jwt_expiration_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expiré")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token invalide")
            return None

# Initialisation de l'application Flask
app = Flask(__name__)
config = APIConfig()
app.config['SECRET_KEY'] = config.secret_key

# Configuration CORS avancée
CORS(app, 
     origins=config.allowed_origins,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Configuration du limiteur de taux
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://"
)

# Initialisation des managers
db_manager = DatabaseManager(config)
auth_manager = AuthManager(config)
scraper_manager = ScraperManager()

def token_required(f):
    """Décorateur pour vérifier l'authentification JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token manquant', 'code': 'MISSING_TOKEN'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token invalide ou expiré', 'code': 'INVALID_TOKEN'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def validate_input(data: Dict, required_fields: List[str]) -> Optional[str]:
    """Valide les données d'entrée"""
    for field in required_fields:
        if field not in data or not data[field]:
            return f"Le champ '{field}' est requis"
    return None

def standardize_response(data=None, error=None, message=None, status_code=200):
    """Standardise les réponses de l'API"""
    response = {
        'success': error is None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
        if isinstance(error, dict) and 'code' not in error:
            response['error']['code'] = 'GENERIC_ERROR'
    
    return jsonify(response), status_code

# ==================== ENDPOINTS D'AUTHENTIFICATION ====================

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Endpoint d'authentification"""
    try:
        data = request.get_json()
        
        if not data:
            return standardize_response(
                error={'message': 'Données JSON requises', 'code': 'INVALID_JSON'},
                status_code=400
            )
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return standardize_response(
                error={'message': 'Username et password requis', 'code': 'MISSING_CREDENTIALS'},
                status_code=400
            )
        
        # Simulation d'une vérification (remplacer par une vraie logique)
        if username == 'admin' and password == 'admin123':
            token = auth_manager.generate_token(username)
            return standardize_response(
                data={
                    'token': token,
                    'user': {'username': username, 'role': 'admin'}
                },
                message='Connexion réussie'
            )
        
        return standardize_response(
            error={'message': 'Identifiants invalides', 'code': 'INVALID_CREDENTIALS'},
            status_code=401
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

# ==================== ENDPOINTS DE DONNÉES ====================

@app.route('/api/data', methods=['GET'])
@limiter.limit("50 per minute")
def get_data():
    """GET /api/data -> liste des données avec pagination et filtres"""
    try:
        # Paramètres de pagination
        page = max(1, int(request.args.get('page', 1)))
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = (page - 1) * limit
        
        # Paramètres de tri
        sort_by = request.args.get('sort_by', 'updated_at')
        sort_order = request.args.get('sort_order', 'DESC').upper()
        
        # Validation du tri
        allowed_sort_fields = ['nom_projet', 'arrondissement', 'date_debut', 'date_fin', 'budget', 'created_at', 'updated_at']
        if sort_by not in allowed_sort_fields:
            sort_by = 'updated_at'
        
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # Filtres de base
        filters = {}
        where_conditions = []
        params = []
        
        # Filtre par arrondissement
        if request.args.get('arrondissement'):
            filters['arrondissement'] = request.args.get('arrondissement')
            where_conditions.append("arrondissement = %s")
            params.append(filters['arrondissement'])
        
        # Filtre par état
        if request.args.get('etat'):
            filters['etat'] = request.args.get('etat')
            where_conditions.append("etat_avancement = %s")
            params.append(filters['etat'])
        
        # Filtre par catégorie
        if request.args.get('categorie'):
            filters['categorie'] = request.args.get('categorie')
            where_conditions.append("categorie = %s")
            params.append(filters['categorie'])
        
        # Recherche textuelle
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
            where_conditions.append("(nom_projet LIKE %s OR description LIKE %s OR adresse LIKE %s)")
            search_param = f"%{filters['search']}%"
            params.extend([search_param, search_param, search_param])
        
        # Filtre par date
        if request.args.get('date_debut'):
            try:
                date_debut = datetime.fromisoformat(request.args.get('date_debut').replace('Z', '+00:00'))
                filters['date_debut'] = date_debut
                where_conditions.append("date_debut >= %s")
                params.append(date_debut.date())
            except ValueError:
                return standardize_response(
                    error={'message': 'Format de date invalide pour date_debut', 'code': 'INVALID_DATE'},
                    status_code=400
                )
        
        if request.args.get('date_fin'):
            try:
                date_fin = datetime.fromisoformat(request.args.get('date_fin').replace('Z', '+00:00'))
                filters['date_fin'] = date_fin
                where_conditions.append("date_fin <= %s")
                params.append(date_fin.date())
            except ValueError:
                return standardize_response(
                    error={'message': 'Format de date invalide pour date_fin', 'code': 'INVALID_DATE'},
                    status_code=400
                )
        
        # Construction de la clause WHERE
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Requête principale
        query = f"""
            SELECT 
                id, record_id, nom_projet, description, categorie, sous_categorie,
                arrondissement, adresse, code_postal, latitude, longitude, 
                etat_avancement, date_debut, date_fin, budget, maitre_ouvrage,
                url_parisfr, url_photo, credit_photo, created_at, updated_at
            FROM paris_projects 
            {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        projects = db_manager.execute_query(query, tuple(params))
        
        # Requête pour le total
        count_query = f"SELECT COUNT(*) as total FROM paris_projects {where_clause}"
        count_params = params[:-2]  # Enlever limit et offset
        total_result = db_manager.execute_query(count_query, tuple(count_params), fetchall=False)
        total = total_result['total'] if total_result else 0
        
        # Formatage des résultats
        formatted_projects = []
        for project in projects:
            formatted_project = {
                'id': project['id'],
                'recordId': project['record_id'],
                'nomProjet': project['nom_projet'],
                'description': project['description'],
                'categorie': project['categorie'],
                'sousCategorie': project['sous_categorie'],
                'arrondissement': project['arrondissement'],
                'adresse': project['adresse'],
                'codePostal': project['code_postal'],
                'coordonnees': {
                    'latitude': float(project['latitude']) if project['latitude'] else None,
                    'longitude': float(project['longitude']) if project['longitude'] else None
                },
                'etatAvancement': project['etat_avancement'],
                'dateDebut': project['date_debut'].isoformat() if project['date_debut'] else None,
                'dateFin': project['date_fin'].isoformat() if project['date_fin'] else None,
                'budget': float(project['budget']) if project['budget'] else None,
                'maitreOuvrage': project['maitre_ouvrage'],
                'urlParisfr': project['url_parisfr'],
                'urlPhoto': project['url_photo'],
                'creditPhoto': project['credit_photo'],
                'createdAt': project['created_at'].isoformat() if project['created_at'] else None,
                'updatedAt': project['updated_at'].isoformat() if project['updated_at'] else None
            }
            formatted_projects.append(formatted_project)
        
        return standardize_response(
            data={
                'projects': formatted_projects,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if total > 0 else 0
                },
                'filters': filters,
                'sort': {
                    'by': sort_by,
                    'order': sort_order
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/data/<filter_type>', methods=['GET'])
@limiter.limit("60 per minute")
def get_filtered_data(filter_type):
    """GET /api/data/<filtre> -> filtrage spécialisé"""
    try:
        # Validation du type de filtre
        allowed_filters = ['arrondissement', 'categorie', 'etat', 'ville', 'date']
        if filter_type not in allowed_filters:
            return standardize_response(
                error={'message': f'Type de filtre non supporté: {filter_type}', 'code': 'INVALID_FILTER'},
                status_code=400
            )
        
        page = max(1, int(request.args.get('page', 1)))
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = (page - 1) * limit
        
        # Construction des requêtes selon le type de filtre
        if filter_type == 'arrondissement':
            value = request.args.get('value')
            if not value:
                return standardize_response(
                    error={'message': 'Paramètre "value" requis pour le filtre arrondissement', 'code': 'MISSING_VALUE'},
                    status_code=400
                )
            
            query = """
                SELECT * FROM paris_projects 
                WHERE arrondissement = %s 
                ORDER BY updated_at DESC 
                LIMIT %s OFFSET %s
            """
            params = (value, limit, offset)
            
            count_query = "SELECT COUNT(*) as total FROM paris_projects WHERE arrondissement = %s"
            count_params = (value,)
            
        elif filter_type == 'categorie':
            value = request.args.get('value')
            if not value:
                return standardize_response(
                    error={'message': 'Paramètre "value" requis pour le filtre catégorie', 'code': 'MISSING_VALUE'},
                    status_code=400
                )
            
            query = """
                SELECT * FROM paris_projects 
                WHERE categorie = %s 
                ORDER BY updated_at DESC 
                LIMIT %s OFFSET %s
            """
            params = (value, limit, offset)
            
            count_query = "SELECT COUNT(*) as total FROM paris_projects WHERE categorie = %s"
            count_params = (value,)
            
        elif filter_type == 'etat':
            value = request.args.get('value')
            if not value:
                return standardize_response(
                    error={'message': 'Paramètre "value" requis pour le filtre état', 'code': 'MISSING_VALUE'},
                    status_code=400
                )
            
            query = """
                SELECT * FROM paris_projects 
                WHERE etat_avancement = %s 
                ORDER BY updated_at DESC 
                LIMIT %s OFFSET %s
            """
            params = (value, limit, offset)
            
            count_query = "SELECT COUNT(*) as total FROM paris_projects WHERE etat_avancement = %s"
            count_params = (value,)
            
        elif filter_type == 'ville':
            # Filtre par ville (basé sur le code postal)
            value = request.args.get('value', 'Paris')  # Par défaut Paris
            
            if value.lower() == 'paris':
                query = """
                    SELECT * FROM paris_projects 
                    WHERE code_postal LIKE '75%' 
                    ORDER BY updated_at DESC 
                    LIMIT %s OFFSET %s
                """
                params = (limit, offset)
                
                count_query = "SELECT COUNT(*) as total FROM paris_projects WHERE code_postal LIKE '75%'"
                count_params = ()
            else:
                return standardize_response(
                    error={'message': 'Seule la ville de Paris est supportée actuellement', 'code': 'UNSUPPORTED_CITY'},
                    status_code=400
                )
                
        elif filter_type == 'date':
            # Filtre par période
            periode = request.args.get('periode', 'mois')  # mois, trimestre, annee
            
            if periode == 'mois':
                date_condition = "date_debut >= DATE_SUB(NOW(), INTERVAL 1 MONTH)"
            elif periode == 'trimestre':
                date_condition = "date_debut >= DATE_SUB(NOW(), INTERVAL 3 MONTH)"
            elif periode == 'annee':
                date_condition = "date_debut >= DATE_SUB(NOW(), INTERVAL 1 YEAR)"
            else:
                return standardize_response(
                    error={'message': 'Période non supportée. Utilisez: mois, trimestre, annee', 'code': 'INVALID_PERIOD'},
                    status_code=400
                )
            
            query = f"""
                SELECT * FROM paris_projects 
                WHERE {date_condition}
                ORDER BY date_debut DESC 
                LIMIT %s OFFSET %s
            """
            params = (limit, offset)
            
            count_query = f"SELECT COUNT(*) as total FROM paris_projects WHERE {date_condition}"
            count_params = ()
        
        # Exécution des requêtes
        projects = db_manager.execute_query(query, params)
        total_result = db_manager.execute_query(count_query, count_params, fetchall=False)
        total = total_result['total'] if total_result else 0
        
        # Formatage des résultats (même format que get_data)
        formatted_projects = []
        for project in projects:
            formatted_project = {
                'id': project['id'],
                'recordId': project['record_id'],
                'nomProjet': project['nom_projet'],
                'description': project['description'],
                'categorie': project['categorie'],
                'sousCategorie': project['sous_categorie'],
                'arrondissement': project['arrondissement'],
                'adresse': project['adresse'],
                'codePostal': project['code_postal'],
                'coordonnees': {
                    'latitude': float(project['latitude']) if project['latitude'] else None,
                    'longitude': float(project['longitude']) if project['longitude'] else None
                },
                'etatAvancement': project['etat_avancement'],
                'dateDebut': project['date_debut'].isoformat() if project['date_debut'] else None,
                'dateFin': project['date_fin'].isoformat() if project['date_fin'] else None,
                'budget': float(project['budget']) if project['budget'] else None,
                'maitreOuvrage': project['maitre_ouvrage'],
                'urlParisfr': project['url_parisfr'],
                'urlPhoto': project['url_photo'],
                'creditPhoto': project['credit_photo'],
                'createdAt': project['created_at'].isoformat() if project['created_at'] else None,
                'updatedAt': project['updated_at'].isoformat() if project['updated_at'] else None
            }
            formatted_projects.append(formatted_project)
        
        return standardize_response(
            data={
                'projects': formatted_projects,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if total > 0 else 0
                },
                'filter': {
                    'type': filter_type,
                    'value': request.args.get('value') if filter_type != 'date' else request.args.get('periode', 'mois')
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du filtrage des données ({filter_type}): {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

# ==================== ENDPOINT SCRAPER ====================

@app.route('/api/scrape', methods=['POST'])
@token_required
@limiter.limit("10 per hour")
def trigger_scrape():
    """POST /api/scrape -> déclenchement du scraper"""
    try:
        success, message = scraper_manager.run_scraper()
        
        if success:
            return standardize_response(
                data=scraper_manager.get_status(),
                message=message
            )
        else:
            return standardize_response(
                error={'message': message, 'code': 'SCRAPER_BUSY'},
                status_code=409
            )
            
    except Exception as e:
        logger.error(f"Erreur lors du déclenchement du scraper: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/scrape/status', methods=['GET'])
@limiter.limit("30 per minute")
def get_scrape_status():
    """GET /api/scrape/status -> statut du scraper"""
    try:
        return standardize_response(
            data=scraper_manager.get_status()
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut du scraper: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/scrape/reset-limits', methods=['POST'])
@token_required
def reset_scraper_limits():
    """POST /api/scrape/reset-limits -> réinitialise les limites de taux (développement uniquement)"""
    try:
        # Réinitialiser les limites pour l'IP actuelle
        limiter.reset()
        return standardize_response(
            message="Limites de taux réinitialisées avec succès"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation des limites: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

# ==================== AUTRES ENDPOINTS ====================

@app.route('/api/projects', methods=['GET'])
@limiter.limit("30 per minute")
def get_projects():
    """Récupère la liste des projets (alias pour /api/data)"""
    return get_data()

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@limiter.limit("60 per minute")
def get_project(project_id):
    """Récupère un projet spécifique"""
    try:
        query = """
            SELECT 
                id, record_id, nom_projet, description, categorie, sous_categorie,
                arrondissement, adresse, code_postal, latitude, longitude, 
                etat_avancement, date_debut, date_fin, budget, maitre_ouvrage,
                url_parisfr, url_photo, credit_photo, created_at, updated_at
            FROM paris_projects 
            WHERE id = %s
        """
        
        project = db_manager.execute_query(query, (project_id,), fetchall=False)
        
        if not project:
            return standardize_response(
                error={'message': 'Projet non trouvé', 'code': 'PROJECT_NOT_FOUND'},
                status_code=404
            )
        
        formatted_project = {
            'id': project['id'],
            'recordId': project['record_id'],
            'nomProjet': project['nom_projet'],
            'description': project['description'],
            'categorie': project['categorie'],
            'sousCategorie': project['sous_categorie'],
            'arrondissement': project['arrondissement'],
            'adresse': project['adresse'],
            'codePostal': project['code_postal'],
            'coordonnees': {
                'latitude': float(project['latitude']) if project['latitude'] else None,
                'longitude': float(project['longitude']) if project['longitude'] else None
            },
            'etatAvancement': project['etat_avancement'],
            'dateDebut': project['date_debut'].isoformat() if project['date_debut'] else None,
            'dateFin': project['date_fin'].isoformat() if project['date_fin'] else None,
            'budget': float(project['budget']) if project['budget'] else None,
            'maitreOuvrage': project['maitre_ouvrage'],
            'urlParisfr': project['url_parisfr'],
            'urlPhoto': project['url_photo'],
            'creditPhoto': project['credit_photo'],
            'createdAt': project['created_at'].isoformat() if project['created_at'] else None,
            'updatedAt': project['updated_at'].isoformat() if project['updated_at'] else None
        }
        
        return standardize_response(data={'project': formatted_project})
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du projet {project_id}: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/statistics', methods=['GET'])
@limiter.limit("20 per minute")
def get_statistics():
    """Récupère les statistiques générales"""
    try:
        # Statistiques générales
        stats_query = """
            SELECT 
                COUNT(*) as total_projects,
                COUNT(DISTINCT arrondissement) as total_arrondissements,
                COUNT(DISTINCT etat_avancement) as total_etats,
                COUNT(DISTINCT categorie) as total_categories,
                AVG(budget) as budget_moyen,
                SUM(budget) as budget_total,
                MIN(date_debut) as date_debut_min,
                MAX(date_fin) as date_fin_max
            FROM paris_projects
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        
        stats = db_manager.execute_query(stats_query, fetchall=False)
        
        # Répartition par arrondissement
        arron_query = """
            SELECT arrondissement, COUNT(*) as count, AVG(budget) as budget_moyen
            FROM paris_projects 
            WHERE arrondissement IS NOT NULL
            GROUP BY arrondissement
            ORDER BY count DESC
            LIMIT 20
        """
        
        arrondissements = db_manager.execute_query(arron_query)
        
        # Répartition par catégorie
        cat_query = """
            SELECT categorie, COUNT(*) as count, AVG(budget) as budget_moyen
            FROM paris_projects 
            WHERE categorie IS NOT NULL
            GROUP BY categorie
            ORDER BY count DESC
            LIMIT 20
        """
        
        categories = db_manager.execute_query(cat_query)
        
        # Répartition par état
        etat_query = """
            SELECT etat_avancement, COUNT(*) as count
            FROM paris_projects 
            WHERE etat_avancement IS NOT NULL
            GROUP BY etat_avancement
            ORDER BY count DESC
        """
        
        etats = db_manager.execute_query(etat_query)
        
        # Évolution par mois (derniers 12 mois)
        evolution_query = """
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as mois,
                COUNT(*) as count
            FROM paris_projects 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY mois DESC
        """
        
        evolution = db_manager.execute_query(evolution_query)
        
        return standardize_response(
            data={
                'general': {
                    'totalProjects': stats['total_projects'],
                    'totalArrondissements': stats['total_arrondissements'],
                    'totalEtats': stats['total_etats'],
                    'totalCategories': stats['total_categories'],
                    'budgetMoyen': float(stats['budget_moyen']) if stats['budget_moyen'] else 0,
                    'budgetTotal': float(stats['budget_total']) if stats['budget_total'] else 0,
                    'dateDebutMin': stats['date_debut_min'].isoformat() if stats['date_debut_min'] else None,
                    'dateFinMax': stats['date_fin_max'].isoformat() if stats['date_fin_max'] else None
                },
                'arrondissements': [
                    {
                        'arrondissement': item['arrondissement'], 
                        'count': item['count'],
                        'budgetMoyen': float(item['budget_moyen']) if item['budget_moyen'] else 0
                    }
                    for item in arrondissements
                ],
                'categories': [
                    {
                        'categorie': item['categorie'], 
                        'count': item['count'],
                        'budgetMoyen': float(item['budget_moyen']) if item['budget_moyen'] else 0
                    }
                    for item in categories
                ],
                'etats': [
                    {'etat': item['etat_avancement'], 'count': item['count']}
                    for item in etats
                ],
                'evolution': [
                    {'mois': item['mois'], 'count': item['count']}
                    for item in evolution
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé"""
    try:
        # Test de connexion à la base de données
        db_result = db_manager.execute_query("SELECT COUNT(*) as count FROM paris_projects", fetchall=False)
        
        return standardize_response(
            data={
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': {
                    'status': 'connected',
                    'projects_count': db_result['count'] if db_result else 0
                },
                'scraper': scraper_manager.get_status(),
                'version': '1.0.0'
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return standardize_response(
            error={
                'message': 'Service non disponible',
                'code': 'SERVICE_UNAVAILABLE',
                'details': str(e)
            },
            status_code=503
        )

@app.route('/api/metadata', methods=['GET'])
@limiter.limit("10 per minute")
def get_metadata():
    """Récupère les métadonnées de l'API (valeurs possibles pour les filtres)"""
    try:
        # Récupérer les valeurs uniques pour les filtres
        arrondissements_query = """
            SELECT DISTINCT arrondissement 
            FROM paris_projects 
            WHERE arrondissement IS NOT NULL 
            ORDER BY arrondissement
        """
        
        categories_query = """
            SELECT DISTINCT categorie 
            FROM paris_projects 
            WHERE categorie IS NOT NULL 
            ORDER BY categorie
        """
        
        etats_query = """
            SELECT DISTINCT etat_avancement 
            FROM paris_projects 
            WHERE etat_avancement IS NOT NULL 
            ORDER BY etat_avancement
        """
        
        arrondissements = [item['arrondissement'] for item in db_manager.execute_query(arrondissements_query)]
        categories = [item['categorie'] for item in db_manager.execute_query(categories_query)]
        etats = [item['etat_avancement'] for item in db_manager.execute_query(etats_query)]
        
        return standardize_response(
            data={
                'filters': {
                    'arrondissements': arrondissements,
                    'categories': categories,
                    'etats': etats
                },
                'sort_fields': ['nom_projet', 'arrondissement', 'date_debut', 'date_fin', 'budget', 'created_at', 'updated_at'],
                'endpoints': {
                    'data': '/api/data',
                    'filtered_data': '/api/data/<filter_type>',
                    'projects': '/api/projects',
                    'project_detail': '/api/projects/<id>',
                    'statistics': '/api/statistics',
                    'scrape': '/api/scrape',
                    'scrape_status': '/api/scrape/status',
                    'scheduler_status': '/api/scheduler/status',
                    'scheduler_config': '/api/scheduler/config',
                    'scheduler_logs': '/api/scheduler/logs',
                    'health': '/api/health',
                    'auth': '/api/auth/login'
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métadonnées: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

# ==================== ENDPOINTS SCHEDULER ====================

@app.route('/api/scheduler/status', methods=['GET'])
@limiter.limit("20 per minute")
def get_scheduler_status():
    """GET /api/scheduler/status -> statut du scheduler"""
    try:
        # Informations sur la configuration du scheduler
        # Ces variables sont définies dans le conteneur scheduler, pas backend
        # Donc on utilise des valeurs par défaut
        scheduler_config = {
            'frequency': 'daily',  # Valeur par défaut
            'time': '02:00',       # Valeur par défaut
            'day': 'monday',       # Valeur par défaut
            'enabled': True
        }
        
        # Essayer de lire le log du scheduler
        scheduler_log_path = os.path.join(os.path.dirname(__file__), 'scheduler.log')
        last_entries = []
        
        try:
            if os.path.exists(scheduler_log_path):
                with open(scheduler_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Prendre les 10 dernières lignes
                    last_entries = [line.strip() for line in lines[-10:] if line.strip()]
            else:
                # Si le fichier n'existe pas, c'est que le scheduler n'a pas encore démarré
                last_entries = ["Scheduler en cours de démarrage..."]
        except Exception as e:
            logger.warning(f"Impossible de lire le log du scheduler: {e}")
            last_entries = ["Impossible de lire les logs du scheduler"]
        
        # Vérifier si le service scheduler est accessible
        scheduler_status = "unknown"
        try:
            import requests
            # Tenter une requête vers le conteneur scheduler (si accessible)
            # Pour l'instant, on suppose qu'il est actif si le log existe
            if os.path.exists(scheduler_log_path):
                scheduler_status = "running"
            else:
                scheduler_status = "starting"
        except Exception:
            scheduler_status = "unknown"
        
        return standardize_response(
            data={
                'config': scheduler_config,
                'last_log_entries': last_entries,
                'log_file': scheduler_log_path,
                'status': scheduler_status,
                'message': 'Configuration par défaut - Le scheduler fonctionne de manière autonome'
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut du scheduler: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/scheduler/config', methods=['GET'])
@token_required
@limiter.limit("10 per minute")
def get_scheduler_config():
    """GET /api/scheduler/config -> configuration du scheduler"""
    try:
        config = {
            'frequency': os.getenv('SCRAPE_FREQUENCY', 'daily'),
            'time': os.getenv('SCRAPE_TIME', '02:00'),
            'day': os.getenv('SCRAPE_DAY', 'monday'),
            'frequencies': ['hourly', 'daily', 'weekly'],
            'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        }
        
        return standardize_response(data=config)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la configuration du scheduler: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

@app.route('/api/scheduler/logs', methods=['GET'])
@token_required
@limiter.limit("10 per minute")
def get_scheduler_logs():
    """GET /api/scheduler/logs -> logs du scheduler"""
    try:
        lines = int(request.args.get('lines', 50))
        lines = min(max(lines, 1), 500)  # Limiter entre 1 et 500 lignes
        
        scheduler_log_path = os.path.join(os.path.dirname(__file__), 'scheduler.log')
        log_entries = []
        
        if os.path.exists(scheduler_log_path):
            with open(scheduler_log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                # Prendre les N dernières lignes
                selected_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in selected_lines:
                    if line.strip():
                        log_entries.append({
                            'timestamp': line.split(' - ')[0] if ' - ' in line else '',
                            'message': line.strip()
                        })
        
        return standardize_response(
            data={
                'logs': log_entries,
                'total_lines': len(log_entries),
                'file_path': scheduler_log_path
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs du scheduler: {e}")
        return standardize_response(
            error={'message': 'Erreur serveur', 'code': 'SERVER_ERROR'},
            status_code=500
        )

# ==================== GESTIONNAIRES D'ERREURS GLOBAUX ====================

@app.errorhandler(400)
def bad_request(error):
    """Gestionnaire d'erreur 400 - Bad Request"""
    return standardize_response(
        error={'message': 'Requête invalide', 'code': 'BAD_REQUEST'},
        status_code=400
    )

@app.errorhandler(401)
def unauthorized(error):
    """Gestionnaire d'erreur 401 - Unauthorized"""
    return standardize_response(
        error={'message': 'Non autorisé', 'code': 'UNAUTHORIZED'},
        status_code=401
    )

@app.errorhandler(403)
def forbidden(error):
    """Gestionnaire d'erreur 403 - Forbidden"""
    return standardize_response(
        error={'message': 'Accès interdit', 'code': 'FORBIDDEN'},
        status_code=403
    )

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404 - Not Found"""
    return standardize_response(
        error={'message': 'Ressource non trouvée', 'code': 'NOT_FOUND'},
        status_code=404
    )

@app.errorhandler(405)
def method_not_allowed(error):
    """Gestionnaire d'erreur 405 - Method Not Allowed"""
    return standardize_response(
        error={'message': 'Méthode non autorisée', 'code': 'METHOD_NOT_ALLOWED'},
        status_code=405
    )

@app.errorhandler(429)
def ratelimit_handler(e):
    """Gestionnaire d'erreur 429 - Too Many Requests"""
    return standardize_response(
        error={
            'message': 'Trop de requêtes, veuillez réessayer plus tard',
            'code': 'RATE_LIMIT_EXCEEDED',
            'retry_after': getattr(e, 'retry_after', None)
        },
        status_code=429
    )

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500 - Internal Server Error"""
    logger.error(f"Erreur interne du serveur: {error}")
    return standardize_response(
        error={'message': 'Erreur interne du serveur', 'code': 'INTERNAL_SERVER_ERROR'},
        status_code=500
    )

@app.errorhandler(503)
def service_unavailable(error):
    """Gestionnaire d'erreur 503 - Service Unavailable"""
    return standardize_response(
        error={'message': 'Service temporairement indisponible', 'code': 'SERVICE_UNAVAILABLE'},
        status_code=503
    )

# ==================== MIDDLEWARE ET HOOKS ====================

@app.before_request
def before_request():
    """Middleware exécuté avant chaque requête"""
    # Log des requêtes
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    # Validation des headers Content-Type pour les requêtes POST/PUT
    if request.method in ['POST', 'PUT'] and request.content_type:
        if not request.content_type.startswith('application/json'):
            return standardize_response(
                error={'message': 'Content-Type doit être application/json', 'code': 'INVALID_CONTENT_TYPE'},
                status_code=400
            )

@app.after_request
def after_request(response):
    """Middleware exécuté après chaque requête"""
    # Headers de sécurité
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Headers CORS supplémentaires si nécessaire
    if request.origin in config.allowed_origins:
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

# ==================== DÉMARRAGE DE L'APPLICATION ====================

if __name__ == '__main__':
    # Vérification de la configuration
    if config.secret_key == '00a741ee-239a-4993-bf19-8f25c5a6cd9d':
    
      logger.info("Démarrage de l'API REST Paris OpenData")
      logger.info(f"Base de données: {config.db_host}:{config.db_name}")
      logger.info(f"CORS autorisé pour: {', '.join(config.allowed_origins)}")
    
    # Test de connexion à la base de données au démarrage
    try:
        db_manager.execute_query("SELECT 1", fetchall=False)
        logger.info("Connexion à la base de données réussie")
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        logger.error("L'application va démarrer mais certaines fonctionnalités peuvent ne pas fonctionner")
    
    # Démarrage du serveur
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        threaded=True
    )
