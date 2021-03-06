from state import State
from mcts import MCTS
from copy import copy

def print_array(A):
    for e in A:
        print(e)
    print()

class ConnectFourState(State):

    HEIGHT = 6
    WIDTH = 7
    SYMBOLS = {1: 'x', -1: 'o'}

    def __init__(self, A, current_player = 1):
        self.current_player = current_player
        self.mask, self.position = self.array_to_bit(A)

    """

    Represents a Connect 4 board with bits. 
    See https://blog.gamesolver.org/solving-connect-four/06-bitboard/

    Each column is represented by height + 1 bits. 
    So a 7 x 6 board would be represented by 49 bits, as so:

    .  .  .  .  .  .  .
    5 12 19 26 33 40 47
    4 11 18 25 32 39 46
    3 10 17 24 31 38 45
    2  9 16 23 30 37 44
    1  8 15 22 29 36 43
    0  7 14 21 28 35 42 

    Game state is stored as
    - a bitboard "mask" with 1 where a stone is present
    - a bitboard "position" with 1 on stones of current player

    """

    def array_to_bit(self, A):

        """
        Takes array of strings corresponding to rows, e.g.,

        [".......",
         ".......",
         "...x...",
         "...o...",
         "...x...",
         ".oxo..."]

         and transforms into a mask, position pair.
         """

        if len(A) != self.HEIGHT or len(A[0]) != self.WIDTH:
            raise Exception("Improper board shape.")

        mask, position = 0, 0

        for c in reversed(range(self.WIDTH)):
            for r in range(-1, self.HEIGHT):
                mask <<= 1
                position <<= 1
                if r == -1:
                    pass # leave a blank space
                elif A[r][c] != ".":
                    mask += 1
                    if A[r][c] == self.SYMBOLS[self.current_player]:
                        position += 1

        return (mask, position)

    def bit_to_array(self):

        """
        Returns array corresponding to self.mask and self.position
        """

        result = [""] * self.HEIGHT
        m, p = self.mask, self.position
        for c in range(self.WIDTH):
            for r in reversed(range(-1, self.HEIGHT)):
                if r == -1:
                    pass # ignore the blank space
                elif m & 1:
                    if p & 1:
                        result[r] += self.SYMBOLS[self.current_player]
                    else:
                        result[r] += self.SYMBOLS[-1 * self.current_player]
                else:
                    result[r] += '.'
                m >>= 1
                p >>= 1
        return result

    def __str__(self):
        result = ""
        for x in self.bit_to_array():
            result += x + "\n"
        return result
    
    def is_valid_action(self, col):
        return not (self.mask & (1 << ((self.HEIGHT + 1) * (col + 1) - 2)))

    def get_valid_actions(self):
        return [c for c in range(self.WIDTH) if self.is_valid_action(c)]

    def act(self, col):
        if not self.is_valid_action(col):
            raise Exception("Attempted invalid action: " + str(col))
        new = copy(self)
        new.position ^= new.mask
        new.current_player *= -1
        new.mask |= new.mask + (1 << (new.HEIGHT + 1) * col)
        return new

    full_board, full_col = 0, 2 ** (HEIGHT) - 1
    for _ in range(WIDTH):
        full_board = (full_board << (HEIGHT + 1)) + full_col

    def is_terminal(self):
        return self.mask == self.full_board or self.get_score() != 0

    def get_score(self):
        # We want to know if the player who just moved won. 
        # This will be the inactive player, so we temporarily look at that player's pieces.
        self.position ^= self.mask

        # horizontal 
        shift = self.position & (self.position >> (self.HEIGHT + 1))
        if shift & (shift >> (2 * (self.HEIGHT + 1))):
            self.position ^= self.mask # Undo the change to get ready for next turn.
            return -1 * self.get_current_player() # Again, winner is the inactive player. 

        # vertical
        shift = self.position & (self.position >> 1)
        if shift & (shift >> 2):
            self.position ^= self.mask 
            return -1 * self.get_current_player()

        # diagonal \
        shift = self.position & (self.position >> self.HEIGHT)
        if shift & (shift >> (2 * self.HEIGHT)):
            self.position ^= self.mask 
            return -1 * self.get_current_player() 

        # diagonal /
        shift = self.position & (self.position >> (self.HEIGHT + 2))
        if shift & (shift >> (2 * (self.HEIGHT + 2 ))):
            self.position ^= self.mask 
            return -1 * self.get_current_player()

        self.position ^= self.mask
        return 0

    def get_current_player(self):
        return self.current_player

if __name__=="__main__":

    A = [".......",
         ".......",
         ".......",
         ".......",
         ".......",
         "......."]

    initial_state = ConnectFourState(A, 1)
    searcher = MCTS(sims = 10000)
    searcher.search(initial_state, verbose = True)