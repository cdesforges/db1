def read_file(filename):
    f_in = open(filename, "r")
    for line in f_in:
        print(line)