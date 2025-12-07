# MCP Checklist - Minimum Compliant Product

## 🎯 Objectif
Garantir un périmètre MCP "tech ready" uniforme : PWA installable/offline, Core Web Vitals saines, sécurité L1–L2 ASVS, Web3/contrats sécurisés et testés, sans dette bloquante sur le cycle de vie du service worker ni l'accès wallet/chaîne.

## 📋 Portée
- **Next.js (App Router)** + Serwist
- **Vite** + vite-plugin-pwa  
- **dApps** Viem + Reown (ex-WalletConnect)
- **Pipeline sécurité contrats** (OpenZeppelin 5.x, Foundry fuzz/invariants, Slither CI)

---

## 0️⃣ Versioning et Lifecycle SW

### ✅ Stratégie SW
- [ ] **autoUpdate** activé pour rafraîchissement contrôlé du shell applicatif
- [ ] **skipWaiting** + **clientsClaim** pour éviter les versions zombies
- [ ] **navigationPreload** optionnel pour lisser les transitions en réseaux fluctuants
- [ ] Messaging UI "nouvelle version disponible" implémenté

### 📚 Références
- [Serwist Documentation](https://serwist.pages.dev/)
- [Workbox Lifecycle](https://developers.google.com/web/tools/workbox/guides/advanced-recipes#offer_a_page_reload_for_users)

---

## 1️⃣ PWA Commun (Tous Projets)

### ✅ Manifest Complet
- [ ] **name** et **short_name** définis
- [ ] **start_url** et **display** (standalone/fullscreen)
- [ ] **theme_color** et **background_color** cohérents
- [ ] **Icônes PNG 192/512 maskables** générées et validées
- [ ] **scope** et **orientation** appropriés

### ✅ Offline & Fallback
- [ ] Route **/offline** dédiée avec fallback navigation
- [ ] **navigationFallback** configuré pour requêtes navigations en échec
- [ ] Page offline avec design cohérent et actions de retry

### ✅ Stratégies de Cache
- [ ] **NetworkFirst** sur APIs/HTML dynamiques
- [ ] **CacheFirst** sur assets statiques (_next/static, images, polices)
- [ ] **runtimeCaching** par patterns documentés
- [ ] **Cache expiration** et **cleanup** configurés

### ✅ Dev/Tests
- [ ] **devOptions.enabled** en développement (Vite) ou équivalent
- [ ] Audit **Lighthouse PWA** avec score ≥ 90
- [ ] Validation **installabilité** mobile/desktop
- [ ] Test **offline** en critères d'acceptation

### 📚 Références
- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Lighthouse PWA Audit](https://developers.google.com/web/tools/lighthouse)

---

## 2️⃣ Next.js PWA (App Router)

### ✅ Intégration Serwist
- [ ] Worker basé sur **@serwist/next/worker**
- [ ] **precacheEntries** injectées au build
- [ ] **runtimeCaching** cohérent avec politique NetworkFirst/CacheFirst
- [ ] **clientsClaim** et **skipWaiting** activés

### ✅ Configuration
- [ ] **manifest.json** dans le Head
- [ ] Route **/offline** définie
- [ ] **app-worker.ts** configuré avec defaultCache
- [ ] Vérification prise de contrôle des clients

### 📝 Exemple Minimal Serwist (Next.js)

```typescript
// app-worker.ts
import { Serwist } from 'serwist'
import { defaultCache } from '@serwist/vite/worker'

declare const self: ServiceWorkerGlobalScope & { __SW_MANIFEST?: (string|object)[] }

const sw = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  precacheOptions: { cleanupOutdatedCaches: true },
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: defaultCache,
})
sw.addEventListeners()
```

### 📚 Références
- [Serwist Next.js Guide](https://serwist.pages.dev/docs/nextjs/getting-started)
- [Next.js PWA Best Practices](https://nextjs.org/docs/app/building-your-application/optimizing/pwa)

---

## 3️⃣ Vite + vite-plugin-pwa

### ✅ Configuration Minimale
- [ ] **registerType: 'autoUpdate'** configuré
- [ ] **workbox: { clientsClaim: true, skipWaiting: true }**
- [ ] **devOptions.enabled** pour test local
- [ ] **includeAssets** pour cohérence installation

### ✅ Manifest & Assets
- [ ] **meta theme-color** dans index.html
- [ ] **maskable icons** 192/512 générées
- [ ] **includeAssets** (favicon, apple-touch-icon)
- [ ] Test installation mobile/desktop

### 📝 Exemple Minimal VitePWA

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [VitePWA({
    registerType: 'autoUpdate',
    includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'maskable-512.png'],
    manifest: {
      name: 'App',
      short_name: 'App',
      start_url: '/',
      display: 'standalone',
      theme_color: '#0f172a',
      background_color: '#0f172a',
      icons: [
        { src: 'pwa-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
        { src: 'pwa-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
        { src: 'maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
      ]
    },
    workbox: { clientsClaim: true, skipWaiting: true },
    devOptions: { enabled: true }
  })]
})
```

### 📚 Références
- [vite-plugin-pwa Documentation](https://vite-pwa-org.netlify.app/)
- [Vite PWA Guide](https://vite-pwa-org.netlify.app/guide/)

---

## 4️⃣ Web3 dApps (Viem + Reown)

### ✅ Clients Viem Type-Safe
- [ ] **createPublicClient** (lecture) séparé de **createWalletClient** (écriture)
- [ ] **chain** et **transport** explicites configurés
- [ ] **fallback RPC** pour résilience réseau
- [ ] **Typage strict TypeScript** pour toutes les interactions

### ✅ Connexion Wallet
- [ ] **Reown AppKit** avec projectId (dashboard)
- [ ] **Modal multi-wallets** avec QR/deep link
- [ ] **Cross-device** desktop/mobile support
- [ ] **Architecture réseau** Reown/WalletConnect alignée

### ✅ Résilience UI
- [ ] **Validation runtime chainId**
- [ ] **Messages d'état transactionnels** clairs
- [ ] **Retry idempotent** et annulation claire
- [ ] **Fallback RPC** en cas de panne

### 📝 Exemple Minimal Viem

```typescript
import { createPublicClient, createWalletClient, http, custom } from 'viem'
import { mainnet } from 'viem/chains'

export const publicClient = createPublicClient({ 
  chain: mainnet, 
  transport: http() 
})

export const walletClient = typeof window !== 'undefined'
  ? createWalletClient({ 
      chain: mainnet, 
      transport: custom((window as any).ethereum) 
    })
  : undefined
```

### 📚 Références
- [Viem Documentation](https://viem.sh/)
- [Reown AppKit](https://docs.reown.com/appkit)
- [WalletConnect v2 Migration](https://docs.walletconnect.com/2.0/migration-guide)

---

## 5️⃣ Contrats et Sécurité On-Chain

### ✅ Gouvernance d'Accès
- [ ] **AccessManager/AccessManaged** OpenZeppelin 5.x privilégiés
- [ ] **Rôles granuleux** (ADMIN/OPERATOR/PAUSER) séparés
- [ ] **Événements indexés** sur changements de rôles
- [ ] **Timelocks** fonctionnels pour gouvernance

### ✅ Tests Foundry
- [ ] **Tests unitaires** complets
- [ ] **Fuzz testing** (property-based) activé
- [ ] **Invariants** sur états monétaires/permissions
- [ ] **Intégration CI** avec rapports artefacts

### ✅ Analyse Statique
- [ ] **Slither** en CI avec seuils de sévérité
- [ ] **Gate de merge bloquant** si findings critiques
- [ ] **Rapports artefacts** consultables
- [ ] **Diagrammes de flux** générés

### 📚 Références
- [OpenZeppelin 5.x AccessManager](https://docs.openzeppelin.com/contracts/5.x/access-control)
- [Foundry Testing](https://book.getfoundry.sh/forge/tests)
- [Slither Documentation](https://github.com/crytic/slither)

---

## 6️⃣ Sécurité Applicative (OWASP ASVS)

### ✅ Couverture L1–L2
- [ ] **Authentification** et gestion sessions/tokens
- [ ] **Contrôle d'accès** granulaire
- [ ] **Validation entrées** côté client/serveur
- [ ] **Durcissement configuration** et secrets
- [ ] **Entêtes sécurité** (CSP/HSTS/COOP/COEP)

### ✅ Traçabilité
- [ ] **Matrice de conformité** locale par chapitre ASVS
- [ ] **Écarts documentés** avec mesures compensatoires
- [ ] **Revue de surface d'attaque** avant exposition
- [ ] **Dépendances à jour** et verrouillées

### 📚 Références
- [OWASP ASVS v4.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)

---

## 7️⃣ Performance et Core Web Vitals

### ✅ Budgets CWV
- [ ] **LCP/CLS/INP** suivis via Lighthouse en CI
- [ ] **Budgets assets** (JS/CSS/images) définis
- [ ] **Seuils de régression** configurés
- [ ] **Monitoring continu** en production

### ✅ Caches Ciblés
- [ ] **NetworkFirst** sur HTML/API pour fraîcheur
- [ ] **CacheFirst** sur assets pour LCP stable
- [ ] **Stratégies adaptées** au type de contenu
- [ ] **Offline shell** fonctionnel

### 📚 Références
- [Core Web Vitals](https://web.dev/vitals/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

---

## 8️⃣ Déploiements Statiques (GitHub Pages)

### ✅ Scope & Configuration
- [ ] **Scope SW** et **start_url** compatibles
- [ ] **Chemins publics** vérifiés pour GH Pages
- [ ] **Test installabilité/offline** en build statique local
- [ ] **Fallback offline** et stratégies runtime adaptées

### 📚 Références
- [GitHub Pages PWA](https://docs.github.com/en/pages/getting-started-with-github-pages)
- [Static Site PWA](https://web.dev/pwa-checklist/)

---

## 9️⃣ CI/CD (Exigences MCP)

### ✅ Build + PWA Audit
- [ ] **Build production** automatisé
- [ ] **Audit Lighthouse PWA/CWV** en CI
- [ ] **Échec si régression** par rapport au seuil
- [ ] **Rapports artefacts** stockés

### ✅ Sécurité Contrats
- [ ] **forge test** (unit/fuzz/invariants) en CI
- [ ] **Slither action** avec fail-on-error
- [ ] **Push rapports** et artefacts
- [ ] **Gate de merge** pour findings critiques

### 📝 Exemple GitHub Actions

```yaml
name: ci-mcp
on: [push, pull_request]
jobs:
  web-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run build
      - run: npx lhci autorun || exit 1
      
  onchain-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: foundry-rs/foundry-toolchain@v1
        with: { version: nightly }
      - run: forge test -vvv
      - name: Slither
        uses: crytic/slither-action@v0.3.0
        with:
          target: .
          fail-on: medium
```

### 📚 Références
- [GitHub Actions](https://docs.github.com/en/actions)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

---

## 🔟 Validation Finale MCP par Dépôt

### ✅ PWA
- [ ] **Installabilité** validée mobile/desktop
- [ ] **Offline** fonctionnel avec fallback
- [ ] **SW autoUpdate** validé
- [ ] **Caches conformes** aux stratégies
- [ ] **Score Lighthouse PWA** ≥ seuil projet

### ✅ Sécurité
- [ ] **ASVS L1–L2** tracé et documenté
- [ ] **Dépendances à jour** et verrouillées
- [ ] **Entêtes sécurité** appliquées
- [ ] **Secrets gérés** correctement

### ✅ Web3/Contrats
- [ ] **Flux wallet stables** (Reown)
- [ ] **Clients Viem** séparés et typés
- [ ] **Tests Foundry** verts
- [ ] **Slither** sans findings bloquants

---

## 📊 Mapping Rapide par Dépôt

### Next.js Projects
- **antony-lambi-nextjs** → Sections 1–2 + 4 + 5 + 9
- **Coach-AI-main** → Sections 1–2 + 6 + 9
- **v0-fixierun-1-plan** → Sections 1–2 + 9
- **fixie-run-next** → Sections 1–2 + 4 + 9
- **fixierun-unified** → Sections 1–2 + 4 + 5 + 6 + 9

### Vite Projects
- **folio-manage-ai** → Sections 1 + 3 + 9
- **fixierun-insight-dash** → Sections 1 + 3 + 9
- **tehen-portfolio-dashboard** → Sections 1 + 3 + 9
- **sidebase-seo-saas** → Sections 1 + 3 + 9
- **giggle-learn** → Sections 1 + 3 + 9
- **techbuzzinga-main** → Sections 1 + 3 + 9

### Web3/Contrats Projects
- **fixie-run-next** → Sections 4 + 9 (exigences fortes)
- **fixierun-unified** → Sections 4 + 5 + 6 + 9 (exigences fortes)

### Déploiement Statique
- **node-pwa** → Sections 1 + 3 + 8 + 9

---

## 🚀 Exécution Suggérée (7 jours)

### Jour 1–2: PWA Standardisation
- [ ] Normaliser PWA Next/Vite (manifest, SW autoUpdate, offline, caches)
- [ ] Tester devOptions + installabilité sur tous les projets

### Jour 3–4: Web3 Integration
- [ ] Viem + Reown sur dapps
- [ ] Flux connexion/signature et états UI résilients
- [ ] Gestion chainId/RPC et fallbacks

### Jour 5: Sécurité Contrats
- [ ] Foundry tests fuzz/invariants
- [ ] Slither sur fixierun-unified en CI
- [ ] Configuration gate de merge

### Jour 6–7: Validation & Déploiement
- [ ] Passage ASVS L1–L2 sur tous les projets
- [ ] Corrections et optimisations
- [ ] Validation CWV/Lighthouse PWA par projet

---

## 📝 Notes Web3/Contrats

### OpenZeppelin 5.x
- Préférer **AccessManager** + **AccessManaged** pour gouvernance centralisée multi-contrats
- **AccessControl** pour rôles simples, **AccessManager** pour gouvernance complexe

### Foundry
- Activer **property-based fuzz** et **invariants** pour détecter edge cases
- Focus sur flux monétaires/permissions critiques

### Slither
- Intégrer **détecteurs** et **diagrammes** en CI
- Bloquer merge si issues critiques (medium+)

---

## 🔗 Liens Utiles

- [Serwist Documentation](https://serwist.pages.dev/)
- [Vite PWA Plugin](https://vite-pwa-org.netlify.app/)
- [Viem Documentation](https://viem.sh/)
- [Reown AppKit](https://docs.reown.com/appkit)
- [OpenZeppelin 5.x](https://docs.openzeppelin.com/contracts/5.x/)
- [Foundry Book](https://book.getfoundry.sh/)
- [Slither](https://github.com/crytic/slither)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [Core Web Vitals](https://web.dev/vitals/)
- [PWA Checklist](https://web.dev/pwa-checklist/)

---

**Version:** 1.0.0  
**Dernière mise à jour:** $(date)  
**Mainteneur:** DevTehen
