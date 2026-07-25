# Production — Frontend Vercel + API VPS (HTTPS)

Topologie retenue :

```
Navigateur
   ├─ https://<projet>.vercel.app        → Frontend Next.js (Vercel)
   └─ https://api.<ip>.sslip.io          → Caddy → API FastAPI (VPS)
                                              └─ Postgres / Kafka / Airflow (VPS)
```

Le frontend est déployé **par Vercel** (intégration GitHub), pas par le job `5 · Deploy`.
Le job `5 · Deploy` ne déploie que l'**API + Caddy** sur le VPS.

---

## 1. VPS — API en HTTPS

### a. Cloner le dépôt sur le serveur
```bash
git clone https://github.com/Semakia/t-data-901-crypto_viz.git ~/cryptoviz
cd ~/cryptoviz
```
Ce chemin devient la variable `DEPLOY_PATH`.

### b. Créer `.config/iac/prod/.env.prod` (NON versionné)
```bash
BRONZE_DB_HOST=...
BRONZE_DB_NAME=...
BRONZE_DB_USER=...
BRONZE_DB_PASSWORD=...
SILVER_DB_HOST=...
GOLD_DB_HOST=...
# ... (mêmes clés que src/.env)

# Domaine public de l'API — sslip.io résout <ip>.sslip.io vers l'IP,
# ce qui permet d'obtenir un certificat Let's Encrypt sans acheter de domaine.
API_DOMAIN=api.91.134.132.149.sslip.io

# Origine autorisée pour le CORS = l'URL du frontend Vercel
CORS_ORIGINS=https://<ton-projet>.vercel.app
```

### c. Ouvrir les ports 80 et 443
Le port **80 est obligatoire** pour le challenge HTTP-01 de Let's Encrypt.

### d. Premier démarrage manuel (pour vérifier le certificat)
```bash
docker compose -f .config/iac/prod/docker-compose.yml up -d
docker compose -f .config/iac/prod/docker-compose.yml logs -f caddy
curl https://api.91.134.132.149.sslip.io/health
```

---

## 2. Vercel — Frontend

1. Vercel → **Add New Project** → importer le dépôt GitHub.
2. **Root Directory** : `crypto-dashboard`
3. Framework : Next.js (détecté automatiquement).
4. **Environment Variables** :
   - `NEXT_PUBLIC_API_URL` = `https://api.91.134.132.149.sslip.io`
5. Déployer → Vercel fournit l'URL `https://<projet>.vercel.app`.

Vercel redéploie ensuite automatiquement à chaque push sur `main`.

> Reporter cette URL dans `CORS_ORIGINS` (`.env.prod`) **et** dans la variable
> GitHub `APP_FRONTEND_URL`, puis redémarrer l'API.

---

## 3. GitHub — Variables & secrets

**Variables** (Settings → Secrets and variables → Actions → *Variables*) :

| Nom | Valeur |
| --- | --- |
| `DEPLOY_ENABLED` | `true` (débloque le job `deploy`) |
| `DEPLOY_PATH` | `~/cryptoviz` |
| `APP_API_URL` | `https://api.91.134.132.149.sslip.io` |
| `APP_FRONTEND_URL` | `https://<projet>.vercel.app` |

**Secrets** (Environment `production`) :

| Nom | Valeur |
| --- | --- |
| `DEPLOY_HOST` | `91.134.132.149` |
| `DEPLOY_USER` | utilisateur SSH du VPS |
| `DEPLOY_SSH_KEY` | clé privée **brute** (`cat ~/.ssh/vps_key`, pas de base64) |

La clé **publique** correspondante doit être dans `~/.ssh/authorized_keys` du serveur.

---

## Ordre de mise en place

1. VPS prêt (clone + `.env.prod` + ports ouverts + `up -d` manuel qui répond en HTTPS)
2. Vercel déployé, URL récupérée
3. `CORS_ORIGINS` mis à jour côté serveur, API redémarrée
4. Variables/secrets GitHub renseignés
5. **En dernier** : `DEPLOY_ENABLED=true` → le job `5 · Deploy` s'exécute au lieu d'être *skipped*

> Mettre `DEPLOY_ENABLED=true` **avant** que le serveur soit prêt fera échouer le job
> (au lieu de le sauter). C'est pour cela que c'est la dernière étape.
