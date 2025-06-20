#!/usr/bin/env python3
"""
Script de test pour l'API REST Paris OpenData
Teste tous les endpoints principaux et vérifie leur bon fonctionnement
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, details=""):
        """Enregistre le résultat d'un test"""
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_health_check(self):
        """Test de l'endpoint de santé"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('status') == 'healthy':
                    self.log_test("Health Check", True, f"Status: {data['data']['status']}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test de l'authentification"""
        try:
            # Test avec des identifiants valides
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'token' in data.get('data', {}):
                    self.token = data['data']['token']
                    self.log_test("Authentication - Valid Credentials", True, "Token obtained")
                    
                    # Test avec des identifiants invalides
                    invalid_login = {
                        "username": "invalid",
                        "password": "invalid"
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json=invalid_login,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 401:
                        self.log_test("Authentication - Invalid Credentials", True, "Correctly rejected")
                        return True
                    else:
                        self.log_test("Authentication - Invalid Credentials", False, f"Expected 401, got {response.status_code}")
                        return False
                else:
                    self.log_test("Authentication - Valid Credentials", False, f"No token in response: {data}")
                    return False
            else:
                self.log_test("Authentication - Valid Credentials", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_data_endpoints(self):
        """Test des endpoints de données"""
        success_count = 0
        total_tests = 0
        
        # Test GET /api/data
        try:
            total_tests += 1
            response = self.session.get(f"{self.base_url}/data")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'projects' in data.get('data', {}):
                    projects_count = len(data['data']['projects'])
                    self.log_test("GET /api/data", True, f"Retrieved {projects_count} projects")
                    success_count += 1
                else:
                    self.log_test("GET /api/data", False, f"Unexpected response structure: {data}")
            else:
                self.log_test("GET /api/data", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/data", False, f"Exception: {str(e)}")
        
        # Test GET /api/data avec paramètres
        try:
            total_tests += 1
            params = {
                'page': 1,
                'limit': 5,
                'sort_by': 'nom_projet',
                'sort_order': 'ASC'
            }
            
            response = self.session.get(f"{self.base_url}/data", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pagination = data.get('data', {}).get('pagination', {})
                    if pagination.get('limit') == 5:
                        self.log_test("GET /api/data with params", True, f"Pagination working: limit={pagination.get('limit')}")
                        success_count += 1
                    else:
                        self.log_test("GET /api/data with params", False, f"Pagination not working correctly")
                else:
                    self.log_test("GET /api/data with params", False, f"Request failed: {data}")
            else:
                self.log_test("GET /api/data with params", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/data with params", False, f"Exception: {str(e)}")
        
        # Test GET /api/data/arrondissement
        try:
            total_tests += 1
            params = {'value': '13e arrondissement'}
            response = self.session.get(f"{self.base_url}/data/arrondissement", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    filter_info = data.get('data', {}).get('filter', {})
                    if filter_info.get('type') == 'arrondissement':
                        self.log_test("GET /api/data/arrondissement", True, f"Filter applied: {filter_info}")
                        success_count += 1
                    else:
                        self.log_test("GET /api/data/arrondissement", False, f"Filter not applied correctly")
                else:
                    self.log_test("GET /api/data/arrondissement", False, f"Request failed: {data}")
            else:
                self.log_test("GET /api/data/arrondissement", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/data/arrondissement", False, f"Exception: {str(e)}")
        
        return success_count == total_tests
    
    def test_statistics_endpoint(self):
        """Test de l'endpoint des statistiques"""
        try:
            response = self.session.get(f"{self.base_url}/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'general' in data.get('data', {}):
                    general_stats = data['data']['general']
                    total_projects = general_stats.get('totalProjects', 0)
                    self.log_test("GET /api/statistics", True, f"Total projects: {total_projects}")
                    return True
                else:
                    self.log_test("GET /api/statistics", False, f"Unexpected response structure: {data}")
                    return False
            else:
                self.log_test("GET /api/statistics", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/statistics", False, f"Exception: {str(e)}")
            return False
    
    def test_metadata_endpoint(self):
        """Test de l'endpoint des métadonnées"""
        try:
            response = self.session.get(f"{self.base_url}/metadata")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'filters' in data.get('data', {}):
                    filters = data['data']['filters']
                    arrondissements_count = len(filters.get('arrondissements', []))
                    self.log_test("GET /api/metadata", True, f"Found {arrondissements_count} arrondissements")
                    return True
                else:
                    self.log_test("GET /api/metadata", False, f"Unexpected response structure: {data}")
                    return False
            else:
                self.log_test("GET /api/metadata", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/metadata", False, f"Exception: {str(e)}")
            return False
    
    def test_scraper_endpoints(self):
        """Test des endpoints du scraper (nécessite authentification)"""
        if not self.token:
            self.log_test("Scraper Tests", False, "No authentication token available")
            return False
        
        success_count = 0
        total_tests = 0
        
        # Test GET /api/scrape/status
        try:
            total_tests += 1
            response = self.session.get(f"{self.base_url}/scrape/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'is_running' in data.get('data', {}):
                    is_running = data['data']['is_running']
                    self.log_test("GET /api/scrape/status", True, f"Scraper running: {is_running}")
                    success_count += 1
                else:
                    self.log_test("GET /api/scrape/status", False, f"Unexpected response: {data}")
            else:
                self.log_test("GET /api/scrape/status", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/scrape/status", False, f"Exception: {str(e)}")
        
        # Test POST /api/scrape (avec authentification)
        try:
            total_tests += 1
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.base_url}/scrape",
                headers=headers
            )
            
            if response.status_code in [200, 409]:  # 409 si déjà en cours
                data = response.json()
                if response.status_code == 200:
                    self.log_test("POST /api/scrape", True, "Scraper started successfully")
                    success_count += 1
                elif response.status_code == 409:
                    self.log_test("POST /api/scrape", True, "Scraper already running (expected)")
                    success_count += 1
            else:
                self.log_test("POST /api/scrape", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/scrape", False, f"Exception: {str(e)}")
        
        return success_count == total_tests
    
    def test_error_handling(self):
        """Test de la gestion d'erreurs"""
        success_count = 0
        total_tests = 0
        
        # Test 404
        try:
            total_tests += 1
            response = self.session.get(f"{self.base_url}/nonexistent")
            
            if response.status_code == 404:
                data = response.json()
                if not data.get('success') and data.get('error', {}).get('code') == 'NOT_FOUND':
                    self.log_test("404 Error Handling", True, "Correct error response")
                    success_count += 1
                else:
                    self.log_test("404 Error Handling", False, f"Incorrect error format: {data}")
            else:
                self.log_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Exception: {str(e)}")
        
        # Test 401 (sans token)
        try:
            total_tests += 1
            headers = {'Content-Type': 'application/json'}
            response = self.session.post(f"{self.base_url}/scrape", headers=headers)
            
            if response.status_code == 401:
                data = response.json()
                if not data.get('success') and 'MISSING_TOKEN' in data.get('error', {}).get('code', ''):
                    self.log_test("401 Error Handling", True, "Correct authentication error")
                    success_count += 1
                else:
                    self.log_test("401 Error Handling", False, f"Incorrect error format: {data}")
            else:
                self.log_test("401 Error Handling", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("401 Error Handling", False, f"Exception: {str(e)}")
        
        return success_count == total_tests
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🧪 Démarrage des tests de l'API REST Paris OpenData")
        print("=" * 60)
        
        start_time = time.time()
        
        # Tests de base
        health_ok = self.test_health_check()
        auth_ok = self.test_authentication()
        
        if not health_ok:
            print("\n❌ Les tests de santé ont échoué. Vérifiez que l'API est démarrée.")
            return False
        
        # Tests des endpoints
        data_ok = self.test_data_endpoints()
        stats_ok = self.test_statistics_endpoint()
        metadata_ok = self.test_metadata_endpoint()
        scraper_ok = self.test_scraper_endpoints()
        error_ok = self.test_error_handling()
        
        # Résumé
        total_time = time.time() - start_time
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSUMÉ DES TESTS")
        print(f"Tests réussis: {passed_tests}/{total_tests}")
        print(f"Temps d'exécution: {total_time:.2f}s")
        
        if passed_tests == total_tests:
            print("🎉 Tous les tests sont passés avec succès!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) ont échoué")
            return False
    
    def save_results(self, filename="test_results.json"):
        """Sauvegarde les résultats des tests"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r['success']),
                    'failed_tests': sum(1 for r in self.test_results if not r['success'])
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Résultats sauvegardés dans {filename}")

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test de l\'API REST Paris OpenData')
    parser.add_argument('--url', default='http://localhost:5000/api', 
                       help='URL de base de l\'API (défaut: http://localhost:5000/api)')
    parser.add_argument('--save', action='store_true', 
                       help='Sauvegarder les résultats dans un fichier JSON')
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    
    try:
        success = tester.run_all_tests()
        
        if args.save:
            tester.save_results()
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrompus par l'utilisateur")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Erreur inattendue: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 