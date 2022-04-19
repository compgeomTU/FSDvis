

class Curve:

    x: list
    y: list

    __filename: str

    def __init__(self, filename):

        self.__filename = filename
        self.x, self.y = list(), list()

        for line in open(filename, "r"):
            coords = line.split()
            self.x.append(float(coords[1]))
            self.y.append(float(coords[2]))
