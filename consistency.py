# 3 Oct 2016
#  start with a known consistent matrix and then measure the number of inconsistnc detected. (and how does it scale with the size of the matrix)
# keep track of the locations of the inconsistent items

# 10 Oct 2016
# besides the direct check of 'b', how many other cycles is 'b' involved in (where it is the Aik or Ajk)
# if one item is changed, 'b', how many other consistency checks would then fail.  It is more n^2?
# 3n of the items will include 'b'

# take matrix full of ones
# computer difference between other matrix and matrix full of ones
# use the place with the largest diff between ones matrix and other matrix

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

    def setWindowRoot(self, root):
        self.root = root

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

    def CheckMatrixDiagonal(self):
        for i in range(0, self.matrixSize):
            if int(self.GetItem(i, i)) != 1:
                return False
        return True

    def CheckMatrixConsistency(self):

        n = self.matrixSize

        for i in range(0, n):
            for j in range(0, n):
                for k in range(0, n):

                    # if i == j:
                    #    matrixSquares[i][j].config(text="1")
                        # continue

                    # print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                    #       str(self.GetItem(i, k)) + "[" + str(i) + "," + str(k) + "] * " + str(
                    #     self.GetItem(k, j)) + "[" + str(
                    #     k) + "," + str(j) + "] should be " + str(self.GetItem(i, j))

                    (ijNum, ijDenom) = GetNumeratorDenominator(self.GetItem(i, j))
                    (ikNum, ikDenom) = GetNumeratorDenominator(self.GetItem(i, k))
                    (kjNum, kjDenom) = GetNumeratorDenominator(self.GetItem(k, j))
                    # print(ijNum, ijDenom)
                    # print(ikNum, ikDenom)
                    # print(kjNum, kjDenom)

                    ijTop = (int(ikNum) * int(kjNum))
                    ijBottom = int(ikDenom) * int(kjDenom)

                    (a, b) = simplify_fraction(ijTop, ijBottom)

                    if (int(a) != int(ijNum)) and (int(b) != int(ijDenom)):
                        print "A=" + str(a)
                        print "B=" + str(b)
                        print "ijNum=" + str(ijNum)
                        print "ijDenom=" + str(ijDenom)
                        return False

                        # print ""


        return True

    def GetDistance(self, oMatrix):
        totalDistance = 0.0
        differencesNoted = 0
        for i in range(0, self.matrixSize):
            for j in range(0, self.matrixSize):

                thisMatrixTuple = list(ParseFraction(self.GetItem(i, j)))
                thisMatrixIsOnes = (thisMatrixTuple[0] == thisMatrixTuple[1])

                otherMatrixTuple = list(ParseFraction(oMatrix.GetItem(i, j)))
                otherMatrixIsOnes = (otherMatrixTuple[0] == otherMatrixTuple[1])

                #if thisMatrixTuple[0] == thisMatrixTuple[1]

                if thisMatrixTuple[1] != otherMatrixTuple[1]:  # find common denominator
                    lcd = 1
                    a = int(thisMatrixTuple[1])
                    b = int(otherMatrixTuple[1])
                    common_divisor = fractions.gcd(a, b)
                    lcd = ((a * b) / common_divisor)

                    # if thisMatrixTuple[0] != thisMatrixTuple[1]:  # if it's not a whole number
                    #     thisMatrixTuple[0] = str(int(thisMatrixTuple[0]) * (lcd / a))
                    #     thisMatrixTuple[1] = str(lcd)
                    #
                    # if otherMatrixTuple[0] != otherMatrixTuple[1]:  # if it's not a whole number
                    #     otherMatrixTuple[0] = str(int(otherMatrixTuple[0]) * (lcd / b))
                    #     otherMatrixTuple[1] = str(lcd)
                    #
                    # else:
                    if int(thisMatrixTuple[1]) != lcd:
                        thisMatrixTuple[0] = str(int(thisMatrixTuple[0]) * lcd)
                        thisMatrixTuple[1] = str(lcd)
                        # if int(otherMatrixTuple[1]) == lcd:
                        #    otherMatrixTuple[0] = str(int(otherMatrixTuple[0]) * lcd)
                    if int(otherMatrixTuple[1]) != lcd:
                        otherMatrixTuple[0] = str(int(otherMatrixTuple[0]) * lcd)
                        otherMatrixTuple[1] = str(lcd)
                        # if int(thisMatrixTuple[1]) == lcd:
                        #    thisMatrixTuple[0] = str(int(thisMatrixTuple[0]) * lcd)

                    difference = abs((float(thisMatrixTuple[0]) - float(otherMatrixTuple[0])) / lcd)
                else:
                    lcd = int(thisMatrixTuple[1])
                    if int(thisMatrixTuple[1]) != lcd:
                        thisMatrixTuple[0] = str(int(thisMatrixTuple[0]) * lcd)
                        thisMatrixTuple[1] = str(lcd)
                    if int(otherMatrixTuple[1]) != lcd:
                        otherMatrixTuple[0] = str(int(otherMatrixTuple[0]) * lcd)
                        otherMatrixTuple[1] = str(lcd)
                    difference = abs((float(thisMatrixTuple[0]) - float(otherMatrixTuple[0])) / lcd)

                if (difference != 0):
                    totalDistance += abs(difference)
                    differencesNoted += 1

                # print "Difference [" + str(i) + "," + str(j) + "]= " + str(abs(difference))
        return (totalDistance, differencesNoted)

def ParseFraction(inputStr):
    fractionParts = inputStr.split('/')
    if len(fractionParts) == 2:
        return fractionParts[0], fractionParts[1]
    return fractionParts[0], '1'

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
        #print "%d/%d is simplified to %d" % (numer, denom, reduced_num)
        return reduced_num, reduced_den
    elif common_divisor == 1:
        #print "%d/%d is already at its most simplified state" % (numer, denom)
        return numer, denom
    else:
        #print "%d/%d is simplified to %d/%d" % (numer, denom, reduced_num, reduced_den)
        return reduced_num, reduced_den


def GetNumeratorDenominator(fractionStr):
    items = fractionStr.split('/')
    if len(items) == 1:
        return fractionStr, '1'
    else:
        return items[0], items[1]

    def CheckMatrixConsistency(self):
        n = self.matrixSize
        for i in range(0, n):
            for j in range(0, n):
                for k in range(0, n):

                    if i == j:
                        matrixSquares[i][j].config(text="1")
                        # continue

                    print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                          str(self.GetItem(i, k)) + "[" + str(i) + "," + str(k) + "] * " + str(
                        self.GetItem(k, j)) + "[" + str(
                        k) + "," + str(j) + "] should be " + str(self.GetItem(i, j))

                    (ijNum, ijDenom) = GetNumeratorDenominator(self.GetItem(i, j))
                    (ikNum, ikDenom) = GetNumeratorDenominator(self.GetItem(i, k))
                    (kjNum, kjDenom) = GetNumeratorDenominator(self.GetItem(k, j))
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

                    self.root.update()
                    self.root.update_idletasks()

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
    p.setWindowRoot(root)
    center(root)
    p.CheckMatrixConsistency()
    # if p.CheckMatrixConsistency():
    #     middle.config(text="Consistent!")
    # else:
    #     middle.config(text="Not Consistent")
    # root.update()
    # if not CheckMatrixConsistency(len(matrixInputSquares)):
    #     print "Matrix not consistent.  Exiting!"
    #     exit()
    # print "\nMatrix is consistent."

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
    allOnes = PairwiseMatrix()
    allOnes.AddMatrixRow(['1', '1', '1'])
    allOnes.AddMatrixRow(['1', '1', '1'])
    allOnes.AddMatrixRow(['1', '1', '1'])
    allOnes.PrintMatrix()

    #1 3 5;2/6 1 10/6;1/5 3/5 1
    p = PairwiseMatrix()
    p.AddMatrixRow(['1','3', '5'])
    p.AddMatrixRow(['1/3', '1', '5/3'])
    p.AddMatrixRow(['1/5','3/5','1'])
    p.PrintMatrix()

    # p2 = PairwiseMatrix()
    # p2.AddMatrixRow(['2', '3', '5'])
    # p2.AddMatrixRow(['1/3', '1', '10/6'])
    # p2.AddMatrixRow(['1/5', '7/10', '1'])
    # p2.PrintMatrix()

    print "Matrix Diagonal Is 'Good': " + str(p.CheckMatrixDiagonal())
    print "Matrix Is Consistent: " + str(p.CheckMatrixConsistency())

    distanceTup = p.GetDistance(allOnes)
    print "Total Distance between matrices = " + str(distanceTup[0]) + ", differences = " + str(distanceTup[1])
