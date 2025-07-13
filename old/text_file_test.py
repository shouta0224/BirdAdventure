import numpy as np
file = open("txt/test.txt", "w+")
a = [
    ["あいうえお", 0]
    ]
a = str(a)
file.write(a)
file.close()