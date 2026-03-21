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

def definirClasse(premOctet):
    octet=int(premOctet)
    match octet:
        case _ if 1 <= octet <= 126:
            print("Classe A")
            return "A"
        case _ if 128 <= octet <= 191:
            print("Classe B")
            return "B"
        case _ if 192 <= octet <= 223:
            print("Classe C")
            return "C"
        case _ if 224 <= octet <= 240:
            print("Classe D")
            return "D"
        case _:
            print("Classe E")
            return "E"

def definirMasque(classe):
    match classe:
        case "A":
            print("255.0.0.0")
        case "B":
            print("255.255.0.0")
        case "C":
            print("255.255.255.0")
        case _:
            print("Pas de masque")

def adresseReseau(segment,classe):
    match classe:
        case "A":
            print(segment[0],".","0",".","0",".","0")
        case "B":
            print(segment[0],".",segment[1],".","0",".","0")
        case "C":
            print(segment[0],".",segment[1],".",segment[2],".","0")

def adresseBroadcast(segment,classe):
    match classe:
        case "A":
            print(segment[0],".","255",".","255",".","255")
        case "B":
            print(segment[0],".",segment[1],".","255",".","255")
        case "C":
            print(segment[0],".",segment[1],".",segment[2],".","255")

def premierHote(segment,classe):
    match classe:
        case "A":
            print(segment[0],".","0",".","0",".","1")
        case "B":
            print(segment[0],".",segment[1],".","0",".","1")
        case "C":
            print(segment[0],".",segment[1],".",segment[2],".","1")

def dernierHote(segment,classe):
    match classe:
        case "A":
            print(segment[0],".","255",".","255",".","254")
        case "B":
            print(segment[0],".",segment[1],".","255",".","254")
        case "C":
            print(segment[0],".",segment[1],".",segment[2],".","254")

def nombresHotes(classe):
    match classe:
        case "A":
            print("16 777 214")
        case "B":
            print("65 534")
        case "C":
            print("254")

def definirCIDR(classe):
    match classe:
        case "A":
            print("0.0.0.255")
        case "B":
            print("0.0.255.255")
        case "C":
            print("0.255.255.255")
       
def definirMasqueWildcart(classe):
    match classe:
        case "A":
            print("0.0.0.255")
        case "B":
            print("0.0.255.255")
        case "C":
            print("0.255.255.255")


ip = input("Entrez votre adresse IP : \n")
verificationIP(ip)

segment = ip.split(".")
classe = definirClasse(segment[0])
definirMasque(classe)
adresseReseau(segment,classe)
adresseBroadcast(segment,classe)
premierHote(segment,classe)
dernierHote(segment,classe)
nombresHotes(classe)
definirMasqueWildcart(classe)
