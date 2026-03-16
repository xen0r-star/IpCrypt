#Menu inscription/connexion 
def menuIC():
    start = 1
    while start == 1: 
        print("Que souhaitez-vous faire ?\n")
        print("1 - Connexion")
        print("2 - Inscription ")
        print("3 - Revenier menu principal")
        choix = int(input())
        match choix: #Permet d'éviter les If/else
            case 1:
                print("Inscription")
            case 2:
                print("Connexion")
            case 3:
                start = 0
                print("Revenier menu principal")
            case _: #Choix par défaut ou choix éronné
                print("Choix éronné, veuillez réssayer.")

#Inscription 
def inscription():
    print("Inscription")

#Connexion
def connexion():
    print("Connexion")

#Menu
start = 1 #Évite la fermeture de l'application après un seul choix 
while start == 1: 
    print("Que souhaitez-vous faire ?\n")
    print("1 - Connexion/Inscription d'un administrateur")
    print("2 - Generer un tableau des masques")
    print("3 - Gestion des adresses IP")
    print("4 - Quitter l'application")

    choix = int(input())
    match choix: #Permet d'éviter les If/else
        case 1:
            print("Inscription/Connexion")
        case 2:
            print("Génération tableau")
        case 3:
            print("Gestion des IP")
        case 4:
            start = 0
            print("Fermeture de l'appli")
        case _: #Choix par défaut ou choix éronné
            print("Choix éronné, veuillez réssayer.")

