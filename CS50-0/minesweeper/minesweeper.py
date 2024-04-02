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
        cells - a set of tuples (i,j) that make up the sentence
        count - the number of elements in the sentence that are mines
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
        return copy.deepcopy(self.cells) if self.count == len(self.cells) else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return copy.deepcopy(self.cells) if self.count == 0 else set()

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

        # Create a set of all possible spaces
        self.fullBoard = set()
        for i in range(height):
            for j in range(width):
                self.fullBoard.add((i, j))

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

    def neighbors(self, cell):
        
        # Loop over all cells within one row and column
        neighbors = []

        # Define the range of neighboring cells
        min_row = max(0, cell[0] - 1)
        max_row = min(self.height - 1, cell[0] + 1)
        min_col = max(0, cell[1] - 1)
        max_col = min(self.width - 1, cell[1] + 1)

        # Iterate over neighboring cells
        for i in range(min_row, max_row + 1):
            for j in range(min_col, max_col + 1):
                # Skip the cell itself
                if (i, j) == cell:
                    continue

                # Add valid neighboring cells to the list
                if (i, j) not in self.moves_made:
                    neighbors.append((i, j))

        return neighbors

    def removeKnowns(self):
        # Mark any additional cells as safe or as mines if it can be concluded based on the knowledge base
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            if mines:
                for mine in mines:
                    self.mark_mine(mine)
            safes = sentence.known_safes()
            if safes:
                for safe in safes:
                    self.mark_safe(safe)
            if not sentence.cells:
                self.knowledge.remove(sentence)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """

        # Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Mark the cell as safe
        self.mark_safe(cell)

        # Add a new sentence to the knowledge base based on the value of cell and count
        tempSentence = Sentence(self.neighbors(cell), count)
        if not tempSentence.cells:
            return
        
        # Remove any known mines or safes from the sentence before adding to the knowledge base
        for mine in self.mines:
            tempSentence.mark_mine(mine)
        for safe in self.safes:
            tempSentence.mark_safe(safe)        
        if tempSentence.cells:
            self.knowledge.append(tempSentence)

        # We may have made changes to the knowledge base, scan and remove any new knowns
        self.removeKnowns()

        # Add any new sentences to the knowledge base if they can be inferred from the existing knowledge
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                    cells3 = sentence2.cells - sentence1.cells
                    count3 = sentence2.count - sentence1.count
                    if count3 == 0:                       # The subset is all safe, so remove sentence as it is a duplicate
                        self.safes.update(cells3)
                        self.knowledge.remove(sentence2)
                    else:                                 # The subset is not all safe, create a new sentence and simplify others
                        sentence3 = Sentence(cells3, count3)
                        self.knowledge.append(sentence3)
                        self.knowledge.remove(sentence2)
                # Now let's see if we have a common set and know they are all mines
                if sentence1 != sentence2:
                    cells3 = sentence1.cells & sentence2.cells
                    if len(cells3) == sentence1.count and len(cells3) == sentence2.count:
                        for cell in cells3:
                            self.mark_mine(cell)

        # We may have made changes to the knowledge base, scan and remove any new knowns
        self.removeKnowns()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Get the available safe moves
        options = self.safes - self.moves_made

        # If there are available safe moves, return one of them
        return options.pop() if options else None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        # Get the available unknown moves
        options = self.fullBoard - self.moves_made - self.mines

        # If there are available unknown moves, return one of them
        return options.pop() if options else None
