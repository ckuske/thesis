#next goal is to implement the function for difference between matrices, is by using the absolute value of the difference between each pair of
#items, and adding each difference between each pair
#could also use the max of all the difference

#start with a known consistent matrix and then measure the number of inconsistnc detected. (and how does it scale with the size of the matrix)
#keep track of the locations of the inconsistent

import numpy as np
from Tkinter import *
import time
import fractions

dataList = []  # list of lists
matrix = np.matrix
matrixSquares = []
matrixInputSquares = []
root = 0

def SimplifyFraction(inputStr):
    fractionParts = inputStr.split('/')
    if (len(fractionParts) == 1):
        return inputStr  # nothing to do

    numerator = fractionParts[0]
    denominator = fractionParts[1]
    tup = simplify_fraction(int(numerator), int(denominator))

    reducedFraction = str(tup[0]) + "/" + str(tup[1]);

    return reducedFraction


def ParseInput2():
    global matrixInputSquares
    row = []
    str = '1 3 5 7;2/6 1 10/6 8;1/5 3/5 1 1/8;1 2 3 4'
    rows = str.split(';')
    print "Original Input:"
    for i in range(0, len(rows)):
        row = rows[i].split()
        print row

    print ""
    for i in range(0, len(rows)):
        row = rows[i].split()
        for j in range(0, len(row)):
            str = SimplifyFraction(row[j])
            row[j] = str
        matrixInputSquares.append(row)


def simplify_fraction(numer, denom):
    if denom == 0:
        return "Division by 0 - result undefined"

    # Remove greatest common divisor:
    common_divisor = fractions.gcd(numer, denom)
    (reduced_num, reduced_den) = (numer / common_divisor, denom / common_divisor)
    # Note that reduced_den > 0 as documented in the gcd function.

    if reduced_den == 1:  #
        print "%d/%d is simplified to %d" % (numer, denom, reduced_num)
        return (reduced_num, reduced_den)
    elif common_divisor == 1:
        print "%d/%d is already at its most simplified state" % (numer, denom)
        return (numer, denom)
    else:
        print "%d/%d is simplified to %d/%d" % (numer, denom, reduced_num, reduced_den)
        return (reduced_num, reduced_den)

def GetNumeratorDenominator(fractionStr):
    items = fractionStr.split('/')
    if(len(items) == 1):
        return (fractionStr,'1')
    else:
        return (items[0], items[1])

def CheckMatrixConsistency2(n):
    global matrix
    global matrixSquares
    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):

                if i == j:
                    matrixSquares[i][j].config(text="1")
                    # continue

                print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                       str(matrixInputSquares[i][k]) + "[" + str(i) + "," + str(k) + "] * " + str(matrixInputSquares[k][j]) + "[" + str(
                     k) + "," + str(j) + "] should be " + str(matrixInputSquares[i][j])

                (ijNum,ijDenom) = GetNumeratorDenominator(matrixInputSquares[i][j])
                (ikNum, ikDenom) = GetNumeratorDenominator(matrixInputSquares[i][k])
                (kjNum, kjDenom) = GetNumeratorDenominator(matrixInputSquares[k][j])
                print((ijNum,ijDenom))
                print((ikNum, ikDenom))
                print((kjNum, kjDenom))

                ijTop = (int(ikNum) * int(kjNum))
                ijBottom = int(ikDenom) * int(kjDenom)

                (a,b) = simplify_fraction(ijTop,ijBottom)


                if((int(a) != int(ijNum)) and (int(b) != int(ijDenom))):
                    print "A=" + str(a)
                    print "B=" + str(b)
                    print "ijNum=" + str(ijNum)
                    print "ijDenom=" + str(ijDenom)
                    return False;

                matrixSquares[i][j].config(bg="#ff0000")  # red
                matrixSquares[i][k].config(bg="#ffff00")  # yellow
                matrixSquares[k][j].config(bg="#00ff00")  # green
                root.update()
                root.update_idletasks()
                #time.sleep(1)
                #

                root.update()
                root.update_idletasks()

                matrixSquares[i][j].config(bg="#ffffff")
                matrixSquares[i][k].config(bg="#ffffff")
                matrixSquares[k][j].config(bg="#ffffff")
                root.update()
                root.update_idletasks()
                print ""
                
    return True


# check that Dij = Dik * Dkj

def callback():
    global matrixInputSquares
    #print matrixSquares
    # if not CheckMatrixDiagonal():
    #     print "Matrix not consistent (diagonal).  Exiting!"
    #     exit()
    if not CheckMatrixConsistency2(len(matrixInputSquares)):
        print "Matrix not consistent.  Exiting!"
        exit()
    print "\nMatrix is consistent."


if __name__ == "__main__":
    global matrixInputSquares
    root = Tk()
    ParseInput2()
    print matrixInputSquares[0]
    print matrixInputSquares[1]
    print matrixInputSquares[2]

    root.attributes("-topmost", True)
    root.minsize(width=133, height=133)

    for i in range(0, len(matrixInputSquares)):
        rowSquares = []
        for j in range(0, len(matrixInputSquares)):
            w = Label(root, text=str(i) + "," + str(j))
            #print w
            w.grid(row=i, column=j)
            rowSquares.append(w)
        matrixSquares.append(rowSquares)

    b = Button(root, text="Check", command=callback).grid()
    root.mainloop()


# def GetMatrixDiagonal():
#     global matrix
#     diagonals = matrix.diagonal()
#     print diagonals

# def GetUpperMatrix(n):
#     global matrix
#     a = np.triu_indices(n)
#     print a[0]
#     return a[0]
#
# def GetLowerMatrix(n):
#     global matrix
#     a = np.tril_indices(n)
#     print a[0]
#     return a[0]

# def CheckMatrixDiagonal():
#     global matrix
#     diagonals = matrix.diagonal()
#     for i in range(0, len(diagonals.A1)):
#         if int(diagonals.A1[i]) != 1:
#             return False
#     return True
