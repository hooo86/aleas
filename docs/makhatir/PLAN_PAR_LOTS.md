# MAKHATIR MAP – Cahier des charges consolidé et plan de développement par lots

Sources : fiche technique « MAKHATIR MAP » (plateforme + chatbot), formulaire actuel
`makhatir.lnhc.dz/formm`, capture de la carte `carte_interactive_aléas`, et les exigences
ajoutées : projets lus dans **Odoo**, comptes utilisateurs **liés à Active Directory**,
périmètre d'accès calqué sur la **hiérarchie des unités d'organisation (OU)**.

Les charges sont des **estimations** en jours-homme (j/h) pour un développeur confirmé ;
elles sont à réviser après le Lot 0. Les points marqués **[à confirmer]** bloquent ou
modifient un lot tant qu'ils ne sont pas tranchés.

---

## 1. Exigences consolidées

### 1.1 Organisation et périmètre d'accès
- Hiérarchie : **DG → DR (DRC, DRE, DRO, DRSE, DRSO) → Unité → Antenne**. Le formulaire actuel
  contient déjà le niveau Antenne (ex. Unité BEJAIA → antennes SETIF, JIJEL).
- La hiérarchie est **gérée dans l'application** (table `org_unit`, écran d'administration),
  et non plus codée en dur dans le JavaScript comme aujourd'hui. Elle ne dépend pas des unités
  d'organisation (OU) de l'Active Directory.
- **Les OU de l'AD servent uniquement à l'importation des utilisateurs** : chaque entité peut
  porter, à titre facultatif, le DN de l'OU correspondante (`ad_dn`). Lors d'un import, l'OU du
  compte AD sert à **proposer** l'entité de l'utilisateur ; l'administrateur confirme ou
  corrige. Ensuite, l'entité est une donnée de l'application : elle n'est jamais recalculée
  depuis l'AD (ni à la connexion, ni par synchronisation) et ne change que par une action d'un
  administrateur, tracée dans l'audit.
- **Règle d'accès** : un utilisateur voit et manipule uniquement les données de son entité
  **et de ses entités descendantes**. Un agent de la DG voit tout ; un agent de la DRE voit la
  DRE, ses unités et leurs antennes ; un agent d'une unité ne voit ni l'unité voisine ni sa DR.
- Le filtrage se fait **côté serveur** sur chaque requête (liste, détail, carte, export,
  rapport, chatbot), jamais seulement dans l'interface.

### 1.2 Authentification
- Une **base d'utilisateurs locale** est la référence : seul un utilisateur présent et actif
  dans cette base peut se connecter, même s'il possède un compte AD valide.
- Chaque utilisateur interne est **lié à un compte AD** (`sAMAccountName`/UPN + `objectGUID`
  pour survivre aux renommages). Il s'authentifie avec son mot de passe AD, vérifié par
  **bind LDAPS (port 636)** ; l'application ne stocke jamais ce mot de passe.
- Compte AD désactivé, expiré ou verrouillé ⇒ le bind échoue et la connexion est refusée.
  L'AD n'intervient pas dans les droits ni dans l'entité de l'utilisateur.
- Les **clients** (Espace Client Étude, Espace Client Aléas) ne sont pas dans l'AD : comptes
  locaux à mot de passe haché (Argon2/PBKDF2), activation par lien e-mail, MFA recommandée.
- Limitation des tentatives, journalisation des connexions, sessions sécurisées, HTTPS
  obligatoire (le site actuel est servi en HTTP : « Non sécurisé »).

### 1.3 Projets Odoo
- La liste des projets (études) vient d'Odoo (modèle `project.project`), lue via l'API
  XML-RPC/JSON-RPC avec un **compte technique en lecture seule**.
- Données récupérées : identifiant Odoo, code, intitulé, client (`res.partner`), entité
  responsable, état/étape, dates, localisation si disponible.
- Copie locale synchronisée (planifiée + à la demande), pour que l'application reste
  utilisable si Odoo est indisponible et pour pouvoir filtrer par périmètre.
- **Correspondance projet → entité [à confirmer]** : société Odoo, compte analytique,
  département, ou champ personnalisé (`x_unite`). Sans cette règle, le périmètre des
  projets ne peut pas être appliqué.
- Un aléa peut être rattaché à un projet Odoo (optionnel : un aléa peut être relevé hors
  étude). Le client Odoo du projet détermine l'accès de l'Espace Client Étude.

### 1.4 Aléas (Phase 1 de la fiche technique)
Fiche site commune : entité (DR/unité/antenne, déduite de l'utilisateur), matricule agent
(déduit du compte), projet Odoo (optionnel), wilaya, commune, localité/lieu-dit,
coordonnées (point, et polygone de zone en option), date de visite, photo globale.

Un site porte **au moins un aléa**, chacun avec ses champs propres (repris du formulaire) :

| Aléa | Champs |
|---|---|
| Agressivité chimique | type (eau/sol), chlorures, sulfates, pH, photo |
| Inondation | **aucun champ aujourd'hui** – à définir [à confirmer] |
| Liquéfaction | épaisseur couche liquéfiable, zone sismique RPA 2024 (0–6), profondeur nappe, photo |
| Mouvement de terrain | type (glissement circulaire/plan, mouvement différentiel, fluage, coulée boueuse, éboulement/chute de blocs), nature du sol, origine, nappe, nb inclinomètres, pente, surface, épaisseur/profondeur ligne de glissement, photo |
| Cavités | profondeur, nature du sol, origine, mode de formation, méthode de détection, nappe, photo |
| Faille active | zone sismique RPA 2024, distance à la faille, photo |
| Sols compressibles | nature du sol, épaisseur, nappe, photo |
| Retrait-gonflement | nature du sol, nappe, photo |
| Sols gypseux | nature du sol, mode de dépôt, épaisseur, nappe, dissolution (oui/non), type de dissolution, photo |

Défauts du formulaire actuel à corriger dans la refonte :
- coordonnées annoncées « DD/MM/SS » mais remplies en degrés décimaux par la carte : stocker
  en décimal WGS84 (EPSG:4326), accepter la saisie DMS et la convertir, vérifier que le point
  tombe dans la commune choisie ;
- pH saisi au pas de 1 (il faut 0,1) ; unités des chlorures/sulfates à préciser (% ou mg/l) ;
- champs « profondeur de nappe / date de prélèvement » prévus dans le script mais absents du
  HTML (le choix « Présence de nappe = oui » n'ouvre rien) ;
- double confirmation à l'envoi (deux gestionnaires `submit`) ;
- DRS/unités/antennes codées en dur dans la page ; date de visite non obligatoire ;
- un seul jeu de champs par type d'aléa (impossible de saisir deux glissements sur un site).

### 1.5 Carte interactive
Fond OSM / satellite ; couches Wilaya, Commune, Failles actives, Zonage sismique RPA 2024
(0 à VI), Présence de gypse, Limite mondiale ; **un symbole SVG distinct par type d'aléa**,
repris dans la légende (dont « Aléas multiples », éboulement, glissement, tassement
différentiel) ; recherche wilaya/commune ; mesure ; géolocalisation ; fiche de l'aléa au
clic avec photos et rapports associés selon les droits ; filtres (type, entité, projet, date,
statut de validation). Les couches sont aujourd'hui des fichiers JS générés par qgis2web :
elles passent en base PostGIS et sont servies en tuiles vectorielles ou GeoJSON filtrés.

### 1.6 Espaces, sécurité, traçabilité
Espace interne LNHC, Espace Client Étude, Espace Client Aléas (fiche technique §4).
Séparation stricte des données clients, audit de toute saisie/modification/validation,
sauvegardes régulières (base + photos/documents), historique des versions des rapports.

---

## 2. Architecture cible

- **Backend** : Django + Django REST Framework + **GeoDjango / PostGIS** ; Celery + Redis pour
  les synchronisations AD/Odoo, la génération de rapports et l'indexation documentaire.
  Ce dépôt contient déjà un socle réutilisable : arborescence `OrgUnit` avec descendants,
  rôles et périmètres, journal d'audit immuable, limitation des tentatives de connexion.
- **Annuaire** : `ldap3` ; bind LDAPS pour vérifier le mot de passe à la connexion ; compte
  de service AD en lecture seule utilisé **uniquement à l'importation** (recherche des
  comptes, lecture de leur OU pour proposer l'entité).
- **Odoo** : client XML-RPC/JSON-RPC isolé dans un module `integrations/odoo`.
- **Frontend** : React + TypeScript, OpenLayers pour la carte, formulaires dynamiques par
  type d'aléa, interface en français (arabe prévu).
- **Stockage fichiers** : stockage objet (MinIO/S3) ou volume dédié, accès aux photos et
  rapports uniquement via des URL signées et contrôlées par le périmètre.
- **Périmètre** : hiérarchie stockée en chemin matérialisé (`ltree` ou `path` texte indexé)
  pour filtrer « entité + descendants » en une requête ; un `ScopedQuerysetMixin` unique
  appliqué à tous les points d'accès.

Modèle de données principal :
```
org_unit(id, parent_id, kind[DG|DR|UNITE|ANTENNE], code, name, path, active,
         ad_dn NULL)                                -- ad_dn : correspondance pour l'import seulement
user(id, username, kind[INTERNE|CLIENT], ad_guid, ad_upn, org_unit_id, matricule, role,
     active, imported_at, imported_by)
project(id, odoo_id UNIQUE, code, name, partner_odoo_id, org_unit_id, state, dates, synced_at)
client_account(user_id, partner_odoo_id)            -- Espace Client Étude
client_zone(user_id, geom)                          -- Espace Client Aléas
site(id, org_unit_id, project_id NULL, author_id, wilaya, commune, localite,
     geom POINT 4326, zone POLYGON NULL, date_visite, photo, status, validated_by, validated_at)
hazard(id, site_id, type, details JSONB validé par schéma, photo)
attachment(id, owner[site|hazard|project], file, kind, version)
ref_wilaya / ref_commune (code, nom, geom) ; ref_faille ; ref_zone_rpa2024 ; ref_gypse
audit_log(user, action, objet, avant, après, ip, date)
```

---

## 3. Plan de développement par lots

Chaque lot se termine par une démonstration et une recette sur ses critères d'acceptation.
Les lots 1 et 2 peuvent avancer en parallèle après le Lot 0.

### Lot 0 – Cadrage, accès et environnement (≈ 5 j/h)
- Ateliers : valider la hiérarchie (antennes incluses), les rôles, la règle projet → entité,
  les champs de l'aléa Inondation, les unités de mesure.
- Obtenir : domaine AD, contrôleurs, certificat LDAPS, base DN de recherche des comptes LNHC,
  compte de service en lecture (pour l'import) ; URL Odoo, version, base, compte technique en lecture, champs utilisés.
- Export de la base actuelle (formulaire Laravel) et des couches QGIS sources.
- Environnements dev/recette/prod (Docker), CI (tests + lint), dépôt dédié **[à confirmer :
  ce dépôt contient aujourd'hui l'application de pointage ; MAKHATIR doit-il vivre dans un
  dépôt séparé ?]**.
- **Livrables** : spécification validée, matrice des droits, accès techniques testés.

### Lot 1 – Socle sécurité : hiérarchie, utilisateurs, connexion AD, périmètre (≈ 13 j/h)
- Gestion de la hiérarchie dans l'application : écran d'administration des entités
  (création, renommage, déplacement, désactivation), chargement initial DG/DR/unités/antennes
  depuis la liste officielle, correspondance facultative entité ↔ OU AD pour l'import.
- **Import des utilisateurs depuis l'AD** : recherche (nom, matricule, UPN) ou import en lot
  d'une OU ; l'entité est proposée d'après l'OU du compte via la correspondance, puis
  confirmée ou corrigée par l'administrateur ; rôle applicatif choisi à l'import ; liaison
  par `objectGUID` ; rapport d'import (créés, ignorés, OU sans correspondance).
- Après l'import, l'entité et le rôle se gèrent uniquement dans l'application ; aucune
  synchronisation des OU, aucune mise à jour de l'entité à la connexion.
- Connexion interne par bind LDAPS ; connexion client par mot de passe local.
- Refus si : utilisateur absent ou inactif localement, compte AD désactivé/expiré/verrouillé.
- Filtrage « entité + descendants » appliqué par un mécanisme unique à toute l'API.
- Rôles proposés : administrateur, validateur, agent de saisie, consultation (internes) ;
  client étude, client aléas.
- Audit des connexions et des changements de droits ; HTTPS, cookies sécurisés.
- **Critères d'acceptation** : un agent d'unité ne peut lire, par aucune URL, une donnée d'une
  unité voisine ou de sa DR (tests automatisés sur chaque point d'accès) ; un compte AD
  désactivé ne se connecte plus ; un compte AD valide mais absent de la base est refusé ;
  déplacer un compte d'OU dans l'AD ne change ni l'entité ni les droits de l'utilisateur.

### Lot 2 – Intégration Odoo (≈ 8 j/h)
- Connecteur Odoo (authentification, lecture paginée de `project.project` et `res.partner`).
- Synchronisation incrémentale (`write_date`) planifiée + bouton « Actualiser », journal de
  synchronisation, alerte en cas d'échec.
- Rattachement projet → entité selon la règle retenue au Lot 0 ; projets non rattachés
  visibles des seuls administrateurs pour correction.
- Liste et recherche des projets filtrées par périmètre ; sélection d'un projet dans la fiche
  aléa.
- **Critères** : un projet créé dans Odoo apparaît après la synchronisation suivante, dans le
  seul périmètre de son entité ; une panne d'Odoo n'empêche pas la saisie.

### Lot 3 – Référentiels et saisie des aléas (≈ 15 j/h)
- Import en PostGIS des 58 wilayas, des communes, des failles actives, du zonage RPA 2024 et
  des zones de gypse.
- Formulaire refait : entité et matricule déduits du compte, wilaya → communes filtrées,
  saisie des coordonnées par clic carte, GPS du téléphone ou saisie DMS/décimale, contrôle de
  cohérence point/commune.
- Plusieurs aléas par site, plusieurs occurrences d'un même type, champs propres à chaque
  type validés côté serveur (schéma par type), photos par aléa (compression, EXIF GPS lu).
- Proposition automatique de la zone sismique RPA 2024 et de la distance à la faille la plus
  proche à partir des couches.
- Brouillon, modification par l'auteur tant que non validé ; interface utilisable sur
  tablette/téléphone sur le terrain.
- **Critères** : saisie complète d'un site multi-aléas sur mobile ; refus serveur des valeurs
  hors bornes ; aucun champ codé en dur côté client pour la hiérarchie.

### Lot 4 – Validation et vérification des données (≈ 6 j/h)
- Statuts : brouillon → soumis → validé / rejeté (motif obligatoire) ; validation par un
  validateur de l'entité ou d'une entité parente.
- Écran « Vérification des données » : file d'attente, filtres, historique des versions de la
  fiche, comparaison avant/après.
- Seules les données validées sont publiées vers les espaces clients et les rapports.
- **Critères** : chaque changement de statut est tracé (qui, quand, avant/après).

### Lot 5 – Carte interactive (≈ 12 j/h)
- Carte OpenLayers : fonds OSM/satellite, couches de référence du Lot 3, gestionnaire de
  couches et légende.
- Bibliothèque de symboles SVG par type d'aléa (et sous-type pour les mouvements de terrain),
  symbole « aléas multiples », regroupement des points aux petites échelles.
- Fiche au clic : attributs, photos, projet, rapports associés selon les droits.
- Recherche wilaya/commune/projet, filtres, mesure, géolocalisation, export de la vue.
- Données servies filtrées par périmètre côté serveur (GeoJSON par emprise ou tuiles
  vectorielles).
- **Critères** : la carte d'un agent n'affiche que les aléas de son périmètre ; fluide avec
  plusieurs milliers de points.

### Lot 6 – Rapports et documents (≈ 10 j/h)
- Rapport des aléas (PDF) par zone (wilaya, commune, polygone dessiné) ou par projet : carte,
  tableau des aléas, contexte sismique et géologique, photos ; modèle LNHC.
- Rattachement des rapports géotechniques existants à un aléa ou un projet, avec versions ;
  consultation depuis la fiche cartographique selon les droits.
- Exports CSV/Excel et GeoJSON/Shapefile filtrés par périmètre.
- **Critères** : un rapport généré ne contient aucune donnée hors du périmètre du demandeur.

### Lot 7 – Espaces clients (≈ 10 j/h)
- **Client Étude** : comptes liés au partenaire Odoo ; liste de ses projets, avancement
  (étape Odoo), données validées et rapport de son étude.
- **Client Aléas** : consultation de la carte et du rapport des aléas de la zone qui lui est
  attribuée.
- Création des comptes par un agent interne, invitation par e-mail, réinitialisation du mot de
  passe, MFA optionnelle.
- **Critères** : tests d'isolement entre deux clients ; aucune donnée non validée exposée.

### Lot 8 – Reprise de l'existant et mise en production (≈ 8 j/h)
- Migration des aléas et photos de l'application actuelle (conversion des coordonnées,
  correspondance des codes DRS/unité/antenne avec les entités, contrôle des doublons) avec rapport
  de reprise.
- Reverse proxy TLS, sauvegardes automatiques base + fichiers avec test de restauration,
  supervision (Zabbix déjà en place), journalisation centralisée.
- Guides utilisateur et administrateur, formation des référents par DR.
- **Critères** : restauration complète testée ; 100 % des fiches reprises ou listées en
  anomalie.

**Total Phase 1 (lots 0 à 8) : ≈ 87 j/h.**

### Phase 2 – Enrichissement de la base géotechnique (lots 9 à 11, ≈ 45 j/h)
- **Lot 9** – Sondages et lithologie : sondages géoréférencés liés aux projets, logs
  lithologiques, affichage du log, contexte géologique/hydrogéologique de la zone.
- **Lot 10** – Essais in situ (SPT, pressiomètre, CPT, PDL, piézomètre, géophysique :
  sismique, imagerie électrique, Down-Hole) et essais de laboratoire (identification,
  chimie, mécanique) : saisie, import Excel normalisé, contrôles de cohérence.
- **Lot 11** – Suivi d'avancement des études (étapes synchronisées avec Odoo), centralisation
  des documents techniques par projet.

### Phase 3 – Calculs et rapport géotechnique (lots 12 à 14, ≈ 60 j/h)
- **Lot 12** – Évaluations : potentiel de gonflement, de gypse, de liquéfaction (méthodes
  et normes de référence à fournir par le LNHC).
- **Lot 13** – Fondations : capacité portante, tassements, stabilité ; notes de calcul
  traçables (entrées, méthode, version).
- **Lot 14** – Rapport géotechnique final au modèle officiel LNHC : assemblage, conclusions
  et recommandations, circuit de contrôle/validation par ingénieur habilité, versions.

### Chatbot géotechnique (lots 15 à 17, ≈ 45 j/h, après le Lot 6)
- **Lot 15** – Base documentaire : import PDF/DOCX/XLSX/PPTX, métadonnées (titre, référence,
  organisme, date, version), statut en vigueur/remplacé/interne, activation, deux bases
  (normative et LNHC), droits par document.
- **Lot 16** – Traitement : extraction de texte, OCR des documents numérisés, découpage par
  titre/article/tableau, indexation vectorielle (pgvector) et plein texte.
- **Lot 17** – Assistant RAG : réponses citant document, article et page ; filtrage des
  documents et données **par le périmètre de l'utilisateur avant la recherche** ; distinction
  norme / recommandation / donnée plateforme / proposition IA ; signalement d'absence de
  source ; journal des questions et sources ; interface intégrée, français et arabe.
  **[à confirmer : modèle d'IA hébergé ou sur site, selon les contraintes de confidentialité.]**

---

## 4. Décisions à obtenir avant le démarrage

1. Liste officielle des entités (DG, DR, unités, antennes) et de leurs codes ; correspondance
   de chaque entité avec son OU AD pour l'import.
2. Règle de rattachement d'un projet Odoo à une entité ; version d'Odoo et mode d'accès API.
3. Rôles et matrice des droits (qui valide, qui crée les comptes clients).
4. Champs de l'aléa Inondation ; unités chlorures/sulfates ; listes de valeurs définitives.
5. Hébergement (sur site ou cloud), nom de domaine et certificat TLS.
6. Dépôt de code : séparé de l'application de pointage ou non.
