# 3 Oct 2016
#  start with a known consistent matrix and then measure the number of inconsistnc detected. (and how does it scale with the size of the matrix) - done
# keep track of the locations of the inconsistent items - done

# 10 Oct 2016
# besides the direct check of 'b', how many other cycles is 'b' involved in (where it is the Aik or Ajk)
# if one item is changed, 'b', how many other consistency checks would then fail.  It is more n^2?
# 3n of the items will include 'b'

# take matrix full of ones
# compute difference between other matrix and matrix full of ones
# use the place with the largest diff between ones matrix and other matrix

# http://www.isc.senshu-u.ac.jp/~thc0456/EAHP/AHPweb.html


# see how many inconsistencies need to be added for the entire matrix to be altered (except the diagonal)
# determine what causes the number of inconsistencies to vary between runs when there are two or more inconsistencies (side by side, on the same line (horizontal or diagonal) etc)
# diagrams - show when an inconsistency introduced, which items are affected (xfig, omnigraffle) 'include graphics' command in LaTeX

import copy
import fractions
import random

dataList = []  # list of lists
matrixSquares = []
matrixInputSquares = []
root = 0


class PairwiseMatrix:
    def __init__(self, data=[]):
        self.matrixData = []
        self.matrixSize = 0

        if len(data) > 0:
            self.matrixData = copy.deepcopy(data)
            self.matrixSize = len(data)

        self.inconsistentLocations = []
        self.inconsistenciesDetected = 0
        self.greatestDistanceLocation = []  
        self.greatestDistanceValue = 0

    def ResetInconsistencyData(self):
        self.inconsistentLocations = []
        self.inconsistenciesDetected = 0

    def ResetInconsistencyLocations(self):
        self.greatestDistanceLocation = []
        self.greatestDistanceValue = 0

    def setWindowRoot(self, root):
        self.root = root

    def AddMatrixRow(self, newRow):
        self.matrixData.append(newRow)
        self.matrixSize += 1

    def PrintMatrix(self):
        for i in range(0, self.matrixSize):
            print self.matrixData[i]

    def GetSize(self):
        return self.matrixSize

    def GetRow(self, i):
        return self.matrixData[i]

    def PrintInconsistencies(self):
        print self.inconsistentLocations

    def GetGreatestDistanceValue(self):
        return self.greatestDistanceValue

    def GetGreatestDistanceLocation(self):
        return self.greatestDistanceLocation

    def GetItem(self, x, y):
        if x > self.matrixSize - 1:
            return ""
        elif y > self.matrixSize - 1:
            return ""
        return self.matrixData[x][y]

    def SetItem(self, x, y, val):
        self.matrixData[x][y] = val

    def CheckMatrixDiagonal(self):
        for i in range(0, self.matrixSize):
            if int(self.GetItem(i, i)) != 1:
                return False
        return True

    def GetElementsAboveDiagonal(self):
        outList = []
        for i in range(0, self.GetSize()):
            for j in range(0, self.GetSize()):
                if j > i:
                    outList.append([j, i])
        return outList

    def CheckMatrixConsistency(self):

        self.inconsistenciesDetected = 0
        n = self.matrixSize

        for i in range(0, n):
            for j in range(0, n):
                for k in range(0, n):

                    if i == j:
                        continue

                    #Dij = Dik * Dkj
                    print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                          str(self.GetItem(i, k)) + "[" + str(i) + "," + str(k) + "] * " + str(
                        self.GetItem(k, j)) + "[" + str(
                        k) + "," + str(j) + "] should be " + str(self.GetItem(i, j))

                    # get i,j
                    (ijNum, ijDenom) = (0, 0)
                    fractionStr = self.GetItem(i, j)
                    if '/' not in fractionStr:
                        (ijNum, ijDenom) = fractionStr, '1'
                    else:
                        items = fractionStr.split('/')
                        (ijNum, ijDenom) = items[0], items[1]

                    # get i,k
                    (ikNum, ikDenom) = (0, 0)
                    fractionStr = self.GetItem(i, k)
                    if '/' not in fractionStr:
                        (ikNum, ikDenom) = fractionStr, '1'
                    else:
                        items = fractionStr.split('/')
                        (ikNum, ikDenom) = items[0], items[1]

                    # get k,j
                    (kjNum, kjDenom) = (0, 0)
                    fractionStr = self.GetItem(k, j)
                    if '/' not in fractionStr:
                        (kjNum, kjDenom) = fractionStr, '1'
                    else:
                        items = fractionStr.split('/')
                        (kjNum, kjDenom) = items[0], items[1]

                    (ijNum, ijDenom) = GetNumeratorDenominator(self.GetItem(i, j))
                    (ikNum, ikDenom) = GetNumeratorDenominator(self.GetItem(i, k))
                    (kjNum, kjDenom) = GetNumeratorDenominator(self.GetItem(k, j))
                    # print(ijNum, ijDenom)
                    # print(ikNum, ikDenom)
                    # print(kjNum, kjDenom)

                    ijTop = (int(ikNum) * int(kjNum))
                    ijBottom = int(ikDenom) * int(kjDenom)

                    (ijTopSimplified, ijBottomSimplified) = simplify_fraction(ijTop, ijBottom)
                    (ijTopReal, ijBottomReal) = simplify_fraction(int(ijNum), int(ijDenom))

                    if ijBottom == 0:
                        return ""

                    if (int(ijTopSimplified) != int(ijTopReal)) or (int(ijBottomSimplified) != int(ijBottomReal)):
                        print "ijTopSimplified=" + str(ijTopSimplified)
                        print "ijBottomSimplified=" + str(ijBottomSimplified)
                        print "ijTopReal=" + str(ijTopReal)
                        print "ijBottomReal=" + str(ijBottomReal)
                        print ""
                        self.inconsistentLocations.append([i, j, k])
                        self.inconsistenciesDetected += 1

        return (self.inconsistenciesDetected, self.inconsistentLocations)

    def GetDistance(self, oMatrix, xPos=-1, yPos=-1):
        totalDistance = 0.0
        differencesNoted = 0
        for i in range(0, self.matrixSize):
            for j in range(0, self.matrixSize):

                thisMatrixTuple = list(ParseFraction(self.GetItem(i, j)))
                thisMatrixIsOnes = (thisMatrixTuple[0] == thisMatrixTuple[1])

                otherMatrixTuple = list(ParseFraction(oMatrix.GetItem(i, j)))
                otherMatrixIsOnes = (otherMatrixTuple[0] == otherMatrixTuple[1])

                # if thisMatrixTuple[0] == thisMatrixTuple[1]

                if thisMatrixTuple[1] != otherMatrixTuple[1]:  # find common denominator
                    lcd = 1
                    a = int(thisMatrixTuple[1])
                    b = int(otherMatrixTuple[1])
                    common_divisor = fractions.gcd(a, b)
                    lcd = ((a * b) / common_divisor)

                    if int(thisMatrixTuple[1]) != lcd:
                        thisMatrixTuple[0] = str(int(thisMatrixTuple[0]) * lcd)
                        thisMatrixTuple[1] = str(lcd)

                    if int(otherMatrixTuple[1]) != lcd:
                        otherMatrixTuple[0] = str(int(otherMatrixTuple[0]) * lcd)
                        otherMatrixTuple[1] = str(lcd)

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
                    if abs(difference) > self.greatestDistanceValue:
                        self.greatestDistanceValue = abs(difference)
                        self.greatestDistanceLocation = [i, j]
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

    numerator = int(fractionParts[0])
    denominator = int(fractionParts[1])
    # tup = simplify_fraction(int(numerator), int(denominator))

    if denominator == 0:
        return ""
    common_divisor = fractions.gcd(numerator, denominator)
    (reduced_num, reduced_den) = (numerator / common_divisor, denominator / common_divisor)
    tup = ()

    if reduced_den == 1:  #
        tup = (reduced_num, reduced_den)
    elif common_divisor == 1:
        tup = (numerator, denominator)
    else:
        tup = (reduced_num, reduced_den)

    reducedFraction = str(tup[0]) + "/" + str(tup[1])

    return reducedFraction


def simplify_fraction(numer, denom):
    if denom == 0:
        return "Division by 0 - result undefined"

    # Remove greatest common divisor:
    common_divisor = fractions.gcd(numer, denom)
    (reduced_num, reduced_den) = (numer / common_divisor, denom / common_divisor)
    # Note that reduced_den > 0 as documented in the gcd function.

    if reduced_den == 1:  #
        return reduced_num, reduced_den
    elif common_divisor == 1:
        return numer, denom
    else:
        return reduced_num, reduced_den


def GetNumeratorDenominator(fractionStr):
    if '/' not in fractionStr:
        return fractionStr, '1'
    else:
        items = fractionStr.split('/')
        return items[0], items[1]


def ModifyOneElement(m):

    for i in range(0, m.GetSize()):
        for j in range(0, m.GetSize()):

            if i >= j:
                continue

            oldVal = m.GetItem(i, j)
            oldVal2 = m.GetItem(j, i)

            if '/' in oldVal:
                num = oldVal.split('/')[0]
                denom = oldVal.split('/')[1]
                newVal = str(int(num) + 1) + '/' + denom
                m.SetItem(i, j, newVal)
                newVal = denom + '/' + str(int(num) + 1)
                m.SetItem(j, i, newVal)
            else:
                m.SetItem(i, j, str(int(oldVal) + 1))
                m.SetItem(j, i, '1/' + str(int(oldVal) + 1))

            # print "Altered matrix: "
            # m.PrintMatrix()
            # print ""

            (noi, consistent) = m.CheckMatrixConsistency()
            if noi > 0:
                # print "Number on Inconsistencies: " + str(noi)

                if noi != (6 * (m.GetSize() - 2)):
                    print "Unexpected number of inconsistencies, should have been " + str(6 * (m.GetSize() - 2))
                    return

                m.SetItem(i, j, oldVal)
                m.SetItem(j, i, oldVal2)
                m.ResetInconsistencyData()
            else:
                m.SetItem(i, j, oldVal)
                m.SetItem(j, i, oldVal2)
                m.ResetInconsistencyData()

    if noi > 0 and noi == (6 * (m.GetSize() - 2)):
        print "Expected number of inconsistencies (" + str(noi) + ") found, great!"
        return


def ModifyElements(m, elementsToChange):
    positions = []
    prevValues = []
    k = 0
    for i in range(0, m.GetSize()):
        for j in range(0, m.GetSize()):
            if j > i:
                k = k + 1
                if j < m.GetSize():
                    positions.append([i,j])

    positions = random.sample(positions, elementsToChange)

    oldValues = []

    for k in range(0, len(positions)):
        i = positions[k][0]
        j = positions[k][1]
        oldVal = m.GetItem(i, j)

        oldValues.append([m.GetItem(i, j), m.GetItem(j, i)])

        if '/' in oldVal:
            num = oldVal.split('/')[0]
            denom = oldVal.split('/')[1]
            # newVal = str(int(num) + 1) + '/' + denom
            newVal = "999/999"
            m.SetItem(i, j, newVal)
            # newVal = denom + '/' + str(int(num) + 1)
            m.SetItem(j, i, newVal)
        else:
            m.SetItem(i, j, "999/999")
            m.SetItem(j, i, "999/999")

    print "Altered matrix: "
    m.PrintMatrix()
    print ""
    #
    # print oldValues

    (noi, consistent) = m.CheckMatrixConsistency()

    for k in range(0, len(oldValues)):
        m.SetItem(positions[k][0], positions[k][1], oldValues[k][0])
        m.SetItem(positions[k][1], positions[k][0], oldValues[k][1])
        m.ResetInconsistencyData()

    # print "Original matrix? "
    # m.PrintMatrix()
    # print ""

    if noi > 0:
        if noi != (6 * (m.GetSize() - 2)):
            print "Unexpected number of inconsistencies (" + str(noi) + "), should have been " + str(6 * (m.GetSize() - 2))
            return

    if noi > 0 and noi == (6 * (m.GetSize() - 2)):
        print "Expected number of inconsistencies (" + str(noi) + ") found, great!"
        return

def GenerateConsistentMatrix(matrixSize):
    random.seed()
    while True:
        lists = []
        m = PairwiseMatrix([['1' for count in range(matrixSize)] for count in range(matrixSize)])
        w = random.sample(range(2, pow(matrixSize, 3)), matrixSize*10)
        w.sort()
        print ""
        print "Random numbers: " + str(w)
        c = 0
        idx = 0

        matrixElements = m.GetElementsAboveDiagonal()
        for i in range(0, len(matrixElements)):
            choice1 = random.choice(w)
            choice2 = random.choice(w)
            m.SetItem(matrixElements[i][0], matrixElements[i][1], str(choice1) + '/' + str(choice2))
            m.SetItem(matrixElements[i][1], matrixElements[i][0], str(choice2) + '/' + str(choice1))

        m.PrintMatrix()
        # for i in range(0, matrixSize):
        #     for j in range(0, matrixSize):
        #         if j > i:
        #             m.SetItem(i, j, str(w[i]) + '/' + str(w[j]))
        #             m.SetItem(j, i, str(w[j]) + '/' + str(w[i]))
        #             c += 2
        #             idx += 1
        # print m.GetElementsAboveDiagonal()
        #
        # print c
        (noi, consistent) = m.CheckMatrixConsistency()

        if noi == 0:
            m.PrintMatrix()
            m.ResetInconsistencyData()
            ModifyElements(m,2)
            return



if __name__ == "__main__":
    for i in range(4, 5):
        GenerateConsistentMatrix(i)

        # m.AddMatrixRow(['1', '18/31', '18/51', '18/55'])
        # m.AddMatrixRow(['31/18', '1', '31/51', '31/55'])
        # m.AddMatrixRow(['51/18', '51/31', '1', '51/55'])
        # m.AddMatrixRow(['55/18', '55/31', '55/51', '1'])

        # m = PairwiseMatrix()
        # m.AddMatrixRow(['1', '18/31', '18/51', '18/55'])
        # m.AddMatrixRow(['31/18', '1', '31/51', '31/55'])
        # m.AddMatrixRow(['51/18', '51/31', '1', '51/55'])
        # m.AddMatrixRow(['55/18', '55/31', '55/51', '1'])
        # m.PrintMatrix()
        # (noi, consistent) = m.CheckMatrixConsistency()
        # print "Inconsistencies: " + str(noi)
        # if noi > 0:
        #     if noi != (6 * (m.GetSize() - 2)):
        #         print "Unexpected number of inconsistencies (" + str(noi) + "), should have been " + str(6 * (m.GetSize() - 2))
