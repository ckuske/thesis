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

    def CheckMatrixConsistency(self):

        self.inconsistenciesDetected = 0
        n = self.matrixSize

        for i in range(0, n):
            for j in range(0, n):
                for k in range(0, n):

                    if i == j:
                        continue

                    #Dij = Dik * Dkj
                    # print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                    #      str(self.GetItem(i, k)) + "[" + str(i) + "," + str(k) + "] * " + str(
                    #      self.GetItem(k, j)) + "[" + str(
                    #      k) + "," + str(j) + "] should be " + str(self.GetItem(i, j))

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

                    # (a, b) = simplify_fraction(ijTop, ijBottom)

                    if ijBottom == 0:
                        return ""
                    common_divisor = fractions.gcd(ijTop, ijBottom)
                    (reduced_num, reduced_den) = (ijTop / common_divisor, ijBottom / common_divisor)
                    tup = ()

                    if reduced_den == 1:  #
                        tup = (reduced_num, reduced_den)
                    elif common_divisor == 1:
                        tup = (ijTop, ijBottom)
                    else:
                        tup = (reduced_num, reduced_den)
                    (a, b) = tup

                    if (int(a) != int(ijNum)) or (int(b) != int(ijDenom)):
                        # print "A=" + str(a)
                        # print "B=" + str(b)
                        # print "ijNum=" + str(ijNum)
                        # print "ijDenom=" + str(ijDenom)
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


# def SimplifyFraction(inputStr):
#     fractionParts = inputStr.split('/')
#     if len(fractionParts) == 1:
#         return inputStr  # nothing to do
#
#     numerator = int(fractionParts[0])
#     denominator = int(fractionParts[1])
#     # tup = simplify_fraction(int(numerator), int(denominator))
#
#     if denominator == 0:
#         return ""
#     common_divisor = fractions.gcd(numerator, denominator)
#     (reduced_num, reduced_den) = (numerator / common_divisor, denominator / common_divisor)
#     tup = ()
#
#     if reduced_den == 1:  #
#         tup = (reduced_num, reduced_den)
#     elif common_divisor == 1:
#         tup = (numerator, denominator)
#     else:
#         tup = (reduced_num, reduced_den)
#
#     reducedFraction = str(tup[0]) + "/" + str(tup[1])
#
#     return reducedFraction


# def ParseInput():
#     global matrixInputSquares
#     matrixStr = '1 3 5;2/6 1 10/6;1/5 3/5 1'
#     rows = matrixStr.split(';')
#     print "Original Input:"
#     for i in range(0, len(rows)):
#         row = rows[i].split()
#         print row
#
#     print ""
#     for i in range(0, len(rows)):
#         row = rows[i].split()
#         for j in range(0, len(row)):
#             matrixStr = SimplifyFraction(row[j])
#             row[j] = matrixStr
#         matrixInputSquares.append(row)


#
# def simplify_fraction(numer, denom):
#     if denom == 0:
#         return "Division by 0 - result undefined"
#
#     # Remove greatest common divisor:
#     common_divisor = fractions.gcd(numer, denom)
#     (reduced_num, reduced_den) = (numer / common_divisor, denom / common_divisor)
#     # Note that reduced_den > 0 as documented in the gcd function.
#
#     if reduced_den == 1:  #
#         #print "%d/%d is simplified to %d" % (numer, denom, reduced_num)
#         return reduced_num, reduced_den
#     elif common_divisor == 1:
#         #print "%d/%d is already at its most simplified state" % (numer, denom)
#         return numer, denom
#     else:
#         #print "%d/%d is simplified to %d/%d" % (numer, denom, reduced_num, reduced_den)
#         return reduced_num, reduced_den


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
            m.SetItem(i, j, str(int(oldVal) + 1))
            m.SetItem(j, i, '1/' + str(int(oldVal) + 1))
            m.PrintMatrix()

            (noi, consistent) = m.CheckMatrixConsistency()
            if noi > 0:
                print "Number on Inconsistencies: " + str(noi)

                if noi != (6 * (m.GetSize() - 2)):
                    print "Unexpected number of inconsistencies!"
                    return

                m.SetItem(i, j, oldVal)
                m.SetItem(j, i, oldVal2)
                m.ResetInconsistencyData()
                # break
            else:
                m.SetItem(i, j, oldVal)
                m.SetItem(j, i, oldVal2)
                m.ResetInconsistencyData()
                # if noi > 0:
                #     break
    if noi == (6 * (m.GetSize() - 2)):
        print ""
        print "Expected number of inconsistencies found, great!"


def FunctionFun():
    for i in range(0, 10 + 1):
        # print str(i) + "->" + str(2*(i-2) + 4*(i-2))
        print str(i) + "->" + str(6 * (i - 2))


def GenerateConsistentMatrix(matrixSize):
    random.seed()
    while True:
        lists = []
        m = PairwiseMatrix()
        for i in range(0, matrixSize):
            l = random.sample(range(2, 81), matrixSize)
            # l.sort()
            # print l
            lists.append(l)

        for i in range(0, matrixSize):
            for j in range(0, matrixSize):
                lists[i][j] = str(lists[i][j])
                if i == j:
                    lists[i][j] = '1'
                if i > j:
                    lists[i][j] = '1' + '/' + str(lists[j][i])
            m.AddMatrixRow(lists[i])
            # print lists[i]
        print ""
        m.PrintMatrix()
        lists = []
        (noi, consistent) = m.CheckMatrixConsistency()

        if noi == 0:
            print ""
            print "Matrix selected"
            m.PrintMatrix()
            print ""
            ModifyOneElement(m)
            return m


if __name__ == "__main__":
    GenerateConsistentMatrix(3)
    # FunctionFun()
    # ModifyOneElement()
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # args = parser.parse_args()
    #
    # matrixFun = PairwiseMatrix()
    # matrixFun.AddMatrixRow(['1',   '2',   '10'])
    # matrixFun.AddMatrixRow(['1/2', '1',   '6'])
    # matrixFun.AddMatrixRow(['1/10', '1/6', '1'])
    #
    # # matrixFun.AddMatrixRow(['1',      '2',     '10',    '100'])
    # # matrixFun.AddMatrixRow(['1/2',    '1',     '5',     '50'])
    # # matrixFun.AddMatrixRow(['1/10',   '1/5',   '1',     '10'])
    # # matrixFun.AddMatrixRow(['1/100',  '1/50',  '1/10',  '1'])
    #
    # # matrixFun.AddMatrixRow(['1',       '2',       '10',      '100',  '1000'])
    # # matrixFun.AddMatrixRow(['1/2',     '1',       '5',       '50',    '500'])
    # # matrixFun.AddMatrixRow(['1/10',    '1/5',     '1',       '10',    '100'])
    # # matrixFun.AddMatrixRow(['1/100',   '1/50',    '1/10',    '1',      '10'])
    # # matrixFun.AddMatrixRow(['1/1000',  '1/500',   '1/100',   '1/10',    '1'])
    #
    # (noi, consistent) = matrixFun.CheckMatrixConsistency()
    # if noi > 0:
    #     print "Matrix not consistent"
    #     print "Number on Inconsistencies: " + str(noi)
    #     print consistent
    # else:
    #     print "Matrix consistent!"
