def calcule_adresse_reseau(ip_binary_table, masque_binary_table):
    """Calcule l'adresse réseau par ET logique bit à bit entre IP et masque."""
    adresse_reseau = []
    
    # AND bit à bit : IP & Masque = Adresse réseau
    for nombre_octet in range(8):
        calcul = int(ip_binary_table[nombre_octet]) & int(masque_binary_table[nombre_octet])
        adresse_reseau.append(calcul)
    
    # Séparation des deux adresses réseau calculées
    reseau1 = adresse_reseau[0:4]
    reseau2 = adresse_reseau[4:8]
    
    print(f"Adresse réseau 1 : {'.'.join(map(str, reseau1))}")
    print(f"Adresse réseau 2 : {'.'.join(map(str, reseau2))}")
    
    # Deux hôtes sont dans le même réseau si IP & Masque est identique
    if reseau1 == reseau2:
        print("A et B sont dans le même réseau")
    else:
        print("A et B ne sont pas dans le même réseau")
    
    return reseau1, reseau2


def transformation_decimal_binaire(ip1, masque1, ip2, masque2):
    """Prépare les tables d'octets pour le calcul des adresses réseau."""
    print("---------------------------------")
    print("     Calculer adresse reseau")
    print("---------------------------------")
    
    ip_binary_table = []
    masque_binary_table = []

    # Concaténation des octets : [ip1_oct1..4, ip2_oct1..4]
    for ip in [ip1, ip2]:
        ip_binary_table.extend(ip)

    # Concaténation des masques : [masque1_oct1..4, masque2_oct1..4]
    for masque in [masque1, masque2]:
        masque_binary_table.extend(masque)
            
    calcule_adresse_reseau(ip_binary_table, masque_binary_table)


def saisir_octets(label):
    """Saisie et validation des 4 octets d'une adresse IPv4 (0-255 par octet)."""
    print(label)
    octets = []
    for i in range(1, 5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        # Un octet IPv4 est compris entre 0 et 255
        while not octet.isdigit() or not (0 <= int(octet) <= 255):
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        octets.append(octet.zfill(3))
    return octets


def input_des_infos():
    ips, masques = [], []

    for label_ip, label_masque in [("Premiere IP", "Premier MASQUE"), ("Seconde IP", "Second MASQUE")]:
        print()
        ips.append(saisir_octets(label_ip))
        masques.append(saisir_octets(label_masque))
        
    print()
    for i in range(2):
        print(f"IP {i+1}     : {'.'.join(ips[i])}")
        print(f"Masque {i+1} : {'.'.join(masques[i])}")
        print()
    
    transformation_decimal_binaire(ips[0], masques[0], ips[1], masques[1])


print("Association d'IP")
input_des_infos()