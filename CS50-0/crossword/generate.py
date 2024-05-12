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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for var, words in self.domains.items():
            self.domains[var] = {word for word in words if len(word) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        modified = False
        if self.crossword.overlaps[x, y]:
            xLetter, yLetter = self.crossword.overlaps[x, y]
            wordsToRemove = {word for word in self.domains[x] if all(
                word[xLetter] != yWord[yLetter] for yWord in self.domains[y] if yWord != word)}
            if wordsToRemove:
                self.domains[x] -= wordsToRemove
                modified = True
        return modified

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Initialize the queue of arcs
        if arcs is None:
            arcs = set(self.crossword.overlaps.keys())
        queue = list(arcs)
        
        # Process each item in the queue
        while queue:
            v1, v2 = queue.pop(0)

            # Revise the domains of v1 and v2
            if self.revise(v1, v2):
                if not self.domains[v1]:
                    return False
                
                # Add additional arcs for neighbors of v1 (just not v2)
                for z in self.crossword.neighbors(v1) - {v2}:
                    queue.append((z, v1))
        return True
            
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        complete = True
        for var in self.crossword.variables:
            if var not in assignment:
                complete = False
        return complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check the length of words
        for var, word in assignment.items():
            if len(word) != var.length:
                return False
        
        # Make sure all words are unique
        allValues = list(assignment.values())
        uniqueValues = set(allValues)
        if len(allValues) != len(uniqueValues):
            return False

        # Check that overlapping cells have the same letter
        for var, word1 in assignment.items():
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment.keys():
                    word2 = assignment[neighbor]
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word1[i] != word2[j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        # Setup some variables that will be used for the search and ordering
        wordCount = {}
        words1 = self.domains[var]
        neighbors = self.crossword.neighbors(var)

        # For each word available (for the passed variable), calculate the number of adjoining possibilities it would eliminate
        for word1 in words1:
            num = 0
            for neighbor in neighbors:
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps.get((var, neighbor))
                    if overlap is not None:

                        # We have potential words that would be eliminated, calculate
                        i, j = overlap
                        num += sum(word1[i] != word2[j] for word2 in self.domains[neighbor])
            wordCount[word1] = num
        
        # Return the sorted list (ascending) of 'least constraining words'
        return sorted(wordCount, key=wordCount.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Build a dictionary of options, calculating domain size and degree for each
        possibilities = {}
        for var in self.crossword.variables:
            if var not in assignment:
                domainSize = len(self.order_domain_values(var, assignment))
                degree = len(self.crossword.neighbors(var))
                possibilities[var] = (domainSize, -degree)

        # Sort the options by first domain size, and then by degree... return first value
        sortedValues = sorted(possibilities.keys(), key=lambda k: possibilities[k])
        return sortedValues.pop(0) if sortedValues else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        # Check and see if we are done... all variables are assigned
        if len(assignment) == len(self.crossword.variables):
            return assignment
        
        # Recrusively try all possible assignments for each unassigned variable
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                
                # Backtrack and try again
                del assignment[var]
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
