# Production — Frontend Vercel + API VPS (HTTPS via le Caddy existant)

Le VPS héberge déjà un autre projet (« homepedia ») dont le **Caddy possède les
ports 80/443**. On ne lance donc **pas** de second reverse proxy : notre API
rejoint le réseau de ce Caddy, qui la publie en HTTPS.

```
Navigateur
   ├─ https://t-data-901-crypto.vercel.app     → Frontend Next.js (Vercel)
   └─ https://api.91.134.132.149.sslip.io      → Caddy homepedia → cryptoviz-api:8000 (VPS)
```

- Frontend : déployé **par Vercel** (intégration GitHub).
- API : déployée par le job `5 · Deploy` (conteneur `cryptoviz-api`, sans ports publiés).
- HTTPS : géré par le **Caddy de homepedia** (Let's Encrypt), via un bloc de site.

---

## 1. VPS — préparer l'API

### a. Cloner le dépôt (= `DEPLOY_PATH`)
```bash
git clone https://github.com/Semakia/t-data-901-crypto_viz.git ~/cryptoviz
```

### b. Créer `.config/iac/prod/.env.prod` (NON versionné)
```bash
BRONZE_DB_HOST=...
BRONZE_DB_NAME=...
BRONZE_DB_USER=...
BRONZE_DB_PASSWORD=...
SILVER_DB_HOST=...
GOLD_DB_HOST=...
# ... (mêmes clés que src/.env)

# Origine autorisée pour le CORS = l'URL du frontend Vercel
CORS_ORIGINS=https://t-data-901-crypto.vercel.app
```

Le job `5 · Deploy` lance ensuite `cryptoviz-api` sur le réseau
`homepedia-prod_default` (réseau externe du Caddy existant), sans publier de port.

---

## 2. VPS — brancher l'API sur le Caddy de homepedia (une seule fois)

Le Caddyfile de homepedia est un fichier hôte :
`/home/ubuntu/T-DAT-902-PAR_5/iac/docker/prod/vps/Caddyfile`

**a. Y ajouter ce bloc de site** (à la fin, sans toucher aux blocs existants) :
```
api.91.134.132.149.sslip.io {
	reverse_proxy cryptoviz-api:8000
}
```

**b. Recharger Caddy sans coupure** (après que `cryptoviz-api` tourne) :
```bash
docker exec homepedia-prod-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

Caddy provisionne alors automatiquement le certificat Let's Encrypt pour le
sous-domaine (il possède déjà 80/443, et sslip.io résout vers l'IP du VPS).

> Ordre important : déployer l'API **d'abord** (pour qu'elle soit résoluble sur
> le réseau), **puis** ajouter le bloc + recharger Caddy.

---

## 3. Vercel — Frontend

- Root Directory : `crypto-dashboard` · Framework : Next.js
- Variable d'env : `NEXT_PUBLIC_API_URL = https://api.91.134.132.149.sslip.io`

---

## 4. GitHub — Variables & secrets

**Variables** (Actions → Variables) :

| Nom | Valeur |
| --- | --- |
| `DEPLOY_ENABLED` | `true` |
| `DEPLOY_PATH` | `~/cryptoviz` |
| `APP_API_URL` | `https://api.91.134.132.149.sslip.io` |
| `APP_FRONTEND_URL` | `https://t-data-901-crypto.vercel.app` |

**Secrets** (Environment `production`) : `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`.

---

## Vérification finale
```bash
docker compose -f .config/iac/prod/docker-compose.yml ps   # cryptoviz-api = Up (healthy)
curl https://api.91.134.132.149.sslip.io/health
```
