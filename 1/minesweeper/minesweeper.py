import itertools
import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count==len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        def neighbors(cell): # returns physical neighbors in a restricted board max of 8 possible neighbors except for edge cells
            tmp = {(cell[0]-1, cell[1]-1), (cell[0]-1, cell[1]), (cell[0]-1, cell[1]+1), (cell[0], cell[1]+1), (cell[0]+1, cell[1]+1), (cell[0]+1, cell[1]), (cell[0]+1, cell[1]-1), (cell[0], cell[1]-1)}
            res = set()
            for tmp_cell in tmp:
                i = tmp_cell[0]
                j = tmp_cell[1]

                if 0 <= i < self.height and 0 <= j < self.width:
                    res.add(tmp_cell)

            return res 
        
        tmp = neighbors(cell)
        # copy of the knowledge 
        # avoid : RuntimeError: Set changed size during iteration
        tmpCopy = copy.deepcopy(tmp)

        for tmp_cell in tmpCopy:
            if tmp_cell in self.mines:
                tmp.remove(tmp_cell)
                count -= 1
            elif tmp_cell in self.safes:
                tmp.remove(tmp_cell)

        # check if newSentence is necessary: either empty sentence or already in the knowledge base
        nwSentence = Sentence(tmp, count)
        if not(tmp==set() and count==0) and not nwSentence in self.knowledge:
            self.knowledge.append(nwSentence)

        #update knowledge base
        #untill saturation
        flag = True # keep checking untill becomes false when it is saturated
        while flag:
            flag = False
            # avoid : RuntimeError: Set changed size during iteration
            
            #initial buffers
            mineSetList = []
            safeSetList = []
            for sentence in self.knowledge:
                anyMines = sentence.known_mines()
                anySafes = sentence.known_safes()
                if anyMines != set():
                    flag = True #change & update
                    mineSetList.append(anyMines) #fill buffer
                elif anySafes != set():
                    flag = True #change & update
                    safeSetList.append(anySafes) #fill buffer
            #flush buffer
            for mineSet in mineSetList:
                minesetCopy = copy.deepcopy(mineSet)
                for mine in minesetCopy:
                    self.mark_mine(mine)    
            for safeSet in safeSetList:
                safesetCopy = copy.deepcopy(safeSet)
                for safe in safesetCopy:
                    self.mark_safe(safe)
            
            # simplify knowledge : remove empty
            sentRmv = [] # buffer for empty sentences
            for sentence in self.knowledge:
                if sentence.cells == set() and sentence.count == 0:
                    sentRmv.append(sentence) # record empty sentences
            # remove empty sentences
            for sentence in sentRmv:
                if sentence in self.knowledge:
                    self.knowledge.remove(sentence)

            sentRmv = []
            sentAdd = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2:
                        if sentence1.cells.issubset(sentence2.cells):
                            flag = True #change & update
                            diffCells = sentence2.cells.difference(sentence1.cells)
                            diffCount = sentence2.count - sentence1.count
                            # keep sets not a subset of each other, linear algebra, avoid infinite loops
                            sentRmv.append(sentence2)
                            # add newSentence
                            nwSentence = Sentence(diffCells, diffCount)
                            sentAdd.append(nwSentence)
            # remove sentences/avoid unnecessary info/keep linearly independent                
            for sentence in sentRmv:
                if sentence in self.knowledge:
                    self.knowledge.remove(sentence)
            # add sentences/new inferences
            for sentence in sentAdd:
                # check if newSentence is necessary: either empty sentence or already in the knowledge base or already removed
                if not (sentence.cells == set() and sentence.count == 0) and not sentence in self.knowledge and not sentence in sentRmv:
                    self.knowledge.append(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        #if no possible moves exist: safes=movesmade => all safe moves are already played, no additional safe moves are left
        if len(self.safes)==len(self.moves_made):
            return None
        #if there exist safe moves not made
        for move in self.safes:
            if not move in self.moves_made:
                return move
        # theoretically never called but just for the good measure
        return None 
        
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        bag = []

        for i in range(0, self.height):
            for j in range(0, self.width):
                move = (i, j)
                if not move in self.moves_made and not move in self.mines:
                    bag.append(move)
        if bag == []:            
        # if move not possible: either no moves are left that might be a safe cell
            return None
        else:
            random.seed()
            index = random.randint(0, len(bag))
            return bag[index]
