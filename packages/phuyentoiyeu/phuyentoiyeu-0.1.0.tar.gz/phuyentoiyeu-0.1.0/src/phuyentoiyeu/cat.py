class Cat:
    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def describe(self):
        print(self.getName())
