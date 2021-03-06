# 3 Oct 2016
#  start with a known consistent matrix and then measure the number of inconsistnc detected.
# (and how does it scale with the size of the matrix) - done
# keep track of the locations of the inconsistent items - done

# 10 Oct 2016
# besides the direct check of 'b', how many other cycles is 'b' involved in (where it is the Aik or Ajk)
# if one item is changed, 'b', how many other consistency checks would then fail.  It is more n^2?
# 3n of the items will include 'b'

# take matrix full of ones
# compute difference between other matrix and matrix full of ones
# use the place with the largest diff between ones matrix and other matrix

# http://www.isc.senshu-u.ac.jp/~thc0456/EAHP/AHPweb.html


# see how many inconsistencies need to be added for the entire matrix to be altered (except the diagonal) == (n(n+1))/2

# determine what causes the number of inconsistencies to vary between runs when there are two or
# more inconsistencies (side by side, on the same line (horizontal or diagonal) etc)

# diagrams - show when an inconsistency introduced, which items are
# affected (xfig, omnigraffle) 'include graphics' command in LaTeX

# 543
# pip
# install
# pylatex
# 544
# sudo
# pip
# install
# pylatex
# 545
# sudo
# pip
# install
# pylatex[matrices]
# 546
# sudo
# pip
# install
# matplotlib
# 547
# sudo
# pip
# install
# quantities

import sys
import copy
import fractions
import random
import time
import threading
from multiprocessing import Process
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Not to use X server. For TravisCI.
import matplotlib.pyplot as plt  # noqa

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix
from pylatex.utils import italic

dataList = []  # list of lists
matrixSquares = []
matrixInputSquares = []
root = 0


def are_two_tuples_reciprocals(i, j, k, l):
    if i == l and j == k:
        return True
    return False

def parse_fraction(input_str):
    fraction_parts = input_str.split('/')
    if len(fraction_parts) == 2:
        return fraction_parts[0], fraction_parts[1]
    return fraction_parts[0], '1'


def simplify_fraction(numer, denom):
    if denom == 0:
        return 0, 0

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


def get_numerator_denominator(fraction_str):
    if '/' not in fraction_str:
        return fraction_str, '1'
    else:
        items = fraction_str.split('/')
        return items[0], items[1]


def modify_one_element(m):
    noi = 0
    for i in range(0, m.get_size()):
        for j in range(0, m.get_size()):

            if i >= j:
                continue

            old_val = m.get_item(i, j)
            old_val2 = m.get_item(j, i)

            if '/' in old_val:
                num = old_val.split('/')[0]
                denom = old_val.split('/')[1]
                new_val = str(int(num) + 1) + '/' + denom
                m.set_item(i, j, new_val)
                new_val = denom + '/' + str(int(num) + 1)
                m.set_item(j, i, new_val)
            else:
                m.set_item(i, j, str(int(old_val) + 1))
                m.set_item(j, i, '1/' + str(int(old_val) + 1))

            # print "Altered matrix: "
            # m.print_matrix()
            # print ""

            (noi, consistent) = m.check_matrix_consistency()
            if noi > 0:
                # print "Number on Inconsistencies: " + str(noi)

                if noi != (6 * (m.get_size() - 2)):
                    print "Unexpected number of inconsistencies, should have been " + str(6 * (m.get_size() - 2))
                    return

                m.set_item(i, j, old_val)
                m.set_item(j, i, old_val2)
                m.reset_inconsistency_data()
            else:
                m.set_item(i, j, old_val)
                m.set_item(j, i, old_val2)
                m.reset_inconsistency_data()

    if noi > 0 and noi == (6 * (m.get_size() - 2)):
        print "Expected number of inconsistencies (" + str(noi) + ") found, great!"
        return


def modify_elements(m, elements_to_change):
    positions = []
    k = 0
    for i in range(0, m.get_size()):
        for j in range(0, m.get_size()):
            if j > i:
                k += 1
                if j < m.get_size():
                    positions.append([i, j])

    positions = random.sample(positions, elements_to_change)

    old_values = []

    for k in range(0, len(positions)):
        i = positions[k][0]
        j = positions[k][1]
        old_val = m.get_item(i, j)

        old_values.append([m.get_item(i, j), m.get_item(j, i)])

        if '/' in old_val:
            # num = old_val.split('/')[0]
            # denom = old_val.split('/')[1]
            # new_val = str(int(num) + 1) + '/' + denom
            new_val = "998/999"
            m.set_item(i, j, new_val)
            # new_val = denom + '/' + str(int(num) + 1)
            new_val = "999/998"
            m.set_item(j, i, new_val)
        else:
            m.set_item(i, j, "999/999")
            m.set_item(j, i, "999/999")

    print "Altered matrix: "
    m.print_matrix()
    print ""
    #
    # print old_values

    (noi, consistent) = m.check_matrix_consistency()

    for k in range(0, len(old_values)):
        m.set_item(positions[k][0], positions[k][1], old_values[k][0])
        m.set_item(positions[k][1], positions[k][0], old_values[k][1])
        m.reset_inconsistency_data()

    # print "Original matrix? "
    # m.print_matrix()
    # print ""

    if noi > 0:
        if noi != (6 * (m.get_size() - 2)):
            print "Unexpected number of inconsistencies (" + str(noi) + "), should have been " + str(
                6 * (m.get_size() - 2))
            return

    if noi > 0 and noi == (6 * (m.get_size() - 2)):
        print "Expected number of inconsistencies (" + str(noi) + ") found, great!"
        return


def make_all_ones_matrix(matrix_size):
    m = []
    ones = []

    for i in range(0, matrix_size):
        ones.append('1')

    for i in range(0, matrix_size):
        m.append(copy.copy(ones))

    return m

def generate_random_matrix(matrix_size):
    l = np.random.randint(2, pow(matrix_size, 3), size=(matrix_size, matrix_size))
    m = PairwiseMatrix(make_all_ones_matrix(matrix_size))

    # matrix_elements = m.get_elements_below_diagonal()
    for i in range(0, matrix_size):
        for j in range(0, matrix_size):
            if i == j:
                continue
            m.set_item(j, i, str(l[i][i]))
            m.set_item(i, j, '1/' + str(l[i][i]))

    return m

def generate_random_consistent_matrix(matrix_size):
    l = np.random.randint(2, pow(matrix_size, 3), size=(matrix_size, matrix_size))
    m = PairwiseMatrix(make_all_ones_matrix(matrix_size))

    # matrix_elements = m.get_elements_below_diagonal()
    for i in range(0, matrix_size):
        for j in range(0, matrix_size):
            if i == j:
                continue
            m.set_item(i, j, str(l[i][i]) + '/' + str(l[j][j]))
            m.set_item(j, i, str(l[j][j]) + '/' + str(l[i][i]))

    return m

def generate_consistent_matrix(inputList, matrix_size):
    rounds_required = 0
    while True:
        rounds_required += 1

        m = PairwiseMatrix(make_all_ones_matrix(matrix_size))

        # matrix_elements = m.get_elements_below_diagonal()
        for i in range(0, matrix_size):
            for j in range(0, matrix_size):
                if i == j:
                    continue
                if (not '/' in inputList[i]) and (not '/' in inputList[j]):
                    m.set_item(i, j, str(inputList[i]) + '/' + str(inputList[j]))
                    m.set_item(j, i, str(inputList[j]) + '/' + str(inputList[i]))
                else:
                    t1 = inputList[i].split('/')
                    if len(t1) == 1:
                        t1.append('1')
                    t2 = inputList[j].split('/')
                    if len(t2) == 1:
                        t2.append('1')
                    t2.reverse()
                    answer1 = str(int(t1[0]) * int(t2[0]))
                    answer2 = str(int(t1[1]) * int(t2[1]))
                    if answer2 == '1':
                        m.set_item(i, j, answer1)
                    else:
                        m.set_item(i, j, answer1 + '/' + answer2)

                    if answer1 == '1':
                        m.set_item(j, i, answer2)
                    else:
                        m.set_item(j, i, answer2 + '/' + answer1)

        return m

# http://stackoverflow.com/questions/2065553/get-all-numbers-that-add-up-to-a-number
def sum_to_n(n, size, limit=None):
    """Produce all lists of `size` positive integers in decreasing order
    that add up to `n`."""
    if size == 1:
        yield [n]
        return
    if limit is None:
        limit = n
    start = (n + size - 1) // size
    stop = min(limit, n - size + 1) + 1
    for i in range(start, stop):
        for tail in sum_to_n(n - i, size - 1, i):
            yield [i] + tail

class PairwiseMatrix:
    def __init__(self, data=None):
        if data is None:
            data = []
        self.matrix_data = []
        self.matrix_size = 0

        if len(data) > 0:
            self.matrix_data = copy.deepcopy(data)
            self.matrix_size = len(data)

        self.inconsistent_locations = []
        self.inconsistencies_detected = 0
        self.greatest_distance_location = []
        self.greatest_distance_value = 0

    def reset_inconsistency_data(self):
        self.inconsistent_locations = []
        self.inconsistencies_detected = 0

    def reset_inconsistency_locations(self):
        self.greatest_distance_location = []
        self.greatest_distance_value = 0

    # def set_window_root(self, root_window):
    #     self.root = root_window

    def add_matrix_row(self, new_row):
        self.matrix_data.append(new_row)
        self.matrix_size += 1

    def print_matrix(self, add_trailing_whitespace=False):
        for i in range(0, self.matrix_size):
            print self.matrix_data[i]
        if add_trailing_whitespace:
            print ""

    def get_size(self):
        return self.matrix_size

    def get_row(self, rowIdx):
        return self.matrix_data[rowIdx]

    def get_column(self, colIdx):
        colData = []
        for rowIdx in range(0, len(self.matrix_data)):
            colData.append(self.matrix_data[rowIdx][colIdx])
        return colData

    def print_inconsistencies(self):
        print self.inconsistent_locations

    def get_greatest_distance_value(self):
        return self.greatest_distance_value

    def get_greatest_distance_location(self):
        return self.greatest_distance_location

    def get_item(self, x, y):
        if x > self.matrix_size - 1:
            return ""
        elif y > self.matrix_size - 1:
            return ""
        return self.matrix_data[x][y]

    def set_item(self, x, y, val):
        self.matrix_data[x][y] = val

    def check_matrix_diagonal(self):
        for i in range(0, self.matrix_size):
            if int(self.get_item(i, i)) != 1:
                return False
        return True

    def get_elements_above_diagonal(self):
        out_list = []
        for i in range(0, self.get_size()):
            for j in range(0, self.get_size()):
                if j > i:
                    out_list.append([i, j])
        return out_list

    def get_elements_below_diagonal(self):
        out_list = []
        for i in range(0, self.get_size()):
            for j in range(0, self.get_size()):
                if i > j:
                    out_list.append([i, j])
        return out_list

    def check_matrix_consistency(self):

        self.inconsistent_locations = []
        self.inconsistencies_detected = 0
        n = self.matrix_size

        for i in range(0, n):
            for j in range(0, n):
                for k in range(0, n):

                    if i == j:
                        continue

                    # Dij = Dik * Dkj
                    if verboseCount > 1:
                        print "i={0}, j={1}, k={2} -> {3}[{4},{5}] * {6}[{7},{8}] should be {9}".format(
                            str(i), str(j), str(k), str(self.get_item(i, k)), str(i), str(k),
                            str(self.get_item(k, j)), str(k), str(j), str(self.get_item(i, j)))

                    # get i,j
                    # (ij_num, ij_denom) = (0, 0)
                    # fraction_str = self.get_item(i, j)
                    # if '/' not in fraction_str:
                    #     (ij_num, ij_denom) = fraction_str, '1'
                    # else:
                    #     items = fraction_str.split('/')
                    #     (ij_num, ij_denom) = items[0], items[1]
                    #
                    # # get i,k
                    # (ik_num, ik_denom) = (0, 0)
                    # fraction_str = self.get_item(i, k)
                    # if '/' not in fraction_str:
                    #     (ik_num, ik_denom) = fraction_str, '1'
                    # else:
                    #     items = fraction_str.split('/')
                    #     (ik_num, ik_denom) = items[0], items[1]
                    #
                    # # get k,j
                    # (kj_num, kj_denom) = (0, 0)
                    # fraction_str = self.get_item(k, j)
                    # if '/' not in fraction_str:
                    #     (kj_num, kj_denom) = fraction_str, '1'
                    # else:
                    #     items = fraction_str.split('/')
                    #     (kj_num, kj_denom) = items[0], items[1]

                    (ij_num, ij_denom) = get_numerator_denominator(self.get_item(i, j))
                    (ik_num, ik_denom) = get_numerator_denominator(self.get_item(i, k))
                    (kj_num, kj_denom) = get_numerator_denominator(self.get_item(k, j))
                    # print(ij_num, ij_denom)
                    # print(ik_num, ik_denom)
                    # print(kj_num, kj_denom)

                    ij_top = (int(ik_num) * int(kj_num))
                    ij_bottom = int(ik_denom) * int(kj_denom)

                    (ij_top_simplified, ij_bottom_simplified) = simplify_fraction(ij_top, ij_bottom)

                    if ij_top_simplified == 0:
                        return (-1, -1)

                    (ij_top_real, ij_bottom_real) = simplify_fraction(int(ij_num), int(ij_denom))

                    if ij_bottom == 0:
                        return (-1, -1)

                    if (int(ij_top_simplified) != int(ij_top_real)) or \
                            (int(ij_bottom_simplified) != int(ij_bottom_real)):
                        if verboseCount >= 2:
                            print "ijTopSimplified=" + str(ij_top_simplified)
                            print "ij_bottom_simplified=" + str(ij_bottom_simplified)
                            print "ij_top_real=" + str(ij_top_real)
                            print "ij_bottom_real=" + str(ij_bottom_real)
                            print ""
                        self.inconsistent_locations.append([i, j, k])
                        self.inconsistencies_detected += 1

        return self.inconsistencies_detected, self.inconsistent_locations

    def get_distance(self, o_matrix):  # , x_pos=-1, y_pos=-1):
        total_distance = 0.0
        differences_noted = 0
        for i in range(0, self.matrix_size):
            for j in range(0, self.matrix_size):

                if i > j: #only check items above the diagonal
                    continue

                this_matrix_tuple = parse_fraction(self.get_item(i, j))
                other_matrix_tuple = parse_fraction(o_matrix.get_item(i, j))

                a = float(float(this_matrix_tuple[0]) / float(this_matrix_tuple[1]))
                b = float(float(other_matrix_tuple[0]) / float(other_matrix_tuple[1]))
                difference = abs(a - b)

                if difference != 0:
                    # print str(difference)
                    if abs(difference) > self.greatest_distance_value:
                        self.greatest_distance_value = abs(difference)
                        self.greatest_distance_location = [i, j]
                    total_distance += abs(difference)
                    differences_noted += 1

                    # print "Difference [" + str(i) + "," + str(j) + "]= " + str(abs(difference))
        return total_distance, differences_noted

    def get_most_inconsistent_tuples(self):
        abvDiag = self.get_elements_above_diagonal()
        bad_places = []

        if verboseCount > 0:
            print self.inconsistent_locations

        for i in range(0, len(self.inconsistent_locations)):
            l = self.inconsistent_locations[i]
            for j in range(i + 1, len(self.inconsistent_locations)):
                if self.inconsistent_locations[i][0] == self.inconsistent_locations[j][0] and \
                                self.inconsistent_locations[i][1] == self.inconsistent_locations[j][1]:  # compare i,j only (not k)
                    if [self.inconsistent_locations[i][0], self.inconsistent_locations[i][1]] in abvDiag: #only add tuples that are above the diagonal
                        bad_places.append([self.inconsistent_locations[i][0], self.inconsistent_locations[i][1]])
        return bad_places

    def get_sum_above_diagonal(self):
        abvDiag = self.get_elements_above_diagonal()
        sum = 0
        for i in range(0,len(abvDiag)):
            (num,denom) = parse_fraction(self.matrix_data[abvDiag[i][0]][abvDiag[i][1]])
            decValu = float(num) / float(denom)
            sum += decValu
        return sum

############## END OF CLASS ########################

# basically a brute force search method
def Search1():
    for gCount in range(0, 5):
        myList = [1, 1, 1, 1]

        m = generate_random_matrix(len(myList))
        mSum = m.get_sum_above_diagonal()
        print "Random Matrix: "
        m.print_matrix()
        print "Random Matrix Sum: " + str(mSum)
        print ""

        resultLists = []
        myList = ['1', '1', '1', '1']
        for i in range(1, 1000):

            distanceDelta = -1
            bestPosition = -1
            slotsToRevert = []
            for listIdx in range(0, len(myList)):

                myList[listIdx] = str(int(myList[listIdx]) + 1)
                mPrime = generate_consistent_matrix(myList, len(myList))
                mPrimeSum = mPrime.get_sum_above_diagonal()

                results = mPrime.get_distance(m)

                if distanceDelta < 0:  # first time in loop(s)
                    distanceDelta = results[0]
                    bestPosition = listIdx

                elif results[0] < distanceDelta:  # this iteration is better than the last run(s)
                    distanceDelta = results[0]
                    bestPosition = listIdx
                elif myList[listIdx] > 1:  # don't go below 0!
                    myList[listIdx] = str(int(myList[listIdx]) - 1)

            # save the best in this iteration
            if len(resultLists) > 0:
                (l, d) = resultLists[0]
                if distanceDelta < d:
                    resultLists = []
                    resultLists.append((copy.deepcopy(myList), distanceDelta))
            else:
                resultLists.append((copy.deepcopy(myList), distanceDelta))

        if len(resultLists) > 0:
            (l, d) = resultLists[0]
            resultMatrix = generate_consistent_matrix(l, len(l))
            results = resultMatrix.get_distance(m)

            print "Solution Set: " + str(l)
            print "Solution Matrix: "
            resultMatrix.print_matrix(True)

            print "Distance from m: " + str(results[0])
            print "Sum: " + str(resultMatrix.get_sum_above_diagonal())
            # print "Number of differences: " + str(results[1])
            print "------------------------------------------"


def Search2(resultsData, startIdx, endIdx):
    batchStartTime = time.time()
    for i in range(startIdx, endIdx):
        #myList = [2,3,4]

        iterStartTime = time.time()
        m = generate_random_matrix(i)
        # m = PairwiseMatrix()
        # m.add_matrix_row(['1', '2', '3'])
        # m.add_matrix_row(['1/2', '1', '4'])
        # m.add_matrix_row(['1/3', '1/4', '1'])
        mSum = m.get_sum_above_diagonal()
        # print "Matrix: "
        # m.print_matrix()
        # print m.check_matrix_consistency()
        # print "Matrix Sum: " + str(mSum)
        # print ""

        bestSolutionDistance = sys.maxint
        bestSolutionSet = []

        for columnIdx in range(0, i):
            columnData = m.get_column(columnIdx)
            mPrime = generate_consistent_matrix(columnData, len(columnData))
            results = mPrime.get_distance(m)
            calculatedDistance = results[0]
            if calculatedDistance < bestSolutionDistance:
                bestSolutionDistance = calculatedDistance
                bestSolutionSet = copy.copy(columnData)

            # print "Potential Solution Set: " + str(columnData)
            # mPrime.print_matrix(True)
            # print "Distance from m: " + str(calculatedDistance)
            # print "Sum: " + str(mPrime.get_sum_above_diagonal())
            # print ""

        for rowIdx in range(0, i):
            rowData = m.get_row(rowIdx)
            mPrime = generate_consistent_matrix(rowData, len(rowData))
            results = mPrime.get_distance(m)
            calculatedDistance = results[0]
            if calculatedDistance < bestSolutionDistance:
                bestSolutionDistance = calculatedDistance
                bestSolutionSet = copy.copy(columnData)
            # print "Potential Solution Set: " + str(rowData)
            # mPrime.print_matrix(True)
            # print "Distance from m: " + str(calculatedDistance)
            # print "Sum: " + str(mPrime.get_sum_above_diagonal())

        # print ""
        # print "-= Best Solution =-"
        # print "Solution Set: " + str(bestSolutionSet)
        # print "Derived Matrix"
        solutionMatrix = generate_consistent_matrix(bestSolutionSet, len(bestSolutionSet))
        # solutionMatrix.print_matrix(True)
        solutionResults = solutionMatrix.get_distance(m)
        solutionDistance = solutionResults[0]
        # print "Distance from m: " + str(solutionDistance)
        # print "Sum: " + str(solutionMatrix.get_sum_above_diagonal())

        iterDuration = time.time() - iterStartTime

        t = (i, copy.deepcopy(solutionMatrix), solutionDistance, iterDuration)
        #print t
        resultsData.append(t)

    resultsData.append((-1, 0, 0, time.time() - batchStartTime))
    return resultsData

def stuff(fname, width, *args, **kwargs):

    x = [0, 1, 2, 3, 4, 5, 6]
    y = [15, 2, 7, 1, 5, 6, 9]

    plt.plot(x, y)

    geometry_options = {"tmargin": "1cm", "lmargin": "10cm"}
    doc = Document(geometry_options=geometry_options)
    #with doc.create(Subsection('Beautiful graphs')):
    with doc.create(TikZ()):
        plot_options = 'height=6cm, width=6cm, grid=major'
        with doc.create(Axis(options=plot_options)) as plot:
            #plot.append(Plot(name='model', func='-x^5 - 242'))

            coordinates = [
                (-4.77778, 2027.60977),
                (-3.55556, 347.84069),
                (-2.33333, 22.58953),
                (-1.11111, -493.50066),
                (0.11111, 46.66082),
                (1.33333, -205.56286),
                (2.55556, -341.40638),
                (3.77778, -1169.24780),
                (5.00000, -3269.56775),
            ]

            plot.append(Plot(name='estimate', coordinates=coordinates))
    print doc.dumps_content()
if __name__ == "__main__":
    verboseCount = 0
    coresToUse = 6
    rowColumnMethodData = []
    geometricMeanMethodData = []
    randomIterationMethodData = []
    for j in range(0,50):
        threads = []
        #rowColumnMethodData = Search2(rowColumnMethodData, 3, 4)
        for i in range(0, coresToUse):
            p = Process(target=Search2, args=(rowColumnMethodData, 3, 4,))
            threads.append(p)
            p.start()
            # t = threading.Thread(target=Search2, args=(rowColumnMethodData, 3, 100,))
            # threads.append(t)
            # t.start()
        for i in range(0,len(threads)):
            threads[i].join()
        # main_thread = threading.currentThread()
        # for t in threading.enumerate():
        #     if t is main_thread:
        #         continue
        #     print 'joining ', t.getName()
        #     t.join()

    print 'Data: ' + str(rowColumnMethodData)
    #stuff('matplotlib_ex-dpi', r'1\textwidth', dpi=300)
    #stuff('matplotlib_ex-facecolor', r'0.5\textwidth', facecolor='b')

