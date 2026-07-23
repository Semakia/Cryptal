# Pipeline CI/CD — Boucle DevOps

Chaque étape de la boucle DevOps a **son propre workflow** (un fichier =
une étape). Le volet **sécurité (DevSecOps)** est intégré à l'étape **CODE**
sous forme de jobs `code: *-scan`.

```
        ┌────────────────────────── Dev ──────────────────────────┐   ┌──────────── Ops ────────────┐
PLAN ─▶ CODE ─▶ TEST ─▶ BUILD ─▶ RELEASE ─▶ DEPLOY ─▶ MONITOR ─▶ FEEDBACK ─┐
  ▲                                                                         │
  └───────────────────────────────────────────────────────────────────────┘
```

| Étape        | Fichier                    | Jobs                                                                 |
| ------------ | -------------------------- | ------------------------------------------------------------------- |
| **PLAN**     | `ISSUE_TEMPLATE/`, `pull_request_template.md` | cadrage des tâches et des PR                      |
| **CODE**     | `workflows/code.yml`       | `code: lint` · `code: sast-scan` · `code: secret-scan` · `code: deps-scan` · `code: trivy-scan` |
| **TEST**     | `workflows/test.yml`       | `test: pytest`                                                       |
| **BUILD**    | `workflows/build.yml`      | `build: docker` (api + frontend, sans push)                         |
| **RELEASE**  | `workflows/release.yml`    | `release: image` (→ GHCR) · `release: github-release` (tag `v*`)     |
| **DEPLOY**   | `workflows/deploy.yml`     | `deploy: server` (SSH compose up, opt-in `DEPLOY_ENABLED`)          |
| **MONITOR**  | `workflows/monitor.yml`    | `monitor: healthchecks` (déclenché après un deploy réussi)          |
| **FEEDBACK** | `workflows/feedback.yml`   | `feedback: incident-issue` (issue auto si deploy/monitor échoue)     |

## Enchaînement des étapes Ops

`5 · Deploy` → (succès) → `6 · Monitor` → (échec d'une des deux) → `7 · Feedback`,
via le déclencheur `workflow_run`.

## Déclencheurs

| Workflow      | push branche | PR → main | push `main` | tag `v*` | manuel | après un autre workflow |
| ------------- | :----------: | :-------: | :---------: | :------: | :----: | :---------------------: |
| `code.yml`    | ✅           | ✅        | ✅          |          |        | + hebdo (cron)          |
| `test.yml`    | ✅           | ✅        | ✅          |          |        |                         |
| `build.yml`   | ✅           | ✅        | ✅          |          |        |                         |
| `release.yml` |              |           | ✅          | ✅       |        |                         |
| `deploy.yml`  |              |           |             | (release)| ✅     |                         |
| `monitor.yml` |              |           |             |          | ✅     | après `5 · Deploy`      |
| `feedback.yml`|              |           |             |          |        | après `5 · Deploy` / `6 · Monitor` |

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
