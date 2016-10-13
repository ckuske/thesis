# next goal is to implement the function for difference between matrices, is by using the absolute value of the difference between each pair of
# items, and adding each difference between each pair
# could also use the max of all the difference

# start with a known consistent matrix and then measure the number of inconsistnc detected. (and how does it scale with the size of the matrix)
# keep track of the locations of the inconsistent

import fractions

dataList = []  # list of lists
matrixSquares = []
matrixInputSquares = []
root = 0


class PairwiseMatrix:
    matrixSize = 0  # NxN matrix

    def __init__(self):
        self.matrixData = []
        self.matrixSize = 0

    def AddMatrixRow(self, newRow):
        self.matrixData.append(newRow)
        self.matrixSize += 1

    def PrintMatrix(self):
        for i in range(0,self.matrixSize):
            print self.matrixData[i]
        print ""

    def GetSize(self):
        return self.matrixSize

    def GetRow(self,i):
        return self.matrixData[i]

    def GetItem(self,x,y):
        if x > self.matrixSize - 1:
            return ""
        elif y > self.matrixSize - 1:
            return ""
        return self.matrixData[x][y]

    def GetDistance(self, oMatrix):
        totalDistance = 0.0
        for i in range(0, self.matrixSize):
            for j in range(0, self.matrixSize):

                thisMatrixTuple = list(ParseFraction(self.GetItem(i, j)))
                otherMatrixTuple = list(ParseFraction(oMatrix.GetItem(i, j)))

                #if thisMatrixTuple[0] == thisMatrixTuple[1]

                if thisMatrixTuple[1] != otherMatrixTuple[1]:  # find common denominator
                    a = int(thisMatrixTuple[1])
                    b = int(otherMatrixTuple[1])
                    common_divisor = fractions.gcd(a, b)
                    lcd = ((a * b) / common_divisor)
                    thisMatrixTuple[0] = str(int(thisMatrixTuple[0]) * (lcd / a))
                    thisMatrixTuple[1] = str(lcd)
                    otherMatrixTuple[0] = str(int(otherMatrixTuple[0]) * (lcd / b))
                    otherMatrixTuple[1] = str(lcd)
                    difference = abs((float(thisMatrixTuple[0]) - float(otherMatrixTuple[0])) / lcd)
                elif thisMatrixTuple[0] == thisMatrixTuple[1]:
                    difference = abs(int(thisMatrixTuple[0])) - int(otherMatrixTuple[0])
                else:
                    difference = abs(int(thisMatrixTuple[0]) - int(otherMatrixTuple[0]))

                totalDistance += abs(difference)

                # print "Difference [" + str(i) + "," + str(j) + "]= " + str(abs(difference))
        return totalDistance

def ParseFraction(inputStr):
    fractionParts = inputStr.split('/')
    if len(fractionParts) == 2:
        return fractionParts[0], fractionParts[1]
    return fractionParts[0], fractionParts[0]

def SimplifyFraction(inputStr):
    fractionParts = inputStr.split('/')
    if len(fractionParts) == 1:
        return inputStr  # nothing to do

    numerator = fractionParts[0]
    denominator = fractionParts[1]
    tup = simplify_fraction(int(numerator), int(denominator))

    reducedFraction = str(tup[0]) + "/" + str(tup[1])

    return reducedFraction


def ParseInput():
    global matrixInputSquares
    matrixStr = '1 3 5;2/6 1 10/6;1/5 3/5 1'
    rows = matrixStr.split(';')
    print "Original Input:"
    for i in range(0, len(rows)):
        row = rows[i].split()
        print row

    print ""
    for i in range(0, len(rows)):
        row = rows[i].split()
        for j in range(0, len(row)):
            matrixStr = SimplifyFraction(row[j])
            row[j] = matrixStr
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
        return reduced_num, reduced_den
    elif common_divisor == 1:
        print "%d/%d is already at its most simplified state" % (numer, denom)
        return numer, denom
    else:
        print "%d/%d is simplified to %d/%d" % (numer, denom, reduced_num, reduced_den)
        return reduced_num, reduced_den


def GetNumeratorDenominator(fractionStr):
    items = fractionStr.split('/')
    if len(items) == 1:
        return fractionStr, '1'
    else:
        return items[0], items[1]


def CheckMatrixConsistency(n):
    global matrixSquares
    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):

                if i == j:
                    matrixSquares[i][j].config(text="1")
                    # continue

                print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                      str(matrixInputSquares[i][k]) + "[" + str(i) + "," + str(k) + "] * " + str(
                    matrixInputSquares[k][j]) + "[" + str(
                    k) + "," + str(j) + "] should be " + str(matrixInputSquares[i][j])

                (ijNum, ijDenom) = GetNumeratorDenominator(matrixInputSquares[i][j])
                (ikNum, ikDenom) = GetNumeratorDenominator(matrixInputSquares[i][k])
                (kjNum, kjDenom) = GetNumeratorDenominator(matrixInputSquares[k][j])
                print(ijNum, ijDenom)
                print(ikNum, ikDenom)
                print(kjNum, kjDenom)

                ijTop = (int(ikNum) * int(kjNum))
                ijBottom = int(ikDenom) * int(kjDenom)

                (a, b) = simplify_fraction(ijTop, ijBottom)

                if (int(a) != int(ijNum)) and (int(b) != int(ijDenom)):
                    print "A=" + str(a)
                    print "B=" + str(b)
                    print "ijNum=" + str(ijNum)
                    print "ijDenom=" + str(ijDenom)
                    return False

                matrixSquares[i][j].config(bg="#ff0000")  # red
                matrixSquares[i][k].config(bg="#ffff00")  # yellow
                matrixSquares[k][j].config(bg="#00ff00")  # green
                root.update()
                root.update_idletasks()
                # time.sleep(1)
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
    # print matrixSquares
    # if not CheckMatrixDiagonal():
    #     print "Matrix not consistent (diagonal).  Exiting!"
    #     exit()
    if not CheckMatrixConsistency(len(matrixInputSquares)):
        print "Matrix not consistent.  Exiting!"
        exit()
    print "\nMatrix is consistent."

def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


if __name__ == "__main__":

    #1 3 5;2/6 1 10/6;1/5 3/5 1
    p = PairwiseMatrix()
    p.AddMatrixRow(['1','3','5'])
    p.AddMatrixRow(['2/6','1','10/6'])
    p.AddMatrixRow(['1/5','3/5','1'])
    p.PrintMatrix()


    p2 = PairwiseMatrix()
    p2.AddMatrixRow(['1','2','3'])
    p2.AddMatrixRow(['4','1','6'])
    p2.AddMatrixRow(['7','8','1'])
    p2.PrintMatrix()

    distance = p2.GetDistance(p)

    print "Total Distance between matrices = " + str(distance)

    # root = Tk()
    # ParseInput()
    #
    # root.attributes("-topmost", True)
    # root.minsize(width=133, height=133)
    # center(root)
    #
    # for i in range(0, len(matrixInputSquares)):
    #     rowSquares = []
    #     for j in range(0, len(matrixInputSquares)):
    #         w = Label(root, text=str(i) + "," + str(j))
    #         # print w
    #         w.grid(row=i, column=j)
    #         rowSquares.append(w)
    #     matrixSquares.append(rowSquares)
    #
    # b = Button(root, text="Check", command=callback).grid()
    # root.mainloop()


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
