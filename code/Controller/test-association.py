#on devra passer 2 fois par cette fonction afin de calculer pour ip 1 et 2
def calculer_adresse_reseau(ip1, masque1, ip2, masque2):

    '''je dois transformer chaque octet de l'ip en binaire puis transformer chaque octet du masque en binaire et faire un ET LOGIQUE pour avoir l'adresse réseau mais en binaire. Il faut faire ca X2 et ensuite on compare les deux adresses réseau et on déduit : 
        A et B dans meme reseau
        A voit B mais B ne voit pas A
        A ne voit pas B et B voit A
        A et B ne se voient pas'''
    
    
    print()
    print("calculer adresse reseau")
    octet_binary = []

    #ca c'est le code pour l'ip 1 - il faut faire le meme pour l'ip 2 ainsi que les masques
    for i in range(1,5):
        print()
        print("valeur de i " ,i)
        octet_Number = i*4
        print("valeur octet_Number : ",octet_Number)
        octet_binary = ip1[i-1]
        print("valeur octetBinaire en decimal " ,octet_binary)
        octet_binary = format(int(octet_binary), 'b')  # or bin(num)[2:]
        while(len(octet_binary) < 8):
            octet_binary = "0" + octet_binary
        print("valeur octetBinaire en binaire " ,octet_binary)
        
        #le transfert en binaire est fonctionel il reste a faire le ET logique entre l'ip et le masque 

def input_des_infos():
    ip = []
    masque=[]
    #premiere ip et masque
    print("Premiere IP")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) > 3 and len(octet) < 1:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(len(octet) < 3):
            octet = "0" + octet
        ip.append(octet)
        
    print("Premier MASQUE")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) > 3 and len(octet) < 1:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(len(octet) < 3):
            octet = "0" + octet
        masque.append(octet)

    #seconde ip et masque
    print("Seconde IP")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) > 3 and len(octet) < 1:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(len(octet) < 3):
            octet = "0" + octet
        ip.append(octet)
    print("Second MASQUE")
    for i in range(1,5):
        octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(octet.isdigit() == False or int(octet) < 0 or int(octet) > 255) or len(octet) > 3 and len(octet) < 1:
            print("Veuillez entrer une valeur valide (0-255).")
            octet = input(f"Entrez les valeurs de l'octet {i} : ")
        while(len(octet) < 3):
            octet = "0" + octet
        masque.append(octet)

    print(f"Première IP : {'.'.join(ip[0:4])}")
    print(f"Premier Masque : {'.'.join(masque[0:4])}")
    print(f"Seconde IP : {'.'.join(ip[4:8])}")
    print(f"Second Masque : {'.'.join(masque[4:8])}")
    
    calculer_adresse_reseau(ip[0:4], masque[0:4], ip[4:8], masque[4:8])

print("Association d'IP")
input_des_infos()