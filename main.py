"""
Outil de pilotage des campagnes de sensibilisation au phishing via GoPhish.

CE SCRIPT PILOTE UNIQUEMENT L'API DE TON INSTANCE GOPHISH, déjà installée et
configurée par toi. Il ne fabrique aucun mécanisme de phishing "depuis zéro" :
il automatise la création de groupes, templates, pages, profils SMTP et
campagnes via l'API officielle documentée de GoPhish.

Toute campagne doit :
  - ne cibler que des utilisateurs de ta propre organisation,
  - être autorisée par la direction / RSSI,
  - avoir un objectif pédagogique clairement communiqué a posteriori.

Usage :
    python main.py list-groups
    python main.py create-group --name "Equipe Marketing" --csv targets.csv
    python main.py list-templates
    python main.py list-pages
    python main.py list-smtp
    python main.py launch --name "..." --template "..." --page "..." --smtp "..." --groups "G1,G2" --url http://...
    python main.py report --campaign-id 3 --output rapport.xlsx
"""

import argparse
import csv
import sys

from gophish_client import GoPhishClient
from reporting import build_excel_report


def load_targets_csv(path: str):
    """CSV attendu avec colonnes: email,first_name,last_name,position"""
    targets = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            targets.append({
                "email": row.get("email", "").strip(),
                "first_name": row.get("first_name", "").strip(),
                "last_name": row.get("last_name", "").strip(),
                "position": row.get("position", "").strip(),
            })
    return targets


def cmd_list_groups(args):
    client = GoPhishClient()
    for g in client.list_groups():
        print(f"- {g['name']} (id={g['id']}, {len(g.get('targets', []))} destinataires)")


def cmd_create_group(args):
    client = GoPhishClient()
    targets = load_targets_csv(args.csv)
    result = client.create_group(args.name, targets)
    print(f"Groupe créé : {result['name']} (id={result['id']}, {len(targets)} destinataires)")


def cmd_list_templates(args):
    client = GoPhishClient()
    for t in client.list_templates():
        print(f"- {t['name']} (id={t['id']}) — sujet : {t.get('subject','')}")


def cmd_list_pages(args):
    client = GoPhishClient()
    for p in client.list_pages():
        print(f"- {p['name']} (id={p['id']})")


def cmd_list_smtp(args):
    client = GoPhishClient()
    for s in client.list_sending_profiles():
        print(f"- {s['name']} (id={s['id']}) — host : {s.get('host','')}")


def cmd_launch(args):
    client = GoPhishClient()
    groups = [g.strip() for g in args.groups.split(",")]
    result = client.create_campaign(
        name=args.name,
        template_name=args.template,
        page_name=args.page,
        smtp_name=args.smtp,
        group_names=groups,
        landing_url=args.url,
        launch_date=args.launch_date,
    )
    print(f"Campagne créée : {result['name']} (id={result['id']}, statut={result.get('status')})")


def cmd_report(args):
    build_excel_report(args.campaign_id, args.output)


def main():
    parser = argparse.ArgumentParser(description="Pilotage de campagnes GoPhish (sensibilisation phishing interne)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-groups", help="Lister les groupes de destinataires").set_defaults(func=cmd_list_groups)
    sub.add_parser("list-templates", help="Lister les templates d'email").set_defaults(func=cmd_list_templates)
    sub.add_parser("list-pages", help="Lister les pages d'atterrissage").set_defaults(func=cmd_list_pages)
    sub.add_parser("list-smtp", help="Lister les profils d'envoi SMTP").set_defaults(func=cmd_list_smtp)

    p1 = sub.add_parser("create-group", help="Créer un groupe de destinataires depuis un CSV")
    p1.add_argument("--name", required=True)
    p1.add_argument("--csv", required=True, help="CSV avec colonnes email,first_name,last_name,position")
    p1.set_defaults(func=cmd_create_group)

    p2 = sub.add_parser("launch", help="Lancer une campagne")
    p2.add_argument("--name", required=True)
    p2.add_argument("--template", required=True, help="Nom du template déjà créé dans GoPhish")
    p2.add_argument("--page", required=True, help="Nom de la landing page déjà créée")
    p2.add_argument("--smtp", required=True, help="Nom du profil d'envoi déjà créé")
    p2.add_argument("--groups", required=True, help="Noms de groupes séparés par des virgules")
    p2.add_argument("--url", required=True, help="URL publique de ton serveur GoPhish (landing page)")
    p2.add_argument("--launch-date", default=None, help="ISO8601, optionnel (sinon lancement immédiat)")
    p2.set_defaults(func=cmd_launch)

    p3 = sub.add_parser("report", help="Générer le rapport Excel d'une campagne")
    p3.add_argument("--campaign-id", type=int, required=True)
    p3.add_argument("--output", default="rapport_campagne.xlsx")
    p3.set_defaults(func=cmd_report)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
