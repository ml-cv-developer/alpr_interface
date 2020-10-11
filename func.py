
import csv
import os


def append_csv(filename, data):
    """
        save the "data" to filename as csv format.
    """
    file_out = open(filename, 'a')
    writer = csv.writer(file_out)
    writer.writerows(data)
    file_out.close()


def save_csv(filename, data):
    """
        save the "data" to filename as csv format.
    """
    file_out = open(filename, 'w')
    writer = csv.writer(file_out)
    writer.writerows(data)
    file_out.close()


def load_csv(filename):
    """
        load the csv data and return it.
    """
    if os.path.isfile(filename):
        file_csv = open(filename, 'r')
        reader = csv.reader(file_csv)
        data_csv = []
        for row_data in reader:
            data_csv.append(row_data)

        file_csv.close()
        return data_csv
    else:
        return []


def save_text(filename, data):
    with open(filename, 'w') as f:
        f.write(data)


def append_text(filename, data):
    with open(filename, 'a') as f:
        f.write(data)


def load_text(filename):
    with open(filename, 'r') as f:
        return f.read()
