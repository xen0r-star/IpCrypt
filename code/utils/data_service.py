from utils.auth_service import _run, ecrire_audit

# ══════════════════════════════════════════════
# F1 : format d'une IP         -> ip_format_checks      (entrée + RÉSULTAT)
# F2 : classe d'une IP         -> ip_class_checks       (entrée)
# F3 : masque de classe        -> ip_class_mask_checks  (entrée)
# F4 : réseau / sous-réseau    -> network_calculations  (entrées)
# F5 : même réseau ?           -> same_network_checks   (entrées + dernier modificateur)
# F6 : découpe en sous-réseaux -> subnet_splits         (entrées + dernier modificateur)
# ══════════════════════════════════════════════


def ip_en_texte(octets: list) -> str:
    """Convertit une liste d'octets (ex. ['010', '000', '000', '001']) en texte normalisé '10.0.0.1'."""
    return ".".join(str(int(o)) for o in octets)


def enregistrer_format_ip(ip: str, est_valide: bool, user_id: int) -> bool:
    """Fonctionnalité 1 : stocke l'IP saisie (brute, même invalide) ET le résultat du contrôle de format."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute("SELECT check_id FROM ip_format_checks WHERE ip=%s AND is_valid=%s", (ip, est_valide))
            if cur.fetchone():
                return  # déjà enregistré : rien à modifier, rien à tagger
            
            cur.execute(
                "INSERT INTO ip_format_checks (ip, is_valid) VALUES (%s, %s) RETURNING check_id",
                (ip, est_valide),
            )
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "ip_format_checks", "INSERT", nouveau_id, user_id, f"ip={ip}, is_valid={est_valide}")

    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_format_ip ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_classe_ip(ip: str, user_id: int) -> bool:
    """Fonctionnalité 2 : stocke uniquement l'IP saisie (le résultat se recalcule)."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute("SELECT check_id FROM ip_class_checks WHERE ip=%s", (ip,))
            if cur.fetchone():
                return
            
            cur.execute("INSERT INTO ip_class_checks (ip) VALUES (%s) RETURNING check_id", (ip,))
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "ip_class_checks", "INSERT", nouveau_id, user_id, f"ip={ip}")

    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_classe_ip ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_masque_classe_ip(ip: str, user_id: int) -> bool:
    """Fonctionnalité 3 : stocke uniquement l'IP saisie (le résultat se recalcule)."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute("SELECT check_id FROM ip_class_mask_checks WHERE ip=%s", (ip,))
            if cur.fetchone():
                return
            
            cur.execute("INSERT INTO ip_class_mask_checks (ip) VALUES (%s) RETURNING check_id", (ip,))
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, "ip_class_mask_checks", "INSERT", nouveau_id, user_id, f"ip={ip}")

    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_masque_classe_ip ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_reseau(ip: str, masque: str, user_id: int) -> bool:
    """Fonctionnalité 4 : stocke uniquement IP + masque (pas de dernier modificateur pour cette fonctionnalité)."""
    def op(cur):
        with cur.connection.transaction():
            cur.execute(
                "SELECT calc_id FROM network_calculations WHERE ip_address=%s AND subnet_mask=%s",
                (ip, masque),
            )
            if cur.fetchone():
                return
            
            cur.execute(
                "INSERT INTO network_calculations (ip_address, subnet_mask) VALUES (%s, %s) RETURNING calc_id",
                (ip, masque),
            )
            nouveau_id = cur.fetchone()["calc_id"]
            ecrire_audit(cur, "network_calculations", "INSERT", nouveau_id, user_id, f"ip={ip}, masque={masque}")

    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_reseau ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_meme_reseau(ip1: str, mask1: str, ip2: str, mask2: str, user_id: int) -> bool:
    """
    Fonctionnalité 5 : stocke les deux couples IP/masque et le dernier modificateur.
    Si ces valeurs existent déjà, seul le dernier modificateur est mis à jour.
    """
    def op(cur):
        details = f"ip1={ip1}, mask1={mask1}, ip2={ip2}, mask2={mask2}"
        with cur.connection.transaction():
            cur.execute(
                "SELECT check_id FROM same_network_checks WHERE ip1=%s AND mask1=%s AND ip2=%s AND mask2=%s",
                (ip1, mask1, ip2, mask2),
            )

            ligne = cur.fetchone()
            if ligne:
                cur.execute(
                    "UPDATE same_network_checks SET last_modified_by=%s, last_modified_at=NOW() WHERE check_id=%s",
                    (user_id, ligne["check_id"]),
                )
                ecrire_audit(cur, "same_network_checks", "UPDATE", ligne["check_id"], user_id, details)
            else:
                cur.execute(
                    "INSERT INTO same_network_checks (ip1, mask1, ip2, mask2, last_modified_by) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING check_id",
                    (ip1, mask1, ip2, mask2, user_id),
                )
                nouveau_id = cur.fetchone()["check_id"]
                ecrire_audit(cur, "same_network_checks", "INSERT", nouveau_id, user_id, details)

    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_meme_reseau ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_decoupe_sous_reseaux(adresse_reseau: str, cidr_base: int, nb_sous_reseaux: int, user_id: int) -> bool:
    """
    Fonctionnalité 6 : stocke uniquement les entrées de la découpe et le dernier modificateur.
    Si ces valeurs existent déjà, seul le dernier modificateur est mis à jour.
    """
    def op(cur):
        details = f"reseau={adresse_reseau}, cidr={cidr_base}, sous_reseaux={nb_sous_reseaux}"
        with cur.connection.transaction():
            cur.execute(
                "SELECT split_id FROM subnet_splits "
                "WHERE network_address=%s AND base_cidr=%s AND requested_subnets=%s",
                (adresse_reseau, cidr_base, nb_sous_reseaux),
            )
            
            ligne = cur.fetchone()
            if ligne:
                cur.execute(
                    "UPDATE subnet_splits SET last_modified_by=%s, last_modified_at=NOW() WHERE split_id=%s",
                    (user_id, ligne["split_id"]),
                )
                ecrire_audit(cur, "subnet_splits", "UPDATE", ligne["split_id"], user_id, details)
            else:
                cur.execute(
                    "INSERT INTO subnet_splits (network_address, base_cidr, requested_subnets, last_modified_by) "
                    "VALUES (%s, %s, %s, %s) RETURNING split_id",
                    (adresse_reseau, cidr_base, nb_sous_reseaux, user_id),
                )
                nouveau_id = cur.fetchone()["split_id"]
                ecrire_audit(cur, "subnet_splits", "INSERT", nouveau_id, user_id, details)

    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_decoupe_sous_reseaux ERREUR {type(e).__name__}: {e}")
        return False