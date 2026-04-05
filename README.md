# TP2 - FastAPI et Kafka

TP2 de microservices avec FastAPI, Kafka et une interface web statique.

## Architecture
- `users_service.py` expose les utilisateurs et publie les requêtes Kafka.
- `products_service.py` écoute les requêtes Kafka et renvoie les produits.
- `gateway_service.py` sert de point d’entrée HTTP et la page statique.
- `static/index.html` fournit l’interface de démonstration.
- `run_all.sh` démarre Kafka et les services locaux.

## Prérequis
- Python 3.11+.
- Kafka accessible sur `localhost:9092`.
- Les topics `user_requests` et `product_responses`.

Créer les topics si besoin:

```bash
kafka-topics --create --topic user_requests --bootstrap-server localhost:9092
kafka-topics --create --topic product_responses --bootstrap-server localhost:9092
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
./run_all.sh
```

L’interface est disponible sur `http://localhost:8002`.

Si tu veux démarrer les services à la main:

```bash
uvicorn users_service:app --reload --port 8000
uvicorn products_service:app --reload --port 8001
python products_service.py
uvicorn gateway_service:app --reload --port 8002
```

## Publication sur GitHub
Le dépôt est déjà prêt pour GitHub. Les artefacts générés localement, les logs, les caches Python et Kafka local sont exclus via `.gitignore`.

Pour publier une nouvelle version:

```bash
git add .
git commit -m "Update TP2"
git push
```

## Licence
Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE).
