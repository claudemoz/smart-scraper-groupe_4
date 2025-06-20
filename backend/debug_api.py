import requests
import json
from pprint import pprint

def debug_api_structure():
    """Debug la structure de l'API Paris OpenData"""
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/parissetransforme/records"
    params = {
        'limit': 10,
        'offset': 0,
        'timezone': 'Europe/Paris'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("=== STRUCTURE GLOBALE DE LA RÉPONSE ===")
        print(f"Clés principales: {list(data.keys())}")
        print(f"Nombre total d'enregistrements: {data.get('total_count', 'N/A')}")
        print(f"Nombre d'enregistrements retournés: {len(data.get('results', []))}")
        
        if 'results' in data and data['results']:
            print("\n=== STRUCTURE D'UN ENREGISTREMENT ===")
            first_record = data['results'][0]
            print(f"Clés de l'enregistrement: {list(first_record.keys())}")
            
            print(f"\n=== PREMIER ENREGISTREMENT COMPLET ===")
            pprint(first_record, width=120, depth=4)
                
           
            print(f"\n=== RECHERCHE D'UN ENREGISTREMENT AVEC COORDONNÉES ===")
            found_with_coords = False
            for i, record in enumerate(data['results']):
                geo_point = record.get('geo_point_2d')
                
                print(f"Enregistrement {i+1}:")
                print(f"  - titre_descriptif: {record.get('titre_descriptif', 'N/A')[:50]}...")
                print(f"  - geo_point_2d présent: {geo_point is not None}")
                if geo_point:
                    print(f"  - geo_point_2d: {geo_point}")
                    print(f"  - Type: {type(geo_point)}")
                    if isinstance(geo_point, dict):
                        print(f"    - lat: {geo_point.get('lat')}")
                        print(f"    - lon: {geo_point.get('lon')}")
                    found_with_coords = True
                    print(f"\n=== ENREGISTREMENT AVEC COORDONNÉES COMPLET ===")
                    pprint(record, width=120, depth=4)
                    break
                print()
            
            if not found_with_coords:
                print("Aucun enregistrement avec coordonnées trouvé dans les 10 premiers.")
                print("Essayons avec plus d'enregistrements...")
                
                params['limit'] = 100
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                for i, record in enumerate(data['results']):
                    geo_point = record.get('geo_point_2d')
                    if geo_point:
                        print(f"\nTrouvé un enregistrement avec coordonnées à l'index {i}:")
                        print(f"  - titre_descriptif: {record.get('titre_descriptif', 'N/A')}")
                        print(f"  - geo_point_2d: {geo_point}")
                        pprint(record, width=120, depth=4)
                        break
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")

if __name__ == "__main__":
    debug_api_structure() 