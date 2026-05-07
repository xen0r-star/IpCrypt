"""
Tests unitaires pour calcule_adresse_reseau (network_comparator.py).

Les octets sont passés en chaînes zero-paddées sur 3 chiffres,
comme le fait lire_octets() dans l'interface : "192", "168", "001", "010".

Lancer avec : python -m pytest code/Controller/test_network_comparator.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from screens.network_comparator import calcule_adresse_reseau


def _oct(ip_str: str) -> list[str]:
    """Convertit '192.168.1.10' en ['192', '168', '001', '010']."""
    return [str(int(o)).zfill(3) for o in ip_str.split(".")]


# ─── Cas 1 : même réseau, mêmes masques ──────────────────────────────────────
def test_meme_reseau():
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.10"), _oct("255.255.255.0"),
        _oct("192.168.1.20"), _oct("255.255.255.0"),
    )
    assert meme is True
    assert verdict == "A et B sont dans le même réseau."
    assert r1 == [192, 168, 1, 0]
    assert r2 == [192, 168, 1, 0]


# ─── Cas 2 : réseaux différents, mêmes masques ───────────────────────────────
def test_reseaux_differents():
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.10"), _oct("255.255.255.0"),
        _oct("192.168.2.10"), _oct("255.255.255.0"),
    )
    assert meme is False
    assert verdict == "A et B ne se voient pas."
    assert r1 == [192, 168, 1, 0]
    assert r2 == [192, 168, 2, 0]


# ─── Cas 3 : A voit B mais B ne voit pas A (masques asymétriques) ────────────
def test_a_voit_b_mais_pas_inverse():
    # A : 10.0.0.1 / 255.0.0.0  → réseau A = 10.0.0.0
    # B : 10.1.0.1 / 255.255.0.0 → réseau B = 10.1.0.0
    # ip_B & masque_A = 10.0.0.0 == réseau A → A voit B ✓
    # ip_A & masque_B = 10.0.0.0 ≠ réseau B (10.1.0.0) → B ne voit pas A ✓
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("10.0.0.1"), _oct("255.0.0.0"),
        _oct("10.1.0.1"), _oct("255.255.0.0"),
    )
    assert meme is False
    assert verdict == "A voit B mais B ne voit pas A."


# ─── Cas 4 : B voit A mais A ne voit pas B (inverse du cas 3) ────────────────
def test_b_voit_a_mais_pas_inverse():
    # A : 10.1.0.1 / 255.255.0.0 → réseau A = 10.1.0.0
    # B : 10.0.0.1 / 255.0.0.0  → réseau B = 10.0.0.0
    # ip_B & masque_A = 10.0.0.0 ≠ réseau A (10.1.0.0) → A ne voit pas B ✓
    # ip_A & masque_B = 10.0.0.0 == réseau B ✓
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("10.1.0.1"), _oct("255.255.0.0"),
        _oct("10.0.0.1"), _oct("255.0.0.0"),
    )
    assert meme is False
    assert verdict == "B voit A mais A ne voit pas B."


# ─── Cas 5 : IP identiques ────────────────────────────────────────────────────
def test_ip_identiques():
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.1"), _oct("255.255.255.0"),
        _oct("192.168.1.1"), _oct("255.255.255.0"),
    )
    assert meme is True
    assert verdict == "A et B sont dans le même réseau."


# ─── Cas 6 : masque /32 — uniquement si IP strictement identiques ─────────────
def test_masque_32_ip_differentes():
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.1"), _oct("255.255.255.255"),
        _oct("192.168.1.2"), _oct("255.255.255.255"),
    )
    assert meme is False
    assert r1 == [192, 168, 1, 1]
    assert r2 == [192, 168, 1, 2]


def test_masque_32_ip_identiques():
    _, _, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.1"), _oct("255.255.255.255"),
        _oct("192.168.1.1"), _oct("255.255.255.255"),
    )
    assert meme is True


# ─── Cas 7 : masque /0 — tout le monde se voit ───────────────────────────────
def test_masque_0():
    _, _, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.1"), _oct("0.0.0.0"),
        _oct("10.20.30.40"), _oct("0.0.0.0"),
    )
    assert meme is True
    assert verdict == "A et B sont dans le même réseau."


# ─── Cas 8 : classe A vs classe C dans le même /8 ────────────────────────────
def test_classe_a_masque_8():
    _, _, verdict, meme = calcule_adresse_reseau(
        _oct("10.0.0.1"),   _oct("255.0.0.0"),
        _oct("10.255.255.1"), _oct("255.0.0.0"),
    )
    assert meme is True


# ─── Cas 9 : adresses limites (0.0.0.0 et 255.255.255.255) ──────────────────
def test_adresses_limites():
    r1, r2, verdict, meme = calcule_adresse_reseau(
        _oct("0.0.0.0"),         _oct("255.255.255.0"),
        _oct("255.255.255.255"), _oct("255.255.255.0"),
    )
    assert meme is False
    assert r1 == [0, 0, 0, 0]
    assert r2 == [255, 255, 255, 0]


# ─── Cas 10 : même IP, masques de tailles différentes ────────────────────────
def test_meme_ip_masques_differents():
    # Les deux hôtes sont la même machine mais avec des masques différents.
    # A (/24) voit B dans son réseau 192.168.1.0/24 ✓
    # B (/16) voit A dans son réseau 192.168.0.0/16 ✓
    # → même réseau (les deux se voient mutuellement)
    _, _, verdict, meme = calcule_adresse_reseau(
        _oct("192.168.1.1"), _oct("255.255.255.0"),
        _oct("192.168.1.1"), _oct("255.255.0.0"),
    )
    assert meme is True
