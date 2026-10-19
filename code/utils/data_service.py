from utils.auth_service import _run, ecrire_audit

def ip_en_texte(octets: list) -> str:
    """Convertit une liste d'octets (ex. ['010', '000', '000', '001']) en texte normalisé '10.0.0.1'."""
    return ".".join(str(int(o)) for o in octets)


def sauvegarder_masques(lignes: list, user_id: int) -> bool:
    """Fonctionnalité 1 : stocke le résultat (masques /8 à /30). N'écrit (et ne tague) que ce qui a changé."""
    def op(cur):
        with cur.connection.transaction():
            for cidr_texte, binaire, decimal in lignes:
                cidr = int(cidr_texte.lstrip("/"))
                cur.execute("SELECT mask_binary, mask_decimal FROM masks WHERE cidr=%s", (cidr,))
                existant = cur.fetchone()
                if existant is None:
                    cur.execute(
                        "INSERT INTO masks (cidr, mask_binary, mask_decimal) VALUES (%s, %s, %s)",
                        (cidr, binaire, decimal),
                    )
                    ecrire_audit(cur, "masks", "INSERT", cidr, user_id, f"/{cidr} = {decimal}")
                elif (existant["mask_binary"], existant["mask_decimal"]) != (binaire, decimal):
                    cur.execute(
                        "UPDATE masks SET mask_binary=%s, mask_decimal=%s WHERE cidr=%s",
                        (binaire, decimal, cidr),
                    )
                    ecrire_audit(cur, "masks", "UPDATE", cidr, user_id, f"/{cidr} = {decimal}")
    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] sauvegarder_masques ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_verification_ip(table: str, ip: str, user_id: int) -> bool:
    """
    Fonctionnalités 2, 3 et 4 : stocke uniquement l'entrée (pas le résultat), sans doublon.
    Pas de colonne « dernier modificateur » ici : l'identité est conservée dans audit_log.
    """
    if table not in ("ip_format_checks", "ip_class_checks", "ip_class_mask_checks"):
        print(f"[DB] enregistrer_verification_ip ERREUR : table non autorisée ({table})")
        return False

    def op(cur):
        with cur.connection.transaction():
            cur.execute(f"SELECT check_id FROM {table} WHERE ip=%s", (ip,))
            if cur.fetchone():
                return  # déjà enregistrée : rien à modifier, rien à tagger
            cur.execute(f"INSERT INTO {table} (ip) VALUES (%s) RETURNING check_id", (ip,))
            nouveau_id = cur.fetchone()["check_id"]
            ecrire_audit(cur, table, "INSERT", nouveau_id, user_id, f"ip={ip}")
    try:
        _run(op)
        return True
    except Exception as e:
        print(f"[DB] enregistrer_verification_ip ERREUR {type(e).__name__}: {e}")
        return False


def _enregistrer_avec_modificateur(cur, table: str, cle: str, valeurs: dict, user_id: int) -> None:
    """
    Fonctionnalités 5 et 6 : si les mêmes entrées existent déjà, met à jour le dernier modificateur
    (last_modified_by / last_modified_at) ; sinon insère une nouvelle ligne. Les deux cas sont tagués.
    """
    colonnes = list(valeurs)
    parametres = tuple(valeurs.values())
    condition = " AND ".join(f"{c}=%s" for c in colonnes)
    details = ", ".join(f"{c}={v}" for c, v in valeurs.items())

    with cur.connection.transaction():
        cur.execute(f"SELECT {cle} FROM {table} WHERE {condition}", parametres)
        ligne = cur.fetchone()
        if ligne:
            cur.execute(
                f"UPDATE {table} SET last_modified_by=%s, last_modified_at=NOW() WHERE {cle}=%s",
                (user_id, ligne[cle]),
            )
            ecrire_audit(cur, table, "UPDATE", ligne[cle], user_id, details)
        else:
            cur.execute(
                f"INSERT INTO {table} ({', '.join(colonnes)}, last_modified_by) "
                f"VALUES ({', '.join(['%s'] * len(colonnes))}, %s) RETURNING {cle}",
                parametres + (user_id,),
            )
            ecrire_audit(cur, table, "INSERT", cur.fetchone()[cle], user_id, details)


def enregistrer_reseau(ip: str, masque: str, user_id: int) -> bool:
    """Fonctionnalité 5 : stocke IP + masque et le dernier modificateur."""
    try:
        _run(lambda cur: _enregistrer_avec_modificateur(
            cur, "network_calculations", "calc_id",
            {"ip_address": ip, "subnet_mask": masque}, user_id,
        ))
        return True
    except Exception as e:
        print(f"[DB] enregistrer_reseau ERREUR {type(e).__name__}: {e}")
        return False


def enregistrer_meme_reseau(ip1: str, mask1: str, ip2: str, mask2: str, user_id: int) -> bool:
    """Fonctionnalité 6 : stocke les deux couples IP/masque et le dernier modificateur."""
    try:
        _run(lambda cur: _enregistrer_avec_modificateur(
            cur, "same_network_checks", "check_id",
            {"ip1": ip1, "mask1": mask1, "ip2": ip2, "mask2": mask2}, user_id,
        ))
        return True
    except Exception as e:
        print(f"[DB] enregistrer_meme_reseau ERREUR {type(e).__name__}: {e}")
        return False
