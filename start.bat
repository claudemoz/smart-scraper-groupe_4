@echo off
echo Démarrage de Smart Scraper avec Docker...

REM Vérifier que Docker est installé
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker n'est pas installé. Veuillez installer Docker Desktop.
    pause
    exit /b 1
)

REM Vérifier que Docker Compose est installé
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Compose n'est pas installé. Veuillez installer Docker Compose.
    pause
    exit /b 1
)

REM Arrêter les conteneurs existants s'ils existent
echo Arrêt des conteneurs existants...
docker-compose down

REM Construire et démarrer les services
echo Construction et démarrage des services...
docker-compose up --build -d

REM Attendre que les services soient prêts
echo Attente que les services soient prêts...
timeout /t 30 /nobreak >nul

REM Vérifier le statut des services
echo Vérification du statut des services...
docker-compose ps

echo.
echo Smart Scraper est maintenant disponible !
echo.
echo Application web : http://localhost
echo API Backend : http://localhost:5000
echo phpMyAdmin : http://localhost:8080
echo.
echo Identifiants de connexion :
echo Username: admin
echo Password: admin123
echo.
echo Pour voir les logs : docker-compose logs -f
echo Pour arrêter : docker-compose down
echo.
pause 