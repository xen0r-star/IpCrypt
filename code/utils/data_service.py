from utils import decoupes_sqlite
from utils.auth_service import _run, ecrire_audit

# ══════════════════════════════════════════════
# F1 : format d'une IP          -> ip_format_checks      (entrée + RÉSULTAT du contrôle)
# F2 : classe d'une IP          -> ip_class_checks       (entrée)
# F3 : masque de classe         -> ip_class_mask_checks  (entrée)
# F4 : réseau / sous-réseau     -> network_calculations  (entrées)
# F5 : même réseau ?            -> same_network_checks   (entrées + dernier modificateur)
# F6 : découpe en sous-réseaux  -> subnet_splits         (entrées + dernier modificateur) — SQLite 3, voir utils/decoupes_sqlite.py
# ══════════════════════════════════════════════

LIMITE_HISTORIQUE = 100  # nombre maximum de lignes renvoyées aux écrans pour l'historique


def ip_en_texte(octets: list) -> str:
    """Convertit une liste d'octets (ex. ['010', '000', '000', '001']) en texte normalisé '10.0.0.1'."""
    return ".".join(str(int(o)) for o in octets)


# ══════════════════════════════════════════════
# Outils internes
# ══════════════════════════════════════════════

def _executer(nom: str, op) -> bool:
    """Exécute op(cur) via _run ; retourne False (et log console) en cas d'erreur."""
    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] {nom} ERREUR {type(e).__name__}: {e}")
        return False


def _lister(nom: str, requete: str) -> list:
    """Exécute une requête de lecture ; retourne [] (et log console) en cas d'erreur."""
    def op(cur):
        cur.execute(requete)
        return cur.fetchall()
    try:
        return _run(op)
    except Exception as e:
        print(f"[DB] {nom} ERREUR {type(e).__name__}: {e}")
        return []


# ══════════════════════════════════════════════
# F1 à F4 : entrées (F1 : + résultat)
# ══════════════════════════════════════════════

def enregistrer_format_ip(ip: str, est_valide: bool, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 1 : stocke l'IP saisie (brute, même invalide) ET le résultat du contrôle de format."""
    def op(cur):
        with cur.connection.transaction():
            # 1) Valeurs déjà en base : rien à faire
            cur.execute("SELECT check_id FROM ip_format_checks WHERE ip=%s AND is_valid=%s", (ip, est_valide))
            if cur.fetchone() is not None:
                return

            # 2) Modification d'un enregistrement rechargé depuis l'historique
            if record_id is not None:
                cur.execute("SELECT ip, is_valid FROM ip_format_checks WHERE check_id=%s", (record_id,))
                ancien = cur.fetchone()
                if ancien is not None:
                    cur.execute("UPDATE ip_format_checks SET ip=%s, is_valid=%s WHERE check_id=%s",
                                (ip, est_valide, record_id))
                    ecrire_audit(cur, "ip_format_checks", "UPDATE", record_id, user_id,
                                 f"avant : ip={ancien['ip']}, is_valid={ancien['is_valid']} -> après : ip={ip}, is_valid={est_valide}")
                    return

            # 3) Nouvel enregistrement
            cur.execute("INSERT INTO ip_format_checks (ip, is_valid) VALUES (%s, %s) RETURNING check_id",
                        (ip, est_valide))
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "ip_format_checks", "INSERT", nouveau_id, user_id,
                         f"ip={ip}, is_valid={est_valide}")
            
    return _executer("enregistrer_format_ip", op)


def enregistrer_classe_ip(ip: str, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 2 : stocke uniquement l'IP saisie (le résultat se recalcule)."""
    def op(cur):
        with cur.connection.transaction():
            # 1) Valeurs déjà en base : rien à faire
            cur.execute("SELECT check_id FROM ip_class_checks WHERE ip=%s", (ip,))
            if cur.fetchone() is not None:
                return

            # 2) Modification d'un enregistrement rechargé depuis l'historique
            if record_id is not None:
                cur.execute("SELECT ip FROM ip_class_checks WHERE check_id=%s", (record_id,))
                ancien = cur.fetchone()
                if ancien is not None:
                    cur.execute("UPDATE ip_class_checks SET ip=%s WHERE check_id=%s", (ip, record_id))
                    ecrire_audit(cur, "ip_class_checks", "UPDATE", record_id, user_id,
                                 f"avant : ip={ancien['ip']} -> après : ip={ip}")
                    return

            # 3) Nouvel enregistrement
            cur.execute("INSERT INTO ip_class_checks (ip) VALUES (%s) RETURNING check_id", (ip,))
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "ip_class_checks", "INSERT", nouveau_id, user_id, f"ip={ip}")

    return _executer("enregistrer_classe_ip", op)


def enregistrer_masque_classe_ip(ip: str, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 3 : stocke uniquement l'IP saisie (le résultat se recalcule)."""
    def op(cur):
        with cur.connection.transaction():
            # 1) Valeurs déjà en base : rien à faire
            cur.execute("SELECT check_id FROM ip_class_mask_checks WHERE ip=%s", (ip,))
            if cur.fetchone() is not None:
                return

            # 2) Modification d'un enregistrement rechargé depuis l'historique
            if record_id is not None:
                cur.execute("SELECT ip FROM ip_class_mask_checks WHERE check_id=%s", (record_id,))
                ancien = cur.fetchone()
                if ancien is not None:
                    cur.execute("UPDATE ip_class_mask_checks SET ip=%s WHERE check_id=%s", (ip, record_id))
                    ecrire_audit(cur, "ip_class_mask_checks", "UPDATE", record_id, user_id,
                                 f"avant : ip={ancien['ip']} -> après : ip={ip}")
                    return

            # 3) Nouvel enregistrement
            cur.execute("INSERT INTO ip_class_mask_checks (ip) VALUES (%s) RETURNING check_id", (ip,))
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "ip_class_mask_checks", "INSERT", nouveau_id, user_id, f"ip={ip}")
            
    return _executer("enregistrer_masque_classe_ip", op)


def enregistrer_reseau(ip: str, masque: str, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 4 : stocke IP + masque (pas les résultats). Pas de dernier modificateur pour cette fonctionnalité."""
    def op(cur):
        with cur.connection.transaction():
            # 1) Valeurs déjà en base : rien à faire
            cur.execute("SELECT calc_id FROM network_calculations WHERE ip_address=%s AND subnet_mask=%s",
                        (ip, masque))
            if cur.fetchone() is not None:
                return

            # 2) Modification d'un enregistrement rechargé depuis l'historique
            if record_id is not None:
                cur.execute("SELECT ip_address, subnet_mask FROM network_calculations WHERE calc_id=%s", (record_id,))
                ancien = cur.fetchone()
                if ancien is not None:
                    cur.execute("UPDATE network_calculations SET ip_address=%s, subnet_mask=%s WHERE calc_id=%s",
                                (ip, masque, record_id))
                    ecrire_audit(cur, "network_calculations", "UPDATE", record_id, user_id,
                                 f"avant : ip_address={ancien['ip_address']}, subnet_mask={ancien['subnet_mask']} "
                                 f"-> après : ip_address={ip}, subnet_mask={masque}")
                    return

            # 3) Nouvel enregistrement
            cur.execute("INSERT INTO network_calculations (ip_address, subnet_mask) VALUES (%s, %s) RETURNING calc_id",
                        (ip, masque))
            nouveau_id = cur.fetchone()["calc_id"]
            ecrire_audit(cur, "network_calculations", "INSERT", nouveau_id, user_id,
                         f"ip_address={ip}, subnet_mask={masque}")
    return _executer("enregistrer_reseau", op)


# ══════════════════════════════════════════════
# F5 et F6 : entrées + dernier modificateur
# ══════════════════════════════════════════════

def enregistrer_meme_reseau(ip1: str, mask1: str, ip2: str, mask2: str, user_id: int, record_id=None) -> bool:
    """
    Fonctionnalité 5 : stocke les deux couples IP/masque et le dernier modificateur.
    Si ces valeurs existent déjà, seul le dernier modificateur est mis à jour.
    """
    def op(cur):
        with cur.connection.transaction():
            details = f"ip1={ip1}, mask1={mask1}, ip2={ip2}, mask2={mask2}"

            # 1) Valeurs déjà en base : pas de doublon, on met à jour le dernier modificateur
            cur.execute("SELECT check_id FROM same_network_checks WHERE ip1=%s AND mask1=%s AND ip2=%s AND mask2=%s",
                        (ip1, mask1, ip2, mask2))
            identique = cur.fetchone()
            if identique is not None:
                cur.execute("UPDATE same_network_checks SET last_modified_by=%s, last_modified_at=NOW() WHERE check_id=%s",
                            (user_id, identique["check_id"]))
                ecrire_audit(cur, "same_network_checks", "UPDATE", identique["check_id"], user_id, details)
                return

            # 2) Modification d'un enregistrement rechargé depuis l'historique
            if record_id is not None:
                cur.execute("SELECT ip1, mask1, ip2, mask2 FROM same_network_checks WHERE check_id=%s", (record_id,))
                ancien = cur.fetchone()
                if ancien is not None:
                    cur.execute(
                        "UPDATE same_network_checks SET ip1=%s, mask1=%s, ip2=%s, mask2=%s, "
                        "last_modified_by=%s, last_modified_at=NOW() WHERE check_id=%s",
                        (ip1, mask1, ip2, mask2, user_id, record_id),
                    )
                    ecrire_audit(cur, "same_network_checks", "UPDATE", record_id, user_id,
                                 f"avant : ip1={ancien['ip1']}, mask1={ancien['mask1']}, ip2={ancien['ip2']}, mask2={ancien['mask2']} "
                                 f"-> après : {details}")
                    return

            # 3) Nouvel enregistrement
            cur.execute(
                "INSERT INTO same_network_checks (ip1, mask1, ip2, mask2, last_modified_by) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING check_id",
                (ip1, mask1, ip2, mask2, user_id),
            )
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "same_network_checks", "INSERT", nouveau_id, user_id, details)
    return _executer("enregistrer_meme_reseau", op)


def enregistrer_decoupe_sous_reseaux(adresse_reseau: str, cidr_base: int, nb_sous_reseaux: int, user_id: int, record_id=None) -> bool:
    """
    Fonctionnalité 6 (découpe en sous-réseaux) : stocke uniquement les entrées de la découpe et le dernier modificateur,
    dans la base SQLite 3 (utils/decoupes_sqlite.py). Si ces valeurs existent déjà, seul le dernier modificateur est mis à jour.
    La modification est aussi tagguée (numéro d'employé) dans le journal audit_log de PostgreSQL.
    """
    if user_id is None:
        print("[SQLite] enregistrer_decoupe_sous_reseaux ERREUR : le numéro d'employé est obligatoire.")
        return False
    try:
        operation, id_ligne, details = decoupes_sqlite.enregistrer(adresse_reseau, cidr_base, nb_sous_reseaux, user_id, record_id)
    except Exception as e:
        print(f"[SQLite] enregistrer_decoupe_sous_reseaux ERREUR {type(e).__name__}: {e}")
        return False

    # Les deux bases ne partagent pas de transaction : la découpe est déjà enregistrée, l'audit est écrit juste après.
    def audit(cur):
        with cur.connection.transaction():
            ecrire_audit(cur, "subnet_splits", operation, id_ligne, user_id, details)
    _executer("audit_decoupe_sous_reseaux", audit)
    return True


# ══════════════════════════════════════════════
# Lecture : historique affiché par les écrans (chaque ligne contient une clé 'id')
# ══════════════════════════════════════════════

def lister_formats_ip() -> list:
    """F1 : [{'id', 'ip', 'resultat'}, ...] du plus récent au plus ancien."""
    return _lister("lister_formats_ip",
                   "SELECT check_id AS id, ip, CASE WHEN is_valid THEN 'Valide' ELSE 'Invalide' END AS resultat "
                   f"FROM ip_format_checks ORDER BY check_id DESC LIMIT {LIMITE_HISTORIQUE}")


def lister_classes_ip() -> list:
    """F2 : [{'id', 'ip'}, ...] du plus récent au plus ancien."""
    return _lister("lister_classes_ip",
                   f"SELECT check_id AS id, ip FROM ip_class_checks ORDER BY check_id DESC LIMIT {LIMITE_HISTORIQUE}")


def lister_masques_classe_ip() -> list:
    """F3 : [{'id', 'ip'}, ...] du plus récent au plus ancien."""
    return _lister("lister_masques_classe_ip",
                   f"SELECT check_id AS id, ip FROM ip_class_mask_checks ORDER BY check_id DESC LIMIT {LIMITE_HISTORIQUE}")


def lister_reseaux() -> list:
    """F4 : [{'id', 'ip', 'masque'}, ...] du plus récent au plus ancien."""
    return _lister("lister_reseaux",
                   f"SELECT calc_id AS id, ip_address AS ip, subnet_mask AS masque FROM network_calculations ORDER BY calc_id DESC LIMIT {LIMITE_HISTORIQUE}")


def lister_memes_reseaux() -> list:
    """F5 : [{'id', 'ip1', 'mask1', 'ip2', 'mask2', 'modifie_par', 'modifie_le'}, ...]."""
    return _lister("lister_memes_reseaux",
                   "SELECT s.check_id AS id, s.ip1, s.mask1, s.ip2, s.mask2, "
                   "u.username AS modifie_par, s.last_modified_at AS modifie_le "
                   "FROM same_network_checks s LEFT JOIN users u ON u.user_id = s.last_modified_by "
                   f"ORDER BY s.last_modified_at DESC, s.check_id DESC LIMIT {LIMITE_HISTORIQUE}")


def _noms_utilisateurs(ids) -> dict:
    """{user_id: username} pour les numéros d'employé donnés (table users de PostgreSQL) ; {} en cas d'erreur."""
    if not ids:
        return {}

    def op(cur):
        cur.execute("SELECT user_id, username FROM users WHERE user_id = ANY(%s)", (list(ids),))
        return {ligne["user_id"]: ligne["username"] for ligne in cur.fetchall()}
    try:
        return _run(op)
    except Exception as e:
        print(f"[DB] _noms_utilisateurs ERREUR {type(e).__name__}: {e}")
        return {}


def lister_decoupes_sous_reseaux() -> list:
    """F6 (découpe) : [{'id', 'reseau', 'cidr', 'nb_sous_reseaux', 'modifie_par', 'modifie_le'}, ...] depuis SQLite 3."""
    try:
        lignes = decoupes_sqlite.lister(LIMITE_HISTORIQUE)
    except Exception as e:
        print(f"[SQLite] lister_decoupes_sous_reseaux ERREUR {type(e).__name__}: {e}")
        return []
    noms = _noms_utilisateurs({ligne["modifie_par_id"] for ligne in lignes})
    for ligne in lignes:
        numero = ligne.pop("modifie_par_id")
        ligne["modifie_par"] = noms.get(numero, f"n° {numero}")
    return lignes