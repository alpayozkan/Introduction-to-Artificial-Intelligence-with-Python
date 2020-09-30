import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        remVal = []
        for v in self.crossword.variables:
            for d in self.domains[v]:
                if len(d) != v.length:
                    remVal.append((v, d))
        for tup in remVal:
            v = tup[0]
            d = tup[1]
            self.domains[v].remove(d)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        remVal = []
        intersection = self.crossword.overlaps[x, y]
        if intersection == None: # intersection yoksa arc consistent olurlar zaten restriction koymaz 
            return revised
        (i, j) = intersection

        for v1 in self.domains[x]:
            flag = False
            for v2 in self.domains[y]:
                if v1[i] == v2[j]:
                    flag = True
                    break
            if not flag: # no v2 in y.dom possible for v1 in x.dom
                revised = True
                remVal.append(v1) 

        for v in remVal:
            self.domains[x].remove(v)
                
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []
        if arcs == None:
            for v1 in self.crossword.variables:
                for v2 in self.crossword.variables:
                    if v1 == v2:
                        continue
                    queue.append((v1, v2))

            while queue != []:
                (x, y) = queue.pop(0)
                if self.revise(x, y):
                    if self.domains[x] == set(): # empty : no possible x left in x.dom
                        return False
                    
                    for z in self.crossword.neighbors(x).difference({y}):
                        queue.append((z, x))

        else:
            queue = arcs
            while queue != []:
                (x, y) = queue.pop(0)
                if self.revise(x, y):
                    if self.domains[x] == set(): # empty : no possible x left in x.dom
                        return False

        return True
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables): # if complete condition
            return True
        
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        #1 all values are distinct 
        asgValsList = list(assignment.values())
        asgValsSet = set(asgValsList)
        if len(asgValsList) != len(asgValsSet): # means no duplicate elements
            return False
        #2 every value is correct lenght: since already satisfied by enforce-node-consistency : solve function calls first enforce then backtrack : no need to check againg
        
        #3 no conflict betw nb vars
        for v1 in self.crossword.variables:
            for v2 in self.crossword.variables:
                if v1==v2 or not v1 in assignment or not v2 in assignment:
                    continue
                intersection = self.crossword.overlaps[v1, v2]
                if intersection==None:
                    continue
                (i, j) = intersection
                if assignment[v1][i] != assignment[v2][j]:
                    return False

        return True
                

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        nb = self.crossword.neighbors(var)
        L = [] # store values with corresponding restriction counts
        # assumed arc and node consistency satisfied before this
        for d in self.domains[var]: # for any words in the dom of var
            count = 0
            for v in nb: # for any nb of var
                if v in assignment: # does not put any restriction since it is already determined
                    continue
                if d in self.domains[v]: # also in the dom of a neighbor : put restriction
                    count += 1
            L.append((count, d))
        L = sorted(L, key=lambda tup: tup[0])
        res = [tup[1] for tup in L]
        return res

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        minRem = len(self.crossword.words) 
        uvs = self.crossword.variables.difference(set(assignment.keys()))
        res = set()

        for v in uvs:
            tmp = len(self.domains[v])
            if tmp == minRem:
                res.add(v)
            elif tmp < minRem:
                minRem = tmp
                res = set()
                res.add(v)
        # if only 1 acc to mrv then answer determined
        if len(res) == 1:
            return res.pop()
        # if multiple variables same acc to mrv
        # check max degree
        maxDeg = 0
        degRes = set()
        for v in res:
            tmp = len(self.crossword.neighbors(v))
            if tmp == maxDeg: 
                degRes.add(v)
            elif tmp > maxDeg: 
                maxDeg = tmp
                degRes = set()
                degRes.add(v)
        # if only one element remains returns it or pick randomly in case of multiple elements
        return degRes.pop()

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
            
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
            assignment.pop(var) 
        
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
