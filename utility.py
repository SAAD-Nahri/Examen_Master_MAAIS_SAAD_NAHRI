import datetime


def input_non_vide(text):
    while True:
        x = input(text)
        if x:
            return x
        else:
            print('ce champ ne peut etre null, retapez')


def int_inpute_non_vide(text):
    while True:
        try:
            x = int(input_non_vide(text))
            return x
        except:
            print("tu doit un entier")


def int_input(c):
    try:
        int(c)
        return True
    except:
        return False


def is_date(a):
    try:
        datetime.datetime.strptime(a, "%Y-%m-%d").date()
        return True
    except ValueError:
        return False


def saisir_date(text):
    while True:
        a = input(text)
        if is_date(a):
            return a
        else:
            print("Incorrect date format,resaisir in the format Years-months-days")


def str_to_date(date):
    return datetime.datetime.strptime(date,"%Y-%m-%d").date()


def afficher_list(L):
    for i in range(len(L)):
        print(i + 1, " : ", L[i], "\n")


def int_input1(text):
    while True:
        try:
            x = int(input(text))
            return x
        except:
            print("tu doit entre un entier")



def input_in_range(L):
    while True:
        i = int_inpute_non_vide("Selon votre choix taper un nombre entre 1 et " + str(len(L)) + " --> ")
        if (i > 0) and (i <= len(L)):
            return i
        else:
            print('out of range, retapez')

def input_in_list(L):
    if len(L) == 1:
        print(f"only one element exist {L[0]} selected by default")
        return L[0]
    elif len(L) > 1:
        afficher_list(L)
        x = input_in_range(L)
        return L[x-1]
    if len(L) == 0:
        print("nothing")


def input_multiple_in_list(L):
    a = {}
    while True:
        if len(L) == 1:
            a[L[0]] = input(f"taper la valeur de {L[0]}")
            return a
        elif len(L) > 1:
            afficher_list(L)
            atr = input_in_range(L)
            a[L[atr-1]] = input(f"taper la valeur de {L[atr-1]}")
            print("do you want to add another filter:")
            if input_in_list(["yes", "no"]) == "yes":
                del L[atr-1]
            else:
                return a
