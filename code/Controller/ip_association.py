#on devra passer 2 fois par cette fonction afin de calculer pour ip 1 et 2
def calculer_adresse_reseau(ip1, masque1, ip2, masque2):
    # Implémenter la logique pour calculer l'adresse réseau
    pass

#comparaison des IP
def comparaison_ip(ip1, masque1, ip2, masque2):

    #verifie si les deux IP et Masques sont identiques
    if(ip1 == ip2):
        if(masque1 == masque2):
            #return (True, "Les deux adresses IP et les masques sont identiques, elles sont dans le même réseau")
            reseau = calculer_adresse_reseau(ip1, masque1, ip2, masque2)
            
    return (False, "Les adresses IP ou les masques sont différents, elles ne sont pas dans le même réseau")

def input_des_infos():

    ip = []
    masque=[]
    #premiere ip et masque
    print("Premiere IP")
    for i in range(1,5):

        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) != 3:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        ip.append(octet)
    print("Premier MASQUE")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) != 3:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        masque.append(octet)

    #seconde ip et masque
    print("Seconde IP")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) != 3:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        ip.append(octet)
    print("Second MASQUE")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) != 3:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        masque.append(octet)

    print(f"Première IP : {'.'.join(ip[0:4])}")
    print(f"Premier Masque : {'.'.join(masque[0:4])}")
    print(f"Seconde IP : {'.'.join(ip[4:8])}")
    print(f"Second Masque : {'.'.join(masque[4:8])}")

    result = comparaison_ip(ip[0:4], masque[0:4], ip[4:8], masque[4:8])
    print(result)

print("Association d'IP")
input_des_infos()