import numpy as np
import random
from typing import List
import pickle as pkl

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
        
        for tail in possible_tails:
            if tail not in idxs and tail[0]>0 and tail[1]>0:
                break
        
        body = np.vstack([head, tail])
        
        self.snake = Snake(body, self)
        self.snake.draw_snake()
        
    def vectorize(self):
        return self.table.ravel()
    
    def save(self, path):
        with open(path, "wb") as fout:
            pkl.dump(self, fout)
    
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
            print("You lost")
        elif new_state == +1:
            print("Eaten")
            self.body = np.vstack([new_head, self.body])
            
            self.table.add_food()
        else:
            self.body = np.vstack([new_head, self.body[:-1]])
        
        
        self.update_snake()
        
        if return_state:
            return new_state
        
    def check_state(self, head):
        table_shape = self.table.table.shape
        if (head[0] < 0) or (head[0] == table_shape[0]) or (head[1] < 0) or (head[1] == table_shape[0]):
            return -1 # Lost game
        
        food = np.argwhere(self.table.table == 2)[0]
        if (head == food).all():
            return +1 # Food eaten
        
        else:
            return 0
        
    def draw_snake(self):
        for x, y in self.body:
            self.table.table[x, y] = 1
            
    def update_snake(self):
        self.table.table[self.table.table == 1] = 0
        self.draw_snake()