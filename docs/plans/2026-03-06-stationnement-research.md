# Recherche : sources alternatives pour le signal "stationnement payant"

**Date :** 2026-03-06
**Contexte :** Le scoring de prospection utilise un signal `stat_payant` (poids 30%) basé sur l'enquête GART/Cerema 2019, qui ne couvre que **226 communes** (taux de réponse 41% sur 551 collectivités interrogées). Or environ **800+ communes** pratiquent réellement le stationnement payant en France. Ce signal est donc très incomplet.

**Source actuelle :** `https://static.data.gouv.fr/resources/enquete-sur-la-reforme-du-stationnement-payant-sur-voirie/20200207-161331/stt-voirie-payant-opendata-v2.csv`

---

## 1. ANTAI — Liste des collectivités délégataires FPS

**Description :** L'ANTAI (Agence Nationale de Traitement Automatisé des Infractions) gère le système de Forfait Post-Stationnement (FPS) pour le compte des collectivités. Fin juin 2024, **622 collectivités** avaient signé une convention avec l'ANTAI (613 en "cycle complet", 9 en "cycle partiel"). Plus de 98% des collectivités ayant du stationnement payant délèguent à l'ANTAI.

| Critère | Valeur |
|---------|--------|
| URL | https://www.antai.gouv.fr/systeme-forfait-post-stationnement-fps/ |
| Format | Pas de dataset open data identifié (liste sur le site ANTAI, non structurée) |
| Couverture | ~622 collectivités (quasi-exhaustif pour le stationnement payant sur voirie) |
| Fraîcheur | Données actualisées en continu (conventions signées) |
| Facilité d'intégration | **Difficile** — pas de fichier téléchargeable structuré. Nécessiterait un scraping ou une demande officielle à l'ANTAI. |

**Verdict :** Excellente couverture (3x la source actuelle), mais pas d'accès open data. Piste à creuser via une demande d'accès.

---

## 2. BNLS — Base Nationale des Lieux de Stationnement

**Description :** Dataset national consolidant les parkings hors voirie (en ouvrage) en France, standardisé par transport.data.gouv.fr. Inclut un champ `gratuit_payant` indiquant si le parking est payant ou gratuit.

| Critère | Valeur |
|---------|--------|
| URL data.gouv.fr | https://www.data.gouv.fr/datasets/base-nationale-des-lieux-de-stationnement |
| URL transport.data.gouv.fr | https://transport.data.gouv.fr/datasets/base-nationale-des-lieux-de-stationnement |
| URL OpenDataSoft | https://public.opendatasoft.com/explore/dataset/mobilityref-france-base-nationale-des-lieux-de-stationnement/ |
| Format | CSV (205 Ko consolidé), schéma standardisé (schema.data.gouv.fr) |
| Schéma | https://schema.data.gouv.fr/etalab/schema-stationnement/latest.html |
| Champs utiles | `gratuit_payant`, `nb_places`, `Xlong`, `Ylat`, code INSEE dérivable des coordonnées |
| Couverture | Partielle — environ 20 villes/agglomérations contributrices. **Hors voirie uniquement** (parkings en ouvrage, pas le stationnement sur voirie). |
| Fraîcheur | Version 0.1.3, consolidation manuelle non automatisée |
| Facilité d'intégration | **Moyenne** — CSV standardisé, mais couverture limitée aux parkings en ouvrage. Le code INSEE n'est pas directement dans le schéma (nécessite géocodage inverse ou enrichissement). |

**Verdict :** Utile en complément mais ne répond pas directement au besoin : le stationnement payant **sur voirie** est le vrai indicateur de prospection vidéo-verbalisation, pas les parkings en ouvrage.

---

## 3. FUN — Fichier Unique National Stationnement

**Description :** Fichier consolidé développé par l'incubateur SciencesPo pour le compte de transport.data.gouv.fr, harmonisant les données de stationnement.

| Critère | Valeur |
|---------|--------|
| URL | https://www.data.gouv.fr/datasets/fichier-unique-national-stationnement/ |
| Format | CSV (séparateur `;`, UTF-8) |
| Champs utiles | Champ "Gratuit/Payant" (valeurs "Gratuit" ou "Payant") |
| Couverture | Similaire à la BNLS, focalisé sur les parkings hors voirie |
| Fraîcheur | Dernière MAJ inconnue (probablement 2019-2020) |
| Facilité d'intégration | **Moyenne** — même limitation que BNLS (hors voirie) |

**Verdict :** Redondant avec la BNLS, même limitation (hors voirie uniquement).

---

## 4. OpenStreetMap — Tags `fee=yes` sur les parkings

**Description :** OpenStreetMap contient des objets `amenity=parking` avec un tag `fee=yes`/`fee=no`. Extractible via l'API Overpass. Couvre à la fois le stationnement sur voirie et hors voirie.

| Critère | Valeur |
|---------|--------|
| URL Overpass | https://overpass-turbo.eu/ |
| API endpoint | https://overpass-api.de/api/interpreter |
| Format | JSON (Overpass JSON), GeoJSON |
| Tags pertinents | `amenity=parking` + `fee=yes`, `parking:fee=yes`, `parking=street_side` + `fee=yes` |
| Couverture | Estimée à **plusieurs milliers** d'objets en France (données contributives, bien renseignées dans les zones urbaines) |
| Fraîcheur | Mise à jour continue (contributif) |
| Facilité d'intégration | **Bonne** — requête Overpass simple, résultats en JSON, rattachement au code INSEE via géocodage inverse ou intersection avec les géométries communales |

**Requête Overpass type :**
```
[out:json][timeout:300];
area["ISO3166-1"="FR"]->.france;
(
  nwr["amenity"="parking"]["fee"="yes"](area.france);
  nwr["amenity"="parking"]["fee:conditional"~"yes"](area.france);
);
out center;
```

**Post-traitement nécessaire :**
1. Exécuter la requête Overpass (peut prendre quelques minutes)
2. Pour chaque résultat, déterminer le code INSEE de la commune (intersection point/polygone avec les géométries communales)
3. Dédupliquer par commune → liste de codes INSEE ayant au moins un parking payant
4. Potentiellement combiner avec le tag `parking=street_side` pour cibler le stationnement sur voirie

**Verdict :** Source la plus prometteuse. Couverture nettement supérieure au GART, données à jour, extraction automatisable. La qualité dépend du renseignement du tag `fee` par les contributeurs OSM (souvent bien renseigné en zone urbaine, lacunaire en zone rurale — mais les communes rurales n'ont généralement pas de stationnement payant).

---

## 5. Cerema — Enquêtes stationnement

**Description :** Le Cerema mène des enquêtes sur le stationnement en partenariat avec le GART. Les données publiées sont les mêmes que celles de l'enquête GART 2019 déjà utilisée.

| Critère | Valeur |
|---------|--------|
| URL | https://www.cerema.fr/fr/actualites/enquete-reforme-du-stationnement |
| Couverture | 226 communes (même source que l'actuelle) |
| Fraîcheur | 2019 (enquête sur l'année 2018) |
| Facilité d'intégration | Déjà intégrée |

**Verdict :** Pas d'amélioration — c'est la source actuelle.

---

## 6. Point d'Accès National (transport.data.gouv.fr)

**Description :** Le PAN agrège les données de mobilité dont le stationnement. Les datasets stationnement disponibles sont essentiellement la BNLS (déjà analysée ci-dessus) et des datasets locaux épars.

| Critère | Valeur |
|---------|--------|
| URL | https://transport.data.gouv.fr/datasets?type=private-parking |
| Couverture | Limitée aux parkings hors voirie, quelques dizaines de producteurs |
| Facilité d'intégration | Faible — datasets fragmentés par collectivité, pas de vue nationale du stationnement sur voirie |

**Verdict :** Pas de valeur ajoutée au-delà de la BNLS.

---

## Synthèse et recommandation

| Source | Couverture estimée | Sur voirie ? | Open data ? | Recommandation |
|--------|-------------------|-------------|-------------|----------------|
| GART 2019 (actuel) | 226 communes | Oui | Oui | Conserver comme fallback |
| ANTAI FPS | ~622 collectivités | Oui | Non | Demander l'accès |
| BNLS | ~20 agglos | Non (hors voirie) | Oui | Complémentaire seulement |
| FUN | ~20 agglos | Non (hors voirie) | Oui | Redondant avec BNLS |
| **OpenStreetMap** | **Estimé 500-1000+ communes** | **Oui + hors voirie** | **Oui** | **Recommandé — priorité 1** |
| Cerema | 226 communes | Oui | Oui | = GART, déjà utilisé |
| PAN transport | ~20 agglos | Non | Oui | Pas de valeur ajoutée |

### Plan d'action recommandé

1. **Court terme (priorité 1) : OpenStreetMap via Overpass API**
   - Extraire tous les `amenity=parking` avec `fee=yes` en France
   - Croiser avec les géométries communales pour obtenir la liste de codes INSEE
   - Fusionner avec les 226 communes GART existantes (union)
   - Couverture attendue : 500-1000+ communes (x2 à x4 par rapport à l'actuel)
   - Script Python estimé : ~80 lignes, dépendance `requests` + `shapely` pour le géocodage

2. **Moyen terme (priorité 2) : ANTAI**
   - Contacter l'ANTAI pour demander la liste des collectivités ayant signé une convention FPS
   - Si obtenue, c'est la source la plus exhaustive (~622 collectivités = quasi-100% du stationnement payant)

3. **Complémentaire : BNLS**
   - Intégrer la BNLS en complément pour les communes ayant des parkings payants en ouvrage mais pas de stationnement sur voirie tagué dans OSM
