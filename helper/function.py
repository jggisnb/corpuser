
import random

def random_d():
    return str(random.randint(0,9))

def random_w_d():
    asciis =  [i for i in range(48,58)]
    asciis += [i for i in range(65,91)]
    asciis += [i for i in range(97,123)]
    return str(chr(asciis[random.randint(0, len(asciis) - 1)]))

def random_w_d_():
    asciis =  [95]
    asciis += [i for i in range(48, 58)]
    asciis += [i for i in range(65, 91)]
    asciis += [i for i in range(97, 123)]
    return str(chr(asciis[random.randint(0, len(asciis) - 1)]))
