from utils.auth_service import _run, ecrire_audit

# ══════════════════════════════════════════════
# F1 : format d'une IP          -> ip_format_checks      (entrée + RÉSULTAT du contrôle)
# F2 : classe d'une IP          -> ip_class_checks       (entrée)
# F3 : masque de classe         -> ip_class_mask_checks  (entrée)
# F4 : réseau / sous-réseau     -> network_calculations  (entrées)
# F5 : même réseau ?            -> same_network_checks   (entrées + dernier modificateur)
# F6 : découpe en sous-réseaux  -> subnet_splits         (entrées + dernier modificateur)
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


def _enregistrer(cur, table: str, col_id: str, valeurs: dict, user_id: int,
                 record_id=None, avec_modificateur: bool = False) -> None:
    """
    Règle commune à toutes les fonctionnalités (à appeler dans une transaction). table/col_id/colonnes sont des
    constantes du code (jamais une saisie utilisateur), seules les valeurs passent en paramètres SQL.

      - record_id fourni (enregistrement rechargé depuis l'historique) et valeurs changées -> UPDATE de cet enregistrement.
      - valeurs déjà présentes en base -> pas de doublon : on ne fait que mettre à jour le dernier modificateur
        (uniquement pour les tables qui en ont un).
      - sinon -> INSERT.
    Chaque INSERT/UPDATE est tagué dans audit_log avec le numéro d'employé.
    """
    colonnes = list(valeurs)
    condition = " AND ".join(f"{c}=%s" for c in colonnes)
    params = tuple(valeurs[c] for c in colonnes)
    details = ", ".join(f"{c}={valeurs[c]}" for c in colonnes)

    cur.execute(f"SELECT {col_id} FROM {table} WHERE {condition}", params)
    identique = cur.fetchone()

    # 1) Modification d'un enregistrement rechargé depuis l'historique
    if record_id is not None and identique is None:
        cur.execute(f"SELECT {', '.join(colonnes)} FROM {table} WHERE {col_id}=%s", (record_id,))
        ancien = cur.fetchone()
        if ancien is not None:
            affectations = ", ".join(f"{c}=%s" for c in colonnes)
            params_maj = params
            if avec_modificateur:
                affectations += ", last_modified_by=%s, last_modified_at=NOW()"
                params_maj = params_maj + (user_id,)
            cur.execute(f"UPDATE {table} SET {affectations} WHERE {col_id}=%s", params_maj + (record_id,))
            avant = ", ".join(f"{c}={ancien[c]}" for c in colonnes)
            ecrire_audit(cur, table, "UPDATE", record_id, user_id, f"avant : {avant} -> après : {details}")
            return
        # l'enregistrement n'existe plus (supprimé entre-temps) : on retombe sur un INSERT

    # 2) Valeurs déjà connues : pas de doublon
    if identique is not None:
        if avec_modificateur:
            cur.execute(
                f"UPDATE {table} SET last_modified_by=%s, last_modified_at=NOW() WHERE {col_id}=%s",
                (user_id, identique[col_id]),
            )
            ecrire_audit(cur, table, "UPDATE", identique[col_id], user_id, details)
        return  # sans modificateur : rien n'a changé, rien à tagger

    # 3) Nouvel enregistrement
    colonnes_insert = colonnes + (["last_modified_by"] if avec_modificateur else [])
    params_insert = params + ((user_id,) if avec_modificateur else ())
    marqueurs = ", ".join(["%s"] * len(colonnes_insert))
    cur.execute(
        f"INSERT INTO {table} ({', '.join(colonnes_insert)}) VALUES ({marqueurs}) RETURNING {col_id}",
        params_insert,
    )
    nouveau_id = cur.fetchone()[col_id]
    ecrire_audit(cur, table, "INSERT", nouveau_id, user_id, details)


# ══════════════════════════════════════════════
# F1 à F4 : entrées (F1 : + résultat)
# ══════════════════════════════════════════════

def enregistrer_format_ip(ip: str, est_valide: bool, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 1 : stocke l'IP saisie (brute, même invalide) ET le résultat du contrôle de format."""
    def op(cur):
        with cur.connection.transaction():
            _enregistrer(cur, "ip_format_checks", "check_id", {"ip": ip, "is_valid": est_valide}, user_id, record_id)
    return _executer("enregistrer_format_ip", op)


def enregistrer_classe_ip(ip: str, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 2 : stocke uniquement l'IP saisie (le résultat se recalcule)."""
    def op(cur):
        with cur.connection.transaction():
            _enregistrer(cur, "ip_class_checks", "check_id", {"ip": ip}, user_id, record_id)
    return _executer("enregistrer_classe_ip", op)


def enregistrer_masque_classe_ip(ip: str, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 3 : stocke uniquement l'IP saisie (le résultat se recalcule)."""
    def op(cur):
        with cur.connection.transaction():
            _enregistrer(cur, "ip_class_mask_checks", "check_id", {"ip": ip}, user_id, record_id)
    return _executer("enregistrer_masque_classe_ip", op)


# ══════════════════════════════════════════════
# F4 : entrées ; F5 et F6 : entrées + dernier modificateur
# ══════════════════════════════════════════════

def enregistrer_reseau(ip: str, masque: str, user_id: int, record_id=None) -> bool:
    """Fonctionnalité 4 : stocke IP + masque (pas les résultats). Pas de dernier modificateur pour cette fonctionnalité."""
    def op(cur):
        with cur.connection.transaction():
            _enregistrer(cur, "network_calculations", "calc_id",
                         {"ip_address": ip, "subnet_mask": masque}, user_id, record_id)
    return _executer("enregistrer_reseau", op)


def enregistrer_meme_reseau(ip1: str, mask1: str, ip2: str, mask2: str, user_id: int, record_id=None) -> bool:
    """
    Fonctionnalité 5 : stocke les deux couples IP/masque et le dernier modificateur.
    Si ces valeurs existent déjà, seul le dernier modificateur est mis à jour.
    """
    def op(cur):
        with cur.connection.transaction():
            _enregistrer(cur, "same_network_checks", "check_id",
                         {"ip1": ip1, "mask1": mask1, "ip2": ip2, "mask2": mask2},
                         user_id, record_id, avec_modificateur=True)
    return _executer("enregistrer_meme_reseau", op)


def enregistrer_decoupe_sous_reseaux(adresse_reseau: str, cidr_base: int, nb_sous_reseaux: int, user_id: int, record_id=None) -> bool:
    """
    Fonctionnalité 6 (découpe en sous-réseaux) : stocke uniquement les entrées de la découpe et le dernier modificateur.
    Si ces valeurs existent déjà, seul le dernier modificateur est mis à jour.
    """
    def op(cur):
        with cur.connection.transaction():
            _enregistrer(cur, "subnet_splits", "split_id",
                         {"network_address": adresse_reseau, "base_cidr": cidr_base, "requested_subnets": nb_sous_reseaux},
                         user_id, record_id, avec_modificateur=True)
    return _executer("enregistrer_decoupe_sous_reseaux", op)


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


def lister_decoupes_sous_reseaux() -> list:
    """F6 (découpe) : [{'id', 'reseau', 'cidr', 'nb_sous_reseaux', 'modifie_par', 'modifie_le'}, ...]."""
    return _lister("lister_decoupes_sous_reseaux",
                   "SELECT d.split_id AS id, d.network_address AS reseau, d.base_cidr AS cidr, "
                   "d.requested_subnets AS nb_sous_reseaux, u.username AS modifie_par, d.last_modified_at AS modifie_le "
                   "FROM subnet_splits d LEFT JOIN users u ON u.user_id = d.last_modified_by "
                   f"ORDER BY d.last_modified_at DESC, d.split_id DESC LIMIT {LIMITE_HISTORIQUE}")
