# TP2 - FastAPI et Kafka

## Publication sur GitHub
Ce projet peut être versionné sur GitHub comme dépôt source. Avant le premier push, crée le dépôt Git localement, ajoute le remote GitHub, puis pousse la branche principale. Les artefacts générés localement, les logs et l'installation Kafka sont exclus via `.gitignore`.

## Prérequis
- Kafka actif sur `localhost:9092`
- Topics créés:

```bash
kafka-topics --create --topic user_requests --bootstrap-server localhost:9092
kafka-topics --create --topic product_responses --bootstrap-server localhost:9092
```

## Lancement

```bash
pip install -r requirements.txt
uvicorn users_service:app --reload --port 8000
uvicorn products_service:app --reload --port 8001
python products_service.py
uvicorn gateway_service:app --reload --port 8002
```

Interface disponible sur `http://localhost:8002`
./run_all.sh

## Mise en ligne sur GitHub
1. Initialiser le dépôt local: `git init`
2. Ajouter les fichiers: `git add .`
3. Créer un premier commit: `git commit -m "Initial commit"`
4. Créer un dépôt vide sur GitHub
5. Ajouter le remote: `git remote add origin <URL_DU_DEPOT>`
6. Pousser: `git push -u origin main`
