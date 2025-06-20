# Interface Web Paris se Transforme

Interface web dynamique React.js pour visualiser et interagir avec les données des projets urbains parisiens.

## Fonctionnalités

### 🏠 Page d'accueil
- Statistiques en temps réel
- Projets récents
- Navigation intuitive

### 🗺️ Exploration des projets
- Liste des projets avec filtres avancés
- Recherche textuelle
- Pagination
- Vue grille/liste
- Cartes interactives

### 📊 Statistiques et analyses
- Graphiques interactifs
- Répartition par arrondissement
- Évolution temporelle
- Budgets et catégories

### 🔧 Administration
- Déclenchement du scraper
- Monitoring en temps réel
- Gestion des données

## Technologies utilisées

- **React 19** - Framework UI
- **React Router** - Navigation
- **React Query** - Gestion d'état et cache
- **Styled Components** - Styles CSS-in-JS
- **Axios** - Requêtes HTTP
- **React Leaflet** - Cartes interactives
- **Chart.js** - Graphiques
- **React Icons** - Icônes
- **Date-fns** - Manipulation des dates

## Installation

1. Installer les dépendances :
```bash
npm install
```

2. Créer le fichier de configuration :
```bash
cp .env.example .env
```

3. Configurer les variables d'environnement dans `.env` :
```env
VITE_API_URL=http://localhost:5000/api
```

## Démarrage

### Mode développement
```bash
npm run dev
```
L'application sera disponible sur http://localhost:5173

### Build de production
```bash
npm run build
```

### Aperçu de production
```bash
npm run preview
```

## Structure du projet

```
src/
├── components/          # Composants réutilisables
│   ├── Layout/         # Header, Footer, Navigation
│   └── ProjectCard/    # Carte de projet
├── hooks/              # Hooks personnalisés
│   └── useApi.js       # Hooks React Query
├── pages/              # Pages de l'application
│   ├── HomePage.jsx    # Page d'accueil
│   ├── ProjectsPage.jsx # Liste des projets
│   └── ...
├── services/           # Services API
│   └── api.js          # Configuration Axios
├── App.jsx             # Composant principal
└── main.jsx            # Point d'entrée
```

## API Backend

L'interface communique avec l'API REST Flask. Assurez-vous que le backend est démarré sur le port 5000.

Endpoints principaux :
- `GET /api/data` - Liste des projets
- `GET /api/statistics` - Statistiques
- `GET /api/health` - Santé de l'API
- `POST /api/scrape` - Déclenchement du scraper (auth requise)

## Fonctionnalités avancées

### Cache intelligent
- Cache automatique des données avec React Query
- Invalidation intelligente
- Optimisations de performance

### Responsive Design
- Interface adaptative mobile/desktop
- Composants optimisés pour tous les écrans

### Gestion d'erreurs
- Toast notifications
- Gestion des états de chargement
- Fallbacks gracieux

### Accessibilité
- Navigation au clavier
- Contraste optimal
- Sémantique HTML

## Développement

### Ajout d'une nouvelle page

1. Créer le composant dans `src/pages/`
2. Ajouter la route dans `App.jsx`
3. Mettre à jour la navigation dans `Header.jsx`

### Ajout d'un nouveau hook API

1. Ajouter la fonction service dans `src/services/api.js`
2. Créer le hook dans `src/hooks/useApi.js`
3. Utiliser le hook dans les composants

### Styling

Utilisation de Styled Components pour un styling modulaire :

```jsx
const StyledComponent = styled.div`
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
`;
```

## Performance

- Code splitting automatique avec Vite
- Lazy loading des composants
- Optimisation des images
- Cache service worker (production)

## Tests

```bash
# Tests unitaires
npm run test

# Tests e2e
npm run test:e2e
```

## Déploiement

### Docker
```bash
docker build -t paris-frontend .
docker run -p 3000:80 paris-frontend
```

### Hébergement statique
Le build peut être déployé sur n'importe quel hébergeur statique (Netlify, Vercel, etc.)

## Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## Support

Pour toute question ou problème :
- Consulter la documentation de l'API
- Vérifier les logs du navigateur
- Tester la connectivité avec le backend
