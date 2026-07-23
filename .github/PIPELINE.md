# Pipeline CI/CD — Boucle DevOps

La chaîne CI/CD suit les étapes de la boucle DevOps. Chaque étape est matérialisée
par un job (préfixé `[ÉTAPE]`) dans l'un des workflows GitHub Actions.

```
        ┌──────────────────────── Dev ────────────────────────┐   ┌──────────── Ops ────────────┐
PLAN ─▶ CODE ─▶ BUILD ─▶ TEST ─▶ (SECURE) ─▶ RELEASE ─▶ DEPLOY ─▶ MONITOR ─▶ FEEDBACK ─┐
  ▲                                                                                      │
  └──────────────────────────────────────────────────────────────────────────────────┘
```

| Étape        | Où                              | Détail                                                                 |
| ------------ | ------------------------------- | ---------------------------------------------------------------------- |
| **PLAN**     | `ISSUE_TEMPLATE/`, PR template  | Cadrage des tâches et des PR avant le code                              |
| **CODE**     | `ci.yml` → `code-quality`       | Marqueurs de conflit, ruff (Python), eslint (front)                    |
| **TEST**     | `ci.yml` → `test`               | pytest sur `src/test`                                                   |
| **BUILD**    | `ci.yml` → `build`              | Build des images Docker API + frontend (validation, sans push)         |
| **SECURE**   | `security.yml`                  | SAST (bandit/semgrep), scan deps (pip-audit/pnpm audit), secrets (gitleaks), image (trivy) — transverse |
| **RELEASE**  | `release.yml`                   | Push des images sur GHCR (`latest`/`sha`/`semver`) + GitHub Release sur tag `v*` |
| **DEPLOY**   | `deploy.yml` → `deploy`         | SSH → `docker compose pull && up` sur le serveur (opt-in `DEPLOY_ENABLED`) |
| **MONITOR**  | `deploy.yml` → `monitor`        | Health checks post-déploiement (`/health`, front)                      |
| **FEEDBACK** | `deploy.yml` → `feedback`       | Ouverture automatique d'une issue d'incident si échec + re-scan sécurité hebdo |

## Déclencheurs

| Workflow      | push branche | PR → main | push `main` | tag `v*` | manuel | planifié |
| ------------- | :----------: | :-------: | :---------: | :------: | :----: | :------: |
| `ci.yml`      | ✅           | ✅        | ✅          |          |        |          |
| `security.yml`| ✅           | ✅        | ✅          |          |        | hebdo    |
| `release.yml` |              |           | ✅          | ✅       |        |          |
| `deploy.yml`  |              |           |             | (release)| ✅     |          |

## Activer le déploiement

Le job **DEPLOY** est désactivé par défaut. Pour l'activer une fois le serveur prêt :

1. **Variables** (Settings → Secrets and variables → Actions → *Variables*)
   - `DEPLOY_ENABLED = true`
   - `DEPLOY_PATH` (chemin du projet sur le serveur, ex. `~/cryptoviz`)
   - `APP_API_URL`, `APP_FRONTEND_URL` (pour le MONITOR)
2. **Secrets** (Environment `production`)
   - `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`
3. Fournir un `docker-compose.prod.yml` sur le serveur, référençant les images GHCR
   publiées par l'étape RELEASE.
