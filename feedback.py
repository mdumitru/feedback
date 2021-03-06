#!/usr/bin/env python3
import sys
import os
import csv
import unicodedata


class Name():
    """Custom object for normalizing names and avoiding 'John Doe', 'john doe'
    and 'Jöhn Döe' being considered distinct.

    The names are converted to lowercase, no diacritics; manually fix them
    after.

    """
    def __init__(self, name):
        self.name = unicodedata.normalize("NFKD", name.lower()).encode("ASCII", "ignore")

    def __repr__(self):
        return repr(self.name)

    def __str__(self):
        return self.name.decode('utf-8')

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def get_eval(s):
    if s == "5 - Complet de Acord":
        return 5
    if s == "4 - ...":
        return 4
    if s == "3 - ...":
        return 3
    if s == "2 - ...":
        return 2

    return 1


def get_h(s):
    # Students can choose between the following options:
    # We will consider the middle value.
    if s == "80% .. 100%":
        return 90
    if s == "60% .. 80%":
        return 70
    if s == "40% .. 60%":
        return 50
    if s == "20% .. 40%":
        return 30

    return 10


def get_nota(s):
    if s == "sub 5":
        return 4
    return int(s)


def get_load(s):
    if s == "DA":
        return 2
    if s == "NU":
        return 0

    return 1


def get_uniq_elem_at_column(csv_data, c):
    uniq = set([])
    for line in csv_data:
        uniq.add(Name(line[c]))
    return list(uniq)


def average_at_column(csv_data, f, c):
    s = 0
    num = 0
    for line in csv_data:
        s += f(line[c])
        num += 1.0
    return round(s/num, 2)


def min_at_column(csv_data, f, c):
    minimum = f(csv_data[0][c])
    for line in csv_data:
        if f(line[c]) < minimum:
            minimum = f(line[c])
    return minimum


def max_at_column(csv_data, f, c):
    maximum = f(csv_data[0][c])
    for line in csv_data:
        if f(line[c]) > maximum:
            maximum = f(line[c])
    return maximum


def get_header(csv_data):
    csv_data[0][2] = "Categorie"
    csv_data[0][3] = "Count"
    return csv_data[0][2:-4]


def get_stats(text, csv_data, f):
    # titular, asistent
    row = [text, len(csv_data)]

    # evaluare generala
    row.append(f(csv_data, get_eval, 4))
    # nota asteptata
    row.append(f(csv_data, float, 5))
    # incarcarea generala
    row.append(f(csv_data, get_eval, 6))
    # dotare locatie
    row.append(f(csv_data, get_eval, 7))
    # participare
    row.append(f(csv_data, get_h, 8))
    # cadrul didactic stapaneste
    row.append(f(csv_data, get_eval, 9))
    # metoda de expunere
    row.append(f(csv_data, get_eval, 10))
    # cursul a stimulat
    row.append(f(csv_data, get_eval, 11))
    # comportament cadru didactic
    row.append(f(csv_data, get_eval, 12))
    # materialele didactice suficiente pentru curs
    row.append(f(csv_data, get_eval, 13))
    # cadrul didactic stapaneste
    row.append(f(csv_data, get_eval, 14))
    # cadrul didactic sustine activitatea individuala
    row.append(f(csv_data, get_eval, 15))
    # cadrul didactic a raspuns intrebarilor
    row.append(f(csv_data, get_eval, 16))
    # comportament adecvat
    row.append(f(csv_data, get_eval, 17))
    # materiale didactice suficiente pentru aplicatii
    row.append(f(csv_data, get_eval, 18))
    # nr. ore saptamana pt teme
    row.append(f(csv_data, float, 19))
    # nr. + dificultate teme
    row.append(f(csv_data, get_eval, 20))
    # temele au ajutat la intelegerea materiei
    row.append(f(csv_data, get_eval, 21))

    return row


def filter_stats(f, f_id, csv_data, writer):
    p = f(csv_data, f_id)
    total = 0
    for e in p:
        a = [row for row in csv_data if Name(row[f_id]) == e]
        row = get_stats(e, a, average_at_column)
        total += int(row[1])
        writer.writerow(row)

    return total


def gather_data(csv_file):
    csv_data = []
    with open(csv_file, 'r') as csv_fd:
        reader = csv.reader(csv_fd)
        for line in reader:
            if line[0].startswith("Obs.:") or line[0] == "":
                break
            else:
                csv_data.append(line)
    csv_result_file = csv_file.rsplit('.', 1)[0] + "-prelucrat.csv"
    csv_result_fd = open(csv_result_file, 'w')
    writer = csv.writer(csv_result_fd, quoting=csv.QUOTE_ALL)

    print("Generate results in " + sys.argv[1] + "/" + csv_result_file)

    writer.writerow(get_header(csv_data))

    writer.writerow([""])
    row = get_stats("Minim", csv_data[1:], min_at_column)
    writer.writerow(row)

    row = get_stats("Mediu", csv_data[1:], average_at_column)
    writer.writerow(row)

    row = get_stats("Maxim", csv_data[1:], max_at_column)
    writer.writerow(row)

    writer.writerow([""])
    writer.writerow(["Titulari Curs"])
    total_t = filter_stats(get_uniq_elem_at_column, 2, csv_data[1:], writer)
    writer.writerow(["Total:", total_t])

    writer.writerow([""])
    writer.writerow(["Asistenți"])
    total_a = filter_stats(get_uniq_elem_at_column, 3, csv_data[1:], writer)
    writer.writerow(["Total:", total_a])


if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    print("Usage: " + sys.argv[0] + " DIR_DATA")
    sys.exit(1)
os.chdir(sys.argv[1])

datasets = [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".csv")]

for csv_file in datasets:
    gather_data(csv_file)
