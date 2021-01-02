import http.client
from bs4 import BeautifulSoup
import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime

# aici modific in caz ca vreau alt interval de ani
an_inceput = 1993
an_final = 2020

# declarari initializari
lista_ani = [str(x) for x in range(an_inceput,an_final+1)]
lista_luni = ["06", "11"]

caractere_bune = set("0123456789.")

dictionar_medii = {}

connection = http.client.HTTPSConnection("www.top500.org")

# pun in fisierul lista_url.txt toate url din intervalul dat
# daca exista deja, nu il mai pun
for an in lista_ani:
    for luna in lista_luni:
        # cam vrajeala cum generez url astea
        url = "https://" + connection.host + "/lists/top500/" + an + "/" + luna + "/"

        # caut sa vad daca exista ulr asta deja in fisier:
        ok = 0
        try:
            with open("lista_url.txt", "r") as f:
                s = f.read()
                if url in s:
                    ok = 1 # e deja acolo
        except FileNotFoundError:
            # daca nu exista fsierul, il creez oricum
            ok = 0

        # pun in continuarea fisierului daca nu e deja acolo
        if ok == 0:
            with open("lista_url.txt", "a") as f:
                f.write(url)
                f.write("\n")
connection.close()

# sortez liniile din fisierul lista_url
lista_linii = []
with open("lista_url.txt", "r") as f:
    for linie in f.readlines():
        lista_linii.append(linie)
lista_linii.sort()
with open("lista_url.txt", "w") as f:
    for url in lista_linii:
        f.write(url)


# pun url urile din fisier intr-o lista ca sa le pot parcurge mai usor:
with open('lista_url.txt', 'r') as f:
    urluri = f.readlines()

# parcurg url urile si fac chestii cu ele:
for url in urluri:
    with open("lista_key.txt", "r") as f:
        s = f.read()

        # verific daca pentru anul si luna de pe url asta exista
        # deja calculata media celor mai puternice 3 masini de calcul
        # daca nu exista, o calculez
        if url[-9:-2] not in s:

            # pun programul sa astepte o secunda ca sa nu suprasolicit site ul
            timp_start = time.time()
            while True:
                timp_acum = time.time()
                durata = timp_acum - timp_start
                if durata > 1:
                    break

            # pun in stringul cod_html tot codul folosit pentru pagina de la url asta
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            cod_html = soup.prettify()

            # putin cam foarte brut ce fac aici, dar nu necesita mare efort intelectual si vreau sa termin repede
            # caut in cod_html aparitiile lui string_cautat = """<td style="text-align: right;">"""
            # fiecare masina de calcul are cate 3 string_cautat de astea
            # si Rmax care ma intereseaza pe mine e dupa a 2-a aparitie a lui string_cautat in cadrul fiecarei masini
            # deci inseamna ca ma intereseaza Rmax de dupa a 2-a, a 5-a si a 8-a pozitie pe care a fost gasit string_cautat

            string_cautat = """<td style="text-align: right;">"""
            lg = len(string_cautat)
            inceput = 0
            final = len(cod_html) - 1
            pozitie_minune = cod_html.find(string_cautat, inceput, final)
            index_gasit = 1
            medie_pe_luna = 0
            while pozitie_minune != -1:
                # daca ma intereseaza numarul de dupa aparitia asta il iau si il prelucrez
                if index_gasit == 2 or index_gasit == 5 or index_gasit == 8:
                    numar = cod_html[pozitie_minune + lg: pozitie_minune + lg + 30]
                    numar = ''.join(c for c in numar if c in caractere_bune)
                    numar_de_medie = int(numar[:-2]) + (int(numar[-1])) / 10

                    # daca anul e inainte de 2005 convertesc numar_de_medie din gflops in tflops
                    # adica impart la 1000
                    if int(url[-9:-5]) < 2005:
                        numar_de_medie /= 1000

                    medie_pe_luna += numar_de_medie

                # nu parcurg mai mult decat am nevoie
                if index_gasit == 8:
                    break

                # trec la urmatoarea aparitie
                inceput = pozitie_minune + len(string_cautat)
                pozitie_minune = cod_html.find(string_cautat, inceput, final)
                index_gasit += 1

            # calcuez media de pe luna asta si o pun in dictionar
            # dic{"an/luna"} = media pe luna asta
            medie_pe_luna /= 3
            key = url[-9:-2]
            dictionar_medii[key] = medie_pe_luna

# caut sa vad daca exista key deja in fisier:
for key in dictionar_medii.keys():
    ok = 0
    try:
        with open("lista_key.txt", "r") as f:
            s = f.read()
            if key in s:
                ok = 1 # e deja acolo
    except FileNotFoundError:
        # daca nu exista fisierul, il creez oricum
        ok = 0

    # pun in continuarea fisierului daca nu e deja acolo
    if ok == 0:
        with open("lista_key.txt", "a") as f:
            f.write(key)
            f.write(" ")
            f.write(str(dictionar_medii[key]))
            f.write("\n")

# sortez liniile din fisierul lista_key
lista_linii = []
with open("lista_key.txt", "r") as f:
    for linie in f.readlines():
        lista_linii.append(linie)
lista_linii.sort()
with open("lista_key.txt", "w") as f:
    for key in lista_linii:
        f.write(key)


# pentru inceput fac un fel de caz special pentru primul an
# pun in medie_pe_an_trecut media din primul an (din intervalul care ma intereseaza)
medie_pe_an_trecut = 0
x_axa = []
y_axa = []
an_cursed = 0
with open("lista_key.txt", "r") as f:
    # iau prima linie, adica aia care are media pe iunie a primului an din fisier
    linie = f.readline()
    # caut primul an din intervalul care ma intereseaza
    while int(linie[:4]) != an_inceput:
        linie = next(f)
    an_cursed = int(linie[:4])
    if int(linie[:4]) in range(an_inceput, an_final + 1): # sigur e in interval
        # convertesc linia intr-un numar
        numar = 0
        zecimale = 0
        nr_zecimale = 1
        dupa = False
        for c in linie[8:-1]:
            if c == ".":
                dupa = True
            elif dupa == False:
                numar = numar * 10 + int(c)
            elif dupa == True:
                zecimale = zecimale * 10 + int(c)
                nr_zecimale *= 10
        numar = numar + (zecimale / nr_zecimale)
        medie_pe_an_trecut = numar

        y_axa.append(numar)
        x_axa.append(datetime.strptime(linie[2:7] + "/01", "%y/%m/%d"))


    # trec la urmatoarea linie, adica aia care are media pe noiembrie
    linie = next(f)
    if int(linie[:4]) in range(an_inceput, an_final + 1): # sigur e in interval
        # convertesc linia intr-un numar
        numar = 0
        zecimale = 0
        nr_zecimale = 1
        dupa = False
        for c in linie[8:-1]:
            if c == ".":
                dupa = True
            elif dupa == False:
                numar = numar * 10 + int(c)
            elif dupa == True:
                zecimale = zecimale * 10 + int(c)
                nr_zecimale *= 10
        numar = numar + (zecimale / nr_zecimale)
        medie_pe_an_trecut += numar

        y_axa.append(numar)
        x_axa.append(datetime.strptime(linie[2:7] + "/01", "%y/%m/%d"))

medie_pe_an_trecut /= 2


# parcurg fisierul lista_key si fac progresul mediu si plot ul
medie_pe_an = 0
PROGRES_MEDIU = 0
nr_p = 0
with open("lista_key.txt", "r") as f:
    for linie in f.readlines()[2:]:
        # daca e in intervalul care ma intereseaza pe mine calculez progresul si fac plotul
        if int(linie[:4]) in range(an_inceput,an_final+1) and int(linie[:4]) != an_cursed:
            # convertesc linia intr-un numar
            numar = 0
            zecimale = 0
            nr_zecimale = 1
            dupa = False
            for c in linie[8:-1]:
                if c == ".":
                    dupa = True
                elif dupa == False:
                    numar = numar * 10 + int(c)
                elif dupa == True:
                    zecimale = zecimale * 10 + int(c)
                    nr_zecimale *= 10
            numar = numar + (zecimale / nr_zecimale)

            y_axa.append(numar)
            x_axa.append(datetime.strptime(linie[2:7] + "/15", "%y/%m/%d"))

            # calculez raspunsul in PROGRES_MEDIU
            # daca sunt in iunie
            if linie[5:7] == "06":
                # incep sa calculez media pe anul asta
                medie_pe_an = numar

            # daca sunt in noiembrie
            elif linie[5:7] == "11":
                # adun la media pe anul asta
                medie_pe_an += numar
                medie_pe_an /= 2

                # calculez progresul facut de anul trecut pana anul asta
                progres_local = medie_pe_an / medie_pe_an_trecut
                medie_pe_an_trecut = medie_pe_an

                # adaug progresul local la suma ca sa calculez progresul mediu
                PROGRES_MEDIU += progres_local
                nr_p += 1


PROGRES_MEDIU /= nr_p
print("PROGRES MEDIU REALIZAT PE AN:", PROGRES_MEDIU)

plt.plot(x_axa,y_axa)
plt.ylabel("Performanta maxima")
plt.xlabel("Anul")
plt.suptitle("Progres mediu realizat pe an: " + str(PROGRES_MEDIU))

plt.show()
