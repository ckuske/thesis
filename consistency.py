import numpy as np
from Tkinter import *
import time
import fractions

dataList = []  # list of lists
matrix = np.matrix
matrixSquares = []
root = 0


def ParseInput():
    global matrix
    # matrix = np.matrix('1 2 2;.5 1 2;.5 .5 1')
    matrix = np.matrix('1 3 5;.3333333 1 1.6666666;.2 .6 1')
    print matrix.A[0]
    print matrix.A[1]
    print matrix.A[2]
    print ""


def ParseInput2():
    matrix = []
    row = []
    str = '1 3 5;1/3 1 5/3;1/5 3/5 1';
    rows = str.split(';')
    for i in range(0, len(rows)):
        row = rows[i].split()
        print row


def CheckMatrixDiagonal():
    global matrix
    diagonals = matrix.diagonal()
    for i in range(0, len(diagonals.A1)):
        if int(diagonals.A1[i]) != 1:
            return False
    return True


# check that Dij = Dik * Dkj
def CheckMatrixConsistency(n):
    global matrix
    global matrixSquares
    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):

                if i == j:
                    matrixSquares[i][j].config(text="1")
                    # continue

                print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                      str(matrix.A[i][k]) + " * " + str(matrix.A[k][j]) + ", " + \
                      str(matrix.A[i][j]) + '=' + str(matrix.A[i][k] * matrix.A[k][j])

                matrixSquares[i][j].config(bg="#ff0000")  # red
                matrixSquares[i][k].config(bg="#ffff00")  # yellow
                matrixSquares[k][j].config(bg="#00ff00")  # green

                # print(fractions.gcd(1/3,3))

                matrixSquares[i][j].config(text=str(matrix.A[i][k] * matrix.A[k][j]))

                if abs(matrix.A[i][j] - matrix.A[i][k] * matrix.A[k][j]) > .01:
                    return False
                root.update()
                root.update_idletasks()
                time.sleep(.1)

                matrixSquares[i][j].config(bg="#ffffff")
                matrixSquares[i][k].config(bg="#ffffff")
                matrixSquares[k][j].config(bg="#ffffff")
                root.update()
                root.update_idletasks()

    return True


def callback():
    # print matrixSquares
    if not CheckMatrixDiagonal():
        print "Matrix not consistent (diagonal).  Exiting!"
        exit()
    if not CheckMatrixConsistency(3):
        print "Matrix not consistent.  Exiting!"
        exit()
    print "\nMatrix is consistent."


if __name__ == "__main__":
    root = Tk()
    ParseInput()

    root.attributes("-topmost", True)
    root.minsize(width=666, height=666)

    for i in range(0, 3):
        rowSquares = []
        for j in range(0, 3):
            w = Label(root, text=str(i) + "," + str(j))
            # print w
            w.grid(row=i, column=j)
            rowSquares.append(w)
        matrixSquares.append(rowSquares)

    b = Button(root, text="OK", command=callback).grid()

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
