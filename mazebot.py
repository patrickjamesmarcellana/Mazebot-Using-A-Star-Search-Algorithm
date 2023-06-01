# GUI is optional
try:
    from gui import GUI
except:
    pass

import fileinput
import copy
from queue import PriorityQueue

# PrioritizedItem copied from https://docs.python.org/3/library/queue.html#queue.PriorityQueue
from dataclasses import dataclass, field
from typing import Any

@dataclass(order = True)
class PrioritizedItem:
    """ 
    Creates a PrioritizedItem object. It has a priority value and a data
    element that is not comparable.
    """
    priority: int
    item: Any = field(compare = False)

class State:
    """
    Creates a state object.
    """
    def __init__(self, coordinate, goal_coordinate, cost, prev_state):
        """
        Assigns the values of the state.

        Args:
            coordinate ((int, int)): coordinate of the state
            goal_coordinate ((int, int)): coordinate of the goal state
            cost (int): number of moves it took to get to the state
        """
        self.coordinate = coordinate
        self.heuristic = calculate_heuristic(self.coordinate, goal_coordinate)
        self.cost = cost
        self.priority = self.heuristic + self.cost
        self.prev_state = prev_state

gui = None
remap = {
    '.': (255, 255, 255),
    '#': (0, 0, 0),
    'X': (255, 0, 0),
    'E': (0, 255, 0),
    
    'S': (0, 0, 255),
    'G': (255, 0, 255)
}

def display_maze(maze, use_gui=True):
    """
    Displays the maze and the person's position on the screen

    Args:
        maze (str[][]): maze loaded into the program
        use_gui (bool): display the maze on the GUI, defaults to True
    """

    if use_gui and gui is not None:
        gui.next_frame()
        for row in range(len(maze)):
            for col in range(len(maze[0])):
                gui.set_tile_color((col, row), remap[maze[row][col]] )
        
        # call this to redraw window
        gui.update_window()

    print("")
    for row in maze:
        output = ""
        for col in row:
            output += col + " "    
        print(output)
    
    print("")
    print("=" * 147)

def find_point(point, maze, n):
    """
    Finds a specific point in the maze. This function is used to get the row
    and column number of the starting (S) and ending point (G) of the maze.

    Args:
        point (str): the point to find
        maze (str[][]): the maze loaded in the program
        n (int): the number of rows/columns

    Returns:
        int: row number of the point
        int: column number of the point
    """
    for row in range(n):
        for col in range(n):
            if maze[row][col] == point:
                return (row, col)
    
    return (-1, -1) # if not found

def calculate_heuristic(coord1, coord2):
    """ 
    Calculates the heuristic of a state using the Manhattan Distance:
    | x2 - x1 | + | y2 - y1 |

    Args:
        coord1 ((int, int)): coordinate of the current state
        coord2 ((int, int)): coordinate of the goal state

    Returns:
        int: the state's calculated heuristic
    """
    return abs(coord2[0] - coord1[0]) + abs(coord2[1] - coord1[1])

def get_possible_moves(current_state, maze, n):
    """
    Gets the possible actions from a state.

    Args:
        current_state (State): state that contains current position in the maze
        maze (str[][]): the maze loaded in the program
        n (int): the number of rows/columns

    Returns:
        [(int, int)]: return the list of all the possible coordinates
    """
    possible_moves = []
        
    first, second = current_state.coordinate[0] - 1, current_state.coordinate[0] + 1
    third, fourth = current_state.coordinate[1] - 1, current_state.coordinate[1] + 1

    if first > -1 and maze[first][current_state.coordinate[1]] != '#': 
        possible_moves.append((first, current_state.coordinate[1]))
    
    if second < n and maze[second][current_state.coordinate[1]] != '#': 
        possible_moves.append((second, current_state.coordinate[1]))

    if third > -1 and maze[current_state.coordinate[0]][third] != '#':
        possible_moves.append((current_state.coordinate[0], third))
    
    if fourth < n and maze[current_state.coordinate[0]][fourth] != '#':
        possible_moves.append((current_state.coordinate[0], fourth))
    
    return possible_moves

def scan_file():
    """
    Scans the input file.

    Returns:
        int: number of rows/columns (n)
        str[][]: maze loaded in the program
    """
    n = 0
    maze = []
    # place whole file address
    for line in fileinput.input(files = "maze.txt"):
        if fileinput.isfirstline():
            n = int(line.rstrip()) # get number of rows/columns
        else: 
            row = []
            for block in line.rstrip():
                row.append(block)
            maze.append(row)
    
    return n, maze

def display_final_path(state, maze_copy, use_gui=True):
    """
    Displays the final path that the bot took to the goal state.

    Args:
        state (State): present state of the bot as it backtracks
        maze_copy (str[][]): copy of the maze loaded in the program
        use_gui (bool): display the maze on the GUI, defaults to True
    """
    while state != None:
        maze_copy[state.coordinate[0]][state.coordinate[1]] = 'X'
        state = state.prev_state
    
    display_maze(maze_copy, use_gui)

def display_explored_locations(explored, maze_copy, use_gui=True):
    """
    Displays all the explored locations in the maze using the A* algorithm.

    Args:
        explored ([(int, int)]): list of explored coordinates
        maze_copy (str[][]): copy of the maze loaded in the program
        use_gui (bool): display the maze on the GUI, defaults to True
    """
    for i in explored:
        maze_copy[i[0]][i[1]] = 'E'
    
    display_maze(maze_copy, gui)

def display_final_stats(explored, explored_count, final_state, maze_copy, found):
    """
    Displays the final stats or information required after the algorithm finishes.

    Args:
        explored ([(int, int)]): list of explored coordinates
        explored_count (int): total number of explored states
        final_state (State): the final state of the bot before it ends the algorithm
        maze_copy (str[][]): copy of the maze loaded in the program
        found (bool): indicates if the bot found the optimal path (if it exists)
    """
    print("a) Final Path Taken by the Bot (Path = X):")
    if found:  
        display_final_path(final_state, maze_copy, use_gui=False)
    else:
        print("A solution cannot be found.")
        print()

    print("b) All the  locations  that  were  explored:")
    display_explored_locations(explored, maze_copy)
        
    print("c) Total Number of Explored States:", explored_count)
    if not found:
        print("A solution cannot be found.")

def run_algorithm(initial_state, end_coord, maze, n, explored, frontier):
    """
    Runs the A* Algorithm 

    Args:
        initial_state (State): initial state of the maze puzzle
        end_coord ((int, int)): coordinate of the goal state in the maze
        maze (str[][]): the maze loaded in the program
        n (int): number of rows/columns
        explored ([(int, int)]): list of explored coordinates
        frontier ([(int, int, State)]): priority queue that keeps track of the discovered states

    Returns:
        int, State, bool: returns the final count of explored states, the final state, and 
                          True if the optimal path was found; False if not
    """
    # start algorithm
    best_prio_in_frontier = {}

    explored.add(initial_state.coordinate)
    best_prio_in_frontier[initial_state.coordinate] = 0 + calculate_heuristic(initial_state.coordinate, end_coord)
    explored_count = 1
    current_state = initial_state
    # maze[initial_state.coordinate[0]][initial_state.coordinate[1]] = str(explored_count)
    # display_maze(maze)
    display_final_path(current_state, copy.deepcopy(maze))
    
    while(current_state.coordinate != end_coord):
        # get possible moves from current state and place them in the frontier list
        possible_coords = get_possible_moves(current_state, maze, n)
        for position in possible_coords:
            if not(position in explored):
                # do not put priorities that are higher than the current one for the state
                new_state = State(position, end_coord, current_state.cost + 1, current_state)
                if position not in best_prio_in_frontier or new_state.priority < best_prio_in_frontier[position]:
                    frontier.put(PrioritizedItem(new_state.priority, new_state))
                    best_prio_in_frontier[position] = new_state.priority

        # stop the program if there are no more possible states to explore
        if frontier.empty():
            break

        # get next state to be transferred to explored
        frontier_select = frontier.get()
        current_state = frontier_select.item
        while current_state.coordinate in explored and not frontier.empty():
            frontier_select = frontier.get()
            current_state = frontier_select.item

        # add the explored state / coordinate and increment count of explored states
        if current_state.coordinate not in explored:
            explored.add(current_state.coordinate)
            explored_count += 1

            # change display to the order
            # maze[current_state.coordinate[0]][current_state.coordinate[1]] = str(explored_count)
            display_final_path(current_state, copy.deepcopy(maze)) 

            # set explored count
            if gui is not None:
                gui.set_explored_count(explored_count)

    if current_state.coordinate == end_coord:
        return explored_count, current_state, True
    else:
        return explored_count, current_state, False

def main():
    """
    Starts the program.
    """
    # scan the input file and store the number of rows/columns and the maze
    n, maze = scan_file()
    maze_copy = copy.deepcopy(maze)

    # get start and end's rows and columns
    start_coord = find_point('S', maze, n)
    end_coord = find_point('G', maze, n)

    # important lists
    explored = set()
    frontier = PriorityQueue()

    # create GUI
    global gui
    gui = GUI(640, 480, n)

    # start A* algorithm
    display_maze(maze)
    initial_state = State(start_coord, end_coord, 0, None)
    explored_count, final_state, found = run_algorithm(initial_state, end_coord, maze, n, explored, frontier)

    # display final stats
    display_final_stats(explored, explored_count, final_state, maze_copy, found)
    
    # keep the GUI running
    gui.keep_running()

main()