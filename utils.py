import random
import numpy as np
import os
import copy

# Variables
VIRTUAL_HEIGHT = int(os.environ["VIRTUAL_HEIGHT"])
VIRTUAL_WIDTH = int(os.environ["VIRTUAL_WIDTH"])
DIM = VIRTUAL_WIDTH * VIRTUAL_HEIGHT
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 64))
MOVE_CODE = {0:"right", 1:"left", 2:"up", 3:"down"}
EPOCHS = int(os.getenv("EPOCHS", 64))
STEPS_PER_EPOCH = int(os.getenv("STEPS_PER_EPOCH", 100))

class TrainFeeder:
    def __init__(self, init_games, n=BATCH_SIZE):
#         assert len(init_games) >= n
        self.init_games = init_games
        self.games = random.choices(self.init_games, k=n)
    
    @property
    def feed(self):
        while True:
            vectors = [game.table.ravel().reshape(1, -1) for game in self.games]
            for idx, vector in enumerate(vectors):
                yield vector, self.games[idx].move_quality().reshape(1, -1), np.array(idx)
    
    def apply_moves(self, directions: list):
        results = []
        for idx, direction in enumerate(directions):
            result = self.games[idx].snake.move(direction, return_state=True)
            results.append(result)
            
            if result == -1:
                # Reset the game
                self.games[idx] = copy.deepcopy(random.choice(self.init_games))
            
        return np.array(results)
    
    def apply_move(self, direction, idx):
        result = self.games[idx].snake.move(direction, return_state=True)
        
        if (self.games[idx].move_quality() == 0).all() or self.games[idx].snake.is_dead:
#             print(f"Lost in this situation: \t {self.games[idx]}")
#             print(f"Had age: {self.games[idx].snake.age}")
            # Reset the game
            self.games[idx] = copy.deepcopy(random.choice(self.init_games))
        
        return result
    
    def length_mean(self):
        # Sum the body + head of the snake. Body is annotated with 1 and head with 3
        length = [np.sum(game.table[game.table==1])+1 for game in self.games]
        return np.mean(length)
    
    def age_mean(self):
        # Sum the body + head of the snake. Body is annotated with 1 and head with 3
        ages = [game.snake.age for game in self.games]
        return np.mean(ages)