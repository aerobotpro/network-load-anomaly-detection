from random import choice
chars = ['a','b','c','d','e','f','1','2','3','4','5','6','7','8','9','0']
class hashes:
    global chars
    def four_char():
        return str(choice(chars) + choice(chars) + choice(chars) + choice(chars))
    def eight_char():
        return str(choice(chars) + choice(chars) + choice(chars) + choice(chars)
                   + choice(chars) + choice(chars) + choice(chars) + choice(chars))
    
def convertBytes(string):
    string = string.lower()
    if "b" in string: string = int(string.replace("b", ""))
    elif "k" in string: string = int(string.replace("k", "")) * 1000
    elif "m" in string: string = int(string.replace("m", "")) * 1000000
    elif "g" in string: string = int(string.replace("g", "")) * 1000000000
    elif "t" in string: string = int(string.replace("t", "")) * 1000000000000
    else: string = None
    return string

def getAvg(array):
    return round(float(sum(array) / len(array)), 2)

