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


ip = input("Entrez votre adresse IP : \n")
verificationIP(ip)
print(ip)