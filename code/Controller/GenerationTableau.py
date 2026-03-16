import pandas as pd

def exporterTableau(tableauSR):
    #Transformation du tableau créer en data
    df = pd.DataFrame(tableauSR, columns=["CIDR","Masque en Binaire","Masque en décimal"])#Ajoute un titre en plus pour les colonnes
    with pd.ExcelWriter('TableauMasques.xlsx', engine="xlsxwriter") as fichier:
        df.to_excel(fichier, sheet_name="Matrice des sous réseaux", index=False)#Exporter en fichier excel

    print("Le fichier a été généré avec succès !")

def binaireDecimal(masqueBinaire):
    # On découpe la chaîne de 32 bits en 4 blocs de 8
    octets = [masqueBinaire[i:i+8] for i in range(0, 32, 8)]
    # On convertit chaque bloc en décimal et on joint par des points
    return ".".join([str(int(o, 2)) for o in octets])

matSR = []

for index in range(8,31):
    cidr = "/" + str(index) #code cidr
    masqueBinaire = "1"*index + "0"*(32-index) #création du masque en binaire
    masqueDecimal = binaireDecimal(masqueBinaire)
    for point in range(24,0,-8):           #commencer par la fin pour ne pas modifier les indices de la chaînes
        masqueBinaire = masqueBinaire[:point] + "." + masqueBinaire[point:]
    lignes = [cidr,masqueBinaire,masqueDecimal]
    matSR.append(lignes)

for l in matSR:
    print(f"{l[0]} | {l[1]} | {l[2]}")

exporterTableau(matSR)