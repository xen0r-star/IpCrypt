BITS_HOTE_MIN = 2

LIMITE_LIGNES = 500

CIDR_PAR_CLASSE = {"A": 8, "B": 16, "C": 24}

def classe_depuis_octet(premier_octet: int) -> str:
    """Retourne la classe (A–E) d'une adresse IP à partir de son premier octet."""
    if premier_octet <= 127:
        return "A"
    if premier_octet <= 191:
        return "B"
    if premier_octet <= 223:
        return "C"
    if premier_octet <= 239:
        return "D"
    return "E"


def octets_vers_entier(octets) -> int:
    "Convertit 4 octets en entier 32 bits"
    valeur = 0
    for octet in octets:
        valeur= (valeur << 8) |int(octet)
    return valeur

def entier_vers_texte(valeur: int) -> str:
    return ".".join(str((valeur >> decalage) & 255) for decalage in (24, 16, 8, 0))

def masque_depuis_cidr(cidr:int) -> int:
    return (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF

def bits_a_emprunter(nb_sous_reseaux: int ) -> int:

    bits = 0
    while(1 << bits) < nb_sous_reseaux:
        bits += 1
    return bits

def nb_sous_reseaux_max(cidr_base: int) -> int:
    "Nbre max de SR pour un préfixe de base, en gardant au moins BITS_HOTE_MIN bits d'hôte"
    return 1 << (32 - BITS_HOTE_MIN - cidr_base)

def calculer_decoupe(octets_ip, nb_demande: int) -> dict:
    """
    Découpe le réseau classful de l'IP donnée en au moins nb_demande sous-réseaux de même taille.

    Lève ValueError si la découpe est impossible.

    On emprunte n bits tels que 2**n >= nb_demande : on obtient donc 2**n sous-réseaux (>= nb_demande).
    """
    premier_octet = int(octets_ip[0])
    classe = classe_depuis_octet(premier_octet)

    if classe in ("D", "E"):
        raise ValueError(f"Classe {classe} : pas de découpe possible (seules les classes A, B et C se découpent).")
    if premier_octet in (0, 127):
        raise ValueError("Réseau réservé (0.0.0.0/8 ou 127.0.0.0/8) : pas de découpe possible.")
    if nb_demande < 2:
        raise ValueError("Il faut demander au moins 2 sous-réseaux.")

    cidr_base = CIDR_PAR_CLASSE[classe]
    maximum = nb_sous_reseaux_max(cidr_base)
    if nb_demande > maximum: 
        raise ValueError(
            f"Classe {classe} : {maximum} sous-réseaux au maximum "
            f"(il faut garder 2 hôtes utilisables par sous-réseau)."
        )

    bits = bits_a_emprunter(nb_demande)
    nouveau_cidr = cidr_base + bits
    base = octets_vers_entier(octets_ip) & masque_depuis_cidr(cidr_base)
    taille_bloc = 1 << (32 - nouveau_cidr)

    return {
        "classe": classe,
        "adresse_reseau": entier_vers_texte(base),
        "cidr_base": cidr_base,
        "masque_base": entier_vers_texte(masque_depuis_cidr(cidr_base)),
        "bits_empruntes": bits,
        "nb_demande": nb_demande,
        "nb_obtenus": 1 << bits,
        "nouveau_cidr": nouveau_cidr,
        "nouveau_masque": entier_vers_texte(masque_depuis_cidr(nouveau_cidr)),
        "taille_bloc": taille_bloc,
        "hotes_par_sous_reseau": taille_bloc - 2,
        "_base": base,
    }

def sous_reseau(decoupe: dict, numero: int) -> dict:
    "Détail du sous-réseaux n° 'numero' (0 = premier) d'une découpe calculée par calculer_decoupe."
    debut = decoupe["_base"] + numero * decoupe["taille_bloc"]
    broadcast = debut + decoupe["taille_bloc"] - 1
    return {
        "numero": numero + 1,
        "reseau": entier_vers_texte(debut),
        "premier_hote": entier_vers_texte(debut+1),
        "dernier_hote": entier_vers_texte(broadcast - 1),
        "broadcast": entier_vers_texte(broadcast),
    }

def lister_sous_reseaux(decoupe: dict, limite: int = LIMITE_LIGNES) -> list:
    "Détail des 'limite' premiers sous_réseaux (une classe A découpé à fond en compte plusieurs millions)."
    return [sous_reseau(decoupe, i) for i in range(min(decoupe["nb_obtenus"], limite))]