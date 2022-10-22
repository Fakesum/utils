def xor(*orands):
        return sum(bool(x) for x in orands) == 1

def NAND (a, b):
        return (False if (a == 1 and b == 1) else True)
