# Aleas – gestion des pointeuses ZKTeco / UNIS

Phase 1 (backend) : modèle de données, module appareils, synchronisation sans perte.

## Démarrage
```bash
cp .env.example .env && docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```
API : `/api/devices/`, `/api/devices/{id}/test_connection/`, `/api/devices/{id}/sync/`, `/api/sync-logs/`, `/api/employees/`, `/api/punches/`.

## Garanties anti-perte
- La mémoire de la pointeuse n'est jamais effacée par l'application.
- Insertion idempotente : contrainte unique (appareil, id utilisateur, horodatage).
- En cas d'échec : état enregistré, nouvelle tentative avec backoff exponentiel (Celery), le cycle planifié reprend ensuite.

## Limites actuelles
- ZKTeco via `pyzk` (TCP/UDP). L'adaptateur UNIS est un squelette : le protocole dépend du modèle exact.
- Pas encore : frontend React, horaires/retards, rapports, sauvegarde/restauration.
