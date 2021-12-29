import math, random


class MCTSNode:
    def __init__(self, state = None, parent = None):
        # print(state.current_player)
        self.state = state
        # print(self.state)
        self.visits = 0
        self.score = 0.0
        self.children = {} # dict of actions to successor nodes
        self.parent = parent
        self.is_terminal = state.is_terminal()
        self.is_fully_expanded = self.is_terminal

def random_action(state):

    """
    Plays a game using random actions until a terminal state is reached.
    Returns score of that game. 
    """
    # print(state)
    while not state.is_terminal():
        valid = state.get_valid_actions()
        if not valid:
            raise Exception("Non-terminal state has no valid actions: " + str(state))
        else:
            action = random.choice(valid)
            # print(action)
            state = state.act(action)
    # print("Final:" + str(state))
    return state.get_score()

class MCTS:
    def __init__(self, sims = 1000, exploration_k = math.sqrt(2), rollout = random_action):
        self.sims = sims
        self.k = exploration_k
        self.rollout = rollout
        self.root = None

    def search(self, state, verbose = False):

        """
        Runs [self.sims] simulations and returns action of child node with most visits.
        If verbose is true, displays summary statistics for all child nodes. 
        """

        # print(state.position)
        self.root = MCTSNode(state)
        # print(state.position)
        for i in range(self.sims):
            self.simulate()

        max_visits, result = 0, []
        summary = ""

        for action, child in self.root.children.items():
            if child.visits > max_visits:
                max_visits = child.visits
                result = [action]
            elif child.visits == max_visits:
                result.append(action)

            if verbose:
                summary += f'{action}: {child.visits: 4} visits, avg score {child.score / child.visits: .3f}\n'

        if result:
            next_move = random.choice(result)
            print("Next move: " + str(next_move) + "\n")
            if verbose:
                print(summary)
        else:
            print("No child nodes: no trials, or root state is terminal.")

    def simulate(self):

        """
        Simulates one game.
        """

        # (1) Pick a child node from which to start simulation
        child = self.select(self.root)

        # (2) From that node, play a game to completion
        score = self.rollout(child.state)

        # (3) Update all parent nodes with that game's outcome
        self.backpropagate(child, score)

    def select(self, node):

        """
        Returns a node from which to start the next simulation.

        In order of preference:

        (1) Explore a yet unexplored node (expand())
        (2) Choose among nodes using UCT formula (get_best_child())
        """

        while not node.is_terminal:
            if not node.is_fully_expanded:
                return self.expand(node)
            else:    
                node = self.get_best_child(node)
        return node

    def expand(self, node):

        """
        Creates a new child node corresponding to a yet unexplored action. 
        """
       #  print("Initial" + str(node.state))
        valid = node.state.get_valid_actions()
        for a in valid:
            if a not in node.children:
                # print("Expand:" + str(node.state.act(a)))
                child = MCTSNode(node.state.act(a), node)
                node.children[a] = child
                if len(node.children) == len(valid):
                    node.is_fully_expanded = True
                return child

        raise Exception("Attempted to expand a fully expanded node.")

    def get_best_child(self, node):

        """
        Implements UCT exploration-exploitation trade-off function.
        """

        max_uct, best = float('-inf'), []
        for child in node.children.values():
            uct = node.state.get_current_player() * child.score / child.visits + self.k * math.sqrt(math.log(node.visits) / child.visits)
            if uct > max_uct:
                max_uct, best = uct, [child]
            elif uct == max_uct:
                best.append(child)

        return random.choice(best)

    def backpropagate(self, node, score):

        """
        Updates all parent nodes with the results of the simulation. 
        """

        while node:
            node.visits += 1
            node.score += score
            node = node.parent

    def move_root(self, action):
        pass
