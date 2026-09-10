# Outil de pilotage — Sensibilisation au phishing avec GoPhish (100% gratuit)

Cet outil pilote GoPhish (https://getgophish.com), un framework open
source de simulation de phishing conçu pour la sensibilisation en entreprise.
Aucune dépendance à Microsoft, aucun abonnement requis.


- Open source, gratuit, code source auditable (Go).
- Utilisé par de nombreuses équipes sécurité et pentesters dans un cadre légal.


- N'utilise ceci que sur ta propre organisation, avec l'accord explicite
  de la direction / RH / RSSI.
- Ne cible jamais des personnes extérieures à ton organisation.
- Informe les employés a posteriori de l'objectif pédagogique.
- Ne stocke jamais de vrais mots de passe : configure tes pages pour capturer
- Vérifie la légalité de ce type de test dans ta juridiction
## Étape 1 — Installer GoPhish (serveur)

```bash
# Télécharger le binaire officiel (Linux/macOS/Windows) :
# https://github.com/gophish/gophish/releases

wget https://github.com/gophish/gophish/releases/latest/download/gophish-vX.Y.Z-linux-64bit.zip
unzip gophish-vX.Y.Z-linux-64bit.zip
cd gophish
chmod +x gophish
./gophish
```

Au premier lancement, GoPhish affiche dans les logs un mot de passe admin
temporaire. Connecte-toi sur `https://localhost:3333` (interface admin) avec
`admin` / ce mot de passe, puis change-le immédiatement.

Récupère ensuite ta clé API dans **Settings > API Key**.

## Étape 2 — Configurer l'outil Python

```bash
pip install -r requirements.txt
cp .env.example .env
# éditer .env :
#   GOPHISH_API_URL=https://localhost:3333
#   GOPHISH_API_KEY=<ta clé>
#   GOPHISH_VERIFY_SSL=false   (true si tu as un vrai certificat)
```

## Étape 3 — Créer les briques de campagne (via l'interface GoPhish, une fois)

Avant de scripter, crée au moins une fois dans l'interface web GoPhish (ou
via ce script) :
1. Un **profil d'envoi SMTP** (le serveur mail qui enverra les faux emails —
   utilise un compte dédié, jamais votre vraie messagerie de production).
2. Un **template d'email** (contenu du mail piège, réaliste mais pédagogique).
3. Une **landing page** (page affichée après le clic — idéalement une page
   qui explique immédiatement qu'il s'agissait d'un test de sensibilisation).
4. Un **groupe** de destinataires internes.

## Étape 4 — Utiliser l'outil

```bash
# Vérifier ce qui existe déjà
python main.py list-smtp
python main.py list-templates
python main.py list-pages
python main.py list-groups

# Créer un groupe depuis un CSV (email,first_name,last_name,position)
python main.py create-group --name "Service Compta" --csv targets_example.csv

# Lancer une campagne
python main.py launch \
  --name "Sensibilisation Q4 2026" \
  --template "Facture urgente" \
  --page "Page de sensibilisation" \
  --smtp "SMTP interne" \
  --groups "Service Compta" \
  --url "http://votre-serveur-gophish:80"

# Générer le rapport une fois la campagne terminée
python main.py report --campaign-id 3 --output rapport_q4.xlsx
```

Le rapport Excel contient le détail par personne (email ouvert, lien cliqué,
données soumises, mail signalé) et un onglet de synthèse avec les
pourcentages globaux — utile pour présenter les résultats à la direction et
identifier qui recycler en formation.
