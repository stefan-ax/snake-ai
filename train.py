# Imports

import tensorflow as tf
import keras
import keras.backend as K
from keras.layers import Dense, Dropout, Input
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
from glob import glob
from objects import Table, Food, Snake
import pickle as pkl
import os
import random
import numpy as np

import logging
logging.basicConfig(level=logging.INFO)


# Variables
VIRTUAL_HEIGHT = int(os.environ["VIRTUAL_HEIGHT"])
VIRTUAL_WIDTH = int(os.environ["VIRTUAL_WIDTH"])
DIM = VIRTUAL_WIDTH * VIRTUAL_HEIGHT
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 64))
MOVE_CODE = {0:"right", 1:"left", 2:"up", 3:"down"}
EPOCHS = int(os.getenv("EPOCHS", 64))
STEPS_PER_EPOCH = int(os.getenv("STEPS_PER_EPOCH", 100))


# Load data
def load_dataset(folder_path=f"dataset_{VIRTUAL_HEIGHT}x{VIRTUAL_WIDTH}", maximum=None):
    paths = glob(folder_path + "/*")

    games = []
    for path in paths[:maximum if maximum else len(paths)]:
        with open(path, "rb") as fin:
            table = pkl.load(fin)
            games.append(table)
            
    return games

init_games = load_dataset(maximum=None)
logging.info(f"Loaded {len(init_games)} games")


# Train Feeder
class TrainFeeder:
    def __init__(self, init_games, n=BATCH_SIZE):
        # assert len(init_games) >= n
        self.init_games = init_games
        self.games = random.choices(self.init_games, k=n)
    
    @property
    def feed(self):
        i=-1
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
                self.games[idx] = random.choice(self.init_games)
            
        return np.array(results)
    
    def apply_move(self, direction, idx):
        result = self.games[idx].snake.move(direction, return_state=True)
        
        if result == -1:
            # Reset the game
            self.games[idx] = random.choice(self.init_games)
            
        return result
        
    def length_mean(self):
        length = [np.sum(game.table[game.table==1]) for game in self.games]
        return np.mean(length)
    
feeder = TrainFeeder(init_games=init_games)

class LoggingCallback(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"\nCurrent length mean: {feeder.length_mean()}")


# Start Training
logging.info("Starting training.")
from model import snakemodel
snakemodel.feeder = feeder
snakemodel.compile(optimizer="adam", run_eagerly=True)
history = snakemodel.fit(x=feeder.feed,
    epochs=EPOCHS,
    verbose=1,
    callbacks=[ModelCheckpoint("models/epoch_{epoch}.h5", verbose=False), LoggingCallback()],
    steps_per_epoch=STEPS_PER_EPOCH,
)

with open("models/history.pkl", "wb") as fout:
    pkl.dump(history.history, fout)