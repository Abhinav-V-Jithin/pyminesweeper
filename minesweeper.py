import itertools
import random

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
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def members(self):

        return self.cells

    def mine_count(self):

        return self.count

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)



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

    def nearby_cells(self, cell):
        neighbors = set()
        x = cell[0]
        y = cell[1]
        height = self.height-1
        width  = self.width-1
        i, j = cell[0], cell[1]
        neighbors = set()

        # neighbous above
        if (i-1 >= 0):
            neighbors.add((i-1, j))
            if (j-1 >= 0):
                neighbors.add((i-1, j-1))
            if (j+1 <= self.width-1):
                neighbors.add((i-1, j+1))

        # neighbors either side
        if (j-1 >= 0):
            neighbors.add((i, j-1))
        if (j+1 <= self.width-1):
            neighbors.add((i, j+1))
        
        # neighbors below
        if (i+1 <= self.height-1):
            neighbors.add((i+1, j))
            if (j-1 >= 0):
                neighbors.add((i+1, j-1))
            if (j+1 <= self.width-1):
                neighbors.add((i+1, j+1))
        return neighbors

        
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
        # mark the cell as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        if cell not in self.safes:
            self.safes.add(cell)

        #3.) add a new sentence to the AI's knowledge base

        nearby_cells = self.nearby_cells(cell)
        neighbor_count = count
        unwanted = []
        for neighbor in nearby_cells:
            if neighbor in self.mines:
                unwanted.append(neighbor)
                neighbor_count -= 1

        for u in unwanted:
            nearby_cells.discard(u)

        new_sentence = Sentence(nearby_cells, neighbor_count)

        self.knowledge.append(new_sentence)
        for sentence in self.knowledge:
            if len(sentence.members()) == 0:
                self.knowledge.remove(sentence)

        """
        4) mark any additional cells as safe or as mines
        if it can be concluded based on the AI's knowledge base
        """
        cells =[]
        safe_cells = []
        for sentence in self.knowledge:
            for cell in sentence.known_mines():
                cells.append(cell)
            for cell in sentence.known_safes():
                safe_cells.append(cell)

        for cell in cells:
            self.mark_mine(cell)
        for cell in safe_cells:
            self.mark_safe(cell)
        """
        5)  add any new sentences to the AI's knowledge base
            if they can be inferred from existing knowledge
        """
        counter = 0
        sentences = []

        sentences = set()
        for sentence in self.knowledge:
            for cell in self.moves_made:
                if  cell in sentence.members():
                    sentence.cells -= set({cell})
        
        


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        all_possibles = []
        print(f"mines known: {self.mines}")
        for sentence in self.knowledge:
            if sentence.mine_count() == 0:
                for cell in sentence.members():
                    return cell

        for cell in self.safes:
            if cell in self.moves_made:
                self.safes -= set(cell)
                continue
            if cell in self.mines:
                self.safes -= set(cell)
                continue
            return cell
        print("What should I do?")

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        move = ()
        chances = []
        all_moves = set()
        for row in range(0, self.height):
            for column in range(0, self.width):
                cell = tuple((row, column))
                all_moves.add(cell)
                if set({cell}).issubset(self.moves_made) == False and set({cell}).issubset(self.mines) == False:
                    print(chances)
                    chances.append(cell)
        if chances == []:
            return None
            #for row in range(0, self.height):
            #    for column in range(0, self.width):
            #        cell = tuple((row, column))
            #        if set({cell}).issubset(self.moves_made) == False and set({cell}).issubset(self.mines) == False:
            #            print(cell)
            #            chances.append(cell)

        move = random.choice(chances)
        print(f"mines known: {self.mines}")
        print(f"chosen: {move}")
        return move
