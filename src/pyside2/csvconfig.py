import csv

class CsvConfig:
    """
            Class: Reads and writes to the csv file containing all the saved wire report excel sheet configurations
            Fields:
                self.file is a file pointer the the text file containing the wire report configuartions
            Methods:
                search(name): search the csv file for the row that begins with the given name
                remove(name): remove the row that begins with name from the csv file. returns 0 on failure and 1 on success
        """

    def __init__(self):
        try:
            file = open("test.txt", "r+")
        except:
            print("Cannot find csv wire configuration file")
        else:
            while(True):
                line = file.readline()
                if not line:
                    break
                if line[0] != '#':
                    if line == "name,from_component,from_pin,to_component,to_pin,wire_csa,description\n":
                        break
            file.close()
        l = ["first","test_1","test_2","test_3","test_4","test_5","cum cugget"]
        self.add(l)

    def search(self, name):
        """
            name: the name field of the given csv row created by the user for indentification later
            This method searches the csv file for the row that begins with the given name
            returns a list representing the csv row where each entry is a string object
        """
        file = open("test.txt", "r")
        reader = csv.reader(file)
        target_row = []
        for row in reader:
            if not row:
                continue
            # ignore lines starting with '#'
            if row[0][0] == '#':
                continue
            if row[0] == name:
                target_row = row
                break
        file.close()
        return target_row

    def delete(self, name):
        """
            name: the name field of the given csv row created by the user for indentification later
            This method searches the csv file for the row that begins with the given name and removes it
            returns 0 on failure
        """
        try:
            # first record orginal contents of text file but exclude the target row
            file = open("test.txt", "r+")
            reader = csv.reader(file)
            new_csv = []
            for row in reader:
                if not row:
                    continue
                if row[0] != name:
                    new_csv.append(row)
            file.close()
            # write new contents to the same file
            file = open("test.txt", "w+", newline='')
            writer = csv.writer(file)
            writer.writerows(new_csv)
            file.close()
        except:
            print("error deleting entry")
            return 0
        return 1

    def add(self, new_row):
        """
            new_row: a list representing one of the csv rows that will be inserted into the csv file
            This method appends the new_row into the wire report csv configuration file
            If the new row shares a name with an existing row then the exisiting row will first be deleted
            Returns 0 on failure and 1 on success

        """
        try:
            # overwting an exisiting row
            if self.search(new_row[0]):
                # Record contents of file except the row to be overwritten
                file = open("test.txt", "r+")
                reader = csv.reader(file)
                new_csv = []
                for row in reader:
                    if not row:
                        continue
                    if row[0] != new_row[0]:
                        new_csv.append(row)
                file.close()
                # write new contents to the same file
                file = open("test.txt", "w+", newline='')
                writer = csv.writer(file)
                writer.writerows(new_csv)
                writer.writerow(new_row)
                file.close()
            # Appending new row
            else:
                file = open("test.txt", "a", newline="")
                writer = csv.writer(file)
                writer.writerow(new_row)
                file.close()
            return 1
        except:
            print("failure adding new row")
            return 0
