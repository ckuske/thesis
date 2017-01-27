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


# see how many inconsistencies need to be added for the entire matrix to be altered (except the diagonal)

# determine what causes the number of inconsistencies to vary between runs when there are two or
# more inconsistencies (side by side, on the same line (horizontal or diagonal) etc)

# diagrams - show when an inconsistency introduced, which items are
# affected (xfig, omnigraffle) 'include graphics' command in LaTeX

import copy
import fractions
import random

import numpy as np

dataList = []  # list of lists
matrixSquares = []
matrixInputSquares = []
root = 0


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

    def print_matrix(self):
        for i in range(0, self.matrix_size):
            print self.matrix_data[i]

    def get_size(self):
        return self.matrix_size

    def get_row(self, i):
        return self.matrix_data[i]

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
                    out_list.append([j, i])
        return out_list

    def get_elements_below_diagonal(self):
        out_list = []
        for i in range(0, self.get_size()):
            for j in range(0, self.get_size()):
                if i > j:
                    out_list.append([j, i])
        return out_list

    def check_matrix_consistency(self):

        self.inconsistencies_detected = 0
        n = self.matrix_size

        for i in range(0, n):
            for j in range(0, n):
                for k in range(0, n):

                    if i == j:
                        continue

                    # Dij = Dik * Dkj
                    # print "i=" + str(i) + ", j=" + str(j) + ", k=" + str(k) + " -> " + \
                    #       str(self.get_item(i, k)) + "[" + str(i) + "," + str(k) + "] * " + str(
                    #     self.get_item(k, j)) + "[" + str(
                    #     k) + "," + str(j) + "] should be " + str(self.get_item(i, j))

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
                    (ij_top_real, ij_bottom_real) = simplify_fraction(int(ij_num), int(ij_denom))

                    if ij_bottom == 0:
                        return ""

                    if (int(ij_top_simplified) != int(ij_top_real)) or \
                            (int(ij_bottom_simplified) != int(ij_bottom_real)):
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

                this_matrix_tuple = list(parse_fraction(self.get_item(i, j)))
                # this_matrix_is_ones = (this_matrix_tuple[0] == this_matrix_tuple[1])

                other_matrix_tuple = list(parse_fraction(o_matrix.get_item(i, j)))
                # other_matrix_is_ones = (other_matrix_tuple[0] == other_matrix_tuple[1])

                # if this_matrix_tuple[0] == this_matrix_tuple[1]

                if this_matrix_tuple[1] != other_matrix_tuple[1]:  # find common denominator
                    a = int(this_matrix_tuple[1])
                    b = int(other_matrix_tuple[1])
                    common_divisor = fractions.gcd(a, b)
                    lcd = ((a * b) / common_divisor)

                    if int(this_matrix_tuple[1]) != lcd:
                        this_matrix_tuple[0] = str(int(this_matrix_tuple[0]) * lcd)
                        this_matrix_tuple[1] = str(lcd)

                    if int(other_matrix_tuple[1]) != lcd:
                        other_matrix_tuple[0] = str(int(other_matrix_tuple[0]) * lcd)
                        other_matrix_tuple[1] = str(lcd)

                    difference = abs((float(this_matrix_tuple[0]) - float(other_matrix_tuple[0])) / lcd)
                else:
                    lcd = int(this_matrix_tuple[1])
                    if int(this_matrix_tuple[1]) != lcd:
                        this_matrix_tuple[0] = str(int(this_matrix_tuple[0]) * lcd)
                        this_matrix_tuple[1] = str(lcd)
                    if int(other_matrix_tuple[1]) != lcd:
                        other_matrix_tuple[0] = str(int(other_matrix_tuple[0]) * lcd)
                        other_matrix_tuple[1] = str(lcd)
                    difference = abs((float(this_matrix_tuple[0]) - float(other_matrix_tuple[0])) / lcd)

                if difference != 0:
                    if abs(difference) > self.greatest_distance_value:
                        self.greatest_distance_value = abs(difference)
                        self.greatest_distance_location = [i, j]
                    total_distance += abs(difference)
                    differences_noted += 1

                    # print "Difference [" + str(i) + "," + str(j) + "]= " + str(abs(difference))
        return total_distance, differences_noted


def parse_fraction(input_str):
    fraction_parts = input_str.split('/')
    if len(fraction_parts) == 2:
        return fraction_parts[0], fraction_parts[1]
    return fraction_parts[0], '1'


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


def generate_consistent_matrix(matrix_size):
    random.seed()
    rounds_required = 0
    while True:
        rounds_required += 1

        l = np.random.randint(pow(matrix_size, 3), size=(matrix_size, matrix_size))
        m = PairwiseMatrix(make_all_ones_matrix(matrix_size))

        #   matrix_elements = m.get_elements_below_diagonal()
        for i in range(0, matrix_size):
            for j in range(0, matrix_size):
                if i == j:
                    continue
                m.set_item(i, j, str(l[i][i]) + '/' + str(l[j][j]))
                m.set_item(j, i, str(l[j][j]) + '/' + str(l[i][i]))
        m.print_matrix()

        (noi, consistent) = m.check_matrix_consistency()

        if noi == 0:
            print "Rounds required: " + str(rounds_required)
            m.print_matrix()
            m.reset_inconsistency_data()
            modify_elements(m, 45)
            return


if __name__ == "__main__":

    for idx in range(10, 11):
        generate_consistent_matrix(idx)

        # 3 == 3 = 0
        # 4 == 6 = 2
        # 5 == 10 = 5
        # 6 == 15  = 9
        # 7 == 21 = 14
        # 8 == 28 = 20
        # 9 == 36 = 27
        # 10 == 45 = 35

    n = 1
    for i in range(2, 11):
        print (str(i) + ":" + str(n))
        n += (i)


        # m.add_matrix_row(['1', '18/31', '18/51', '18/55'])
        # m.add_matrix_row(['31/18', '1', '31/51', '31/55'])
        # m.add_matrix_row(['51/18', '51/31', '1', '51/55'])
        # m.add_matrix_row(['55/18', '55/31', '55/51', '1'])

        # m = PairwiseMatrix()
        # m.add_matrix_row(['1', '18/31', '18/51', '18/55'])
        # m.add_matrix_row(['31/18', '1', '31/51', '31/55'])
        # m.add_matrix_row(['51/18', '51/31', '1', '51/55'])
        # m.add_matrix_row(['55/18', '55/31', '55/51', '1'])
        # m.print_matrix()
        # (noi, consistent) = m.check_matrix_consistency()
        # print "Inconsistencies: " + str(noi)
        # if noi > 0:
        #     if noi != (6 * (m.get_size() - 2)):
        #          print "Unexpected number of inconsistencies (" + str(noi) + "), should have been "\
        #                + str(6 * (m.get_size() - 2))
