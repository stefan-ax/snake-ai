import numpy as np
import random
from typing import List
import pickle as pkl
import os

VIRTUAL_HEIGHT = int(os.environ["VIRTUAL_HEIGHT"])
VIRTUAL_WIDTH = int(os.environ["VIRTUAL_WIDTH"])
MOVE_CODE = {0:"right", 1:"left", 2:"up", 3:"down"}

def numpy_in_columns(a, b):
    """
    Checks whether a is in the columns of b.
    """
    for row in b:
        if (row==a).all():
            return True
        
    return False
        
class Table:
    def __init__(self):
        self.table = self.generate_table()
        self.food = None
        self.snake = None
    
    @staticmethod
    def generate_table():
        return np.zeros((VIRTUAL_HEIGHT, VIRTUAL_WIDTH))
    
    def __repr__(self):
        return self.table.__repr__()

    def add_food(self):
        idxs = np.argwhere(self.table == 0)
        idx = random.choices(idxs, k=1)[0]
        self.food = Food(idx, self)
        self.food.draw()
        
    def add_snake(self):
        idxs = np.argwhere(self.table == 0)
        head = random.choices(idxs, k=1)[0]
        
        possible_tails = [
                         [head[0]-1, head[1]],
                         [head[0]+1, head[1]],
                         [head[0], head[1]+1],
                         [head[0], head[1]-1]
                        ]
        random.shuffle(possible_tails)
        
        for tail in possible_tails:
            if numpy_in_columns(tail, idxs) and tail[0]>0 and tail[1]>0:
                break
        
        body = np.vstack([head, tail])
        
        self.snake = Snake(body, self)
        self.snake.draw_snake()
        
    def vectorize(self):
        return self.table.ravel()
    
    def save(self, path):
        with open(path, "wb") as fout:
            pkl.dump(self, fout)
            
    def move_quality(self):
        """
        Return the quality of the moves as an probabilities array [_, _, _, _]
        representing the directions. The higher the number, the better the direction.
        """
        result = np.zeros((4,))
        values = []
        
        for idx, move in MOVE_CODE.items():
            value = self.snake.check_move(move)
            
            if value == 1:
                result[idx] = 1
                return result
            
            values.append(value)
        
        values = np.array(values)
        
        # Convert to probability vector
        result[values==0] = 1 / np.sum(values == 0)
        
        return result

class Food:
    def __init__(self, body: np.ndarray, table: Table):
        self.body = body
        self.table = table
    
    def draw(self):
        x, y = self.body[0], self.body[1]
        self.table.table[x, y] = 2

class Snake:
    def __init__(self, body: np.ndarray, table: Table):
        self.body = body
        self.table = table
        
    def __repr__(self):
        return f"{self.body}"
    
    def move(self, direction: str, return_state: bool = False):    
        head = self.body[0]
        
        if direction == "right":
            new_head = [head[0], head[1] + 1]
        elif direction == "left":
            new_head = [head[0], head[1] - 1]
        elif direction == "up":
            new_head = [head[0] - 1, head[1]]
        elif direction == "down":
            new_head = [head[0] + 1, head[1]]
        
        new_head = np.array(new_head)

        new_state = self.check_state(new_head)
        
        if new_state == -1:
            pass
#             print("You lost")
        elif new_state == +1:
#             print("Eaten")
            self.body = np.vstack([new_head, self.body])
            
            self.table.add_food()
        else:
            self.body = np.vstack([new_head, self.body[:-1]])
        
        
        self.update_snake()
        
        if return_state:
            return new_state
        
    def check_state(self, head):
        table_shape = self.table.table.shape
        
        # If out the table
        if (head[0] < 0) or (head[0] == table_shape[0]) or (head[1] < 0) or (head[1] == table_shape[0]) or numpy_in_columns(head, self.body):
            return -1 # Lost game
        
        food = np.argwhere(self.table.table == 2)[0]
        if (head == food).all():
            return +1 # Food eaten
        
        else:
            return 0
        
    def check_move(self, direction):
        head = self.body[0]
        
        if direction == "right":
            new_head = [head[0], head[1] + 1]
        elif direction == "left":
            new_head = [head[0], head[1] - 1]
        elif direction == "up":
            new_head = [head[0] - 1, head[1]]
        elif direction == "down":
            new_head = [head[0] + 1, head[1]]
            
        table_shape = self.table.table.shape
        
        # If out the table
        if (new_head[0] < 0) or (new_head[0] == table_shape[0]) or (new_head[1] < 0) or (new_head[1] == table_shape[0]) or numpy_in_columns(new_head, self.body):
            return -1 # Lost game
        
        food = np.argwhere(self.table.table == 2)[0]
        if (new_head == food).all():
            return +1 # Food eaten
        
        else:
            return 0
        
    def draw_snake(self):
        # Head
        self.table.table[self.body[0][0], self.body[0][1]] = 3
        
        # Rest of the body
        for x, y in self.body[1:]:
            self.table.table[x, y] = 1
            
    def update_snake(self):
        self.table.table[self.table.table == 1] = 0
        self.draw_snake()