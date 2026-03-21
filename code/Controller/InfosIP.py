def verificationIP (ip):
    #Découpage en plusieurs segments
    segment = ip.split(".")
    if len(segment) != 4: #S'il n'y a pas 4 segments l'adresse est invalide
        print("On ne peut couper l'adresse en quatre segment")
        return False
    
    for s in segment:
        if len(s) > 3: #Si la longueur d'un des segments est supérieur à 3
            print ("Un des segment fait plus de 3 chiffres")
            return False
        if not s.isdigit(): #Si l'un des segments n'est pas composés que de chiffres
            print("Il y a des lettres ou caracteres speciaux dans l'adresse")
            return False
        if int(s) < 0 or int(s) > 255: #Si le chiffres d'un des segments n'est pas entre 0 et 255
            print("un des segment est inférieur à 0 où supérieur à 255")
            return False
        
    if int(segment[3]) == 255:
        print("L'adresse insérée est une IP broadcast")
        return False
    elif int(segment[3]) == 0:
        print("L'adresse insérée est une adresse réseau")
        return False
    
    return True

def definirclasse(premOctet):
    octet=int(premOctet)
    if octet < 127 and octet > 1:
        print("Classe A")
        print("255.0.0.0")
        classe = "A"
    elif octet < 192 and octet > 127:
        print("Classe B")
        print("255.255.0.0")
        classe = "B"
    elif octet < 224 and octet > 191:
        print("Classe C")
        print("255.255.255.0")
        classe = "C"
    elif octet < 240 and octet > 223:
        print("Classe D")
        print("Pas de masque")
        classe = "D"
    else:
        print("Classe E")
        print("Pas de masque")
        classe = "E"


ip = input("Entrez votre adresse IP : \n")
verificationIP(ip)

segment = ip.split(".")
definirclasse(segment[0])




print(ip)