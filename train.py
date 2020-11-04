# Imports
import tensorflow as tf
import keras
import keras.backend as K
from keras.layers import Dense, Dropout, Input
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
from glob import glob
from objects import Table, Food, Snake
from utils import TrainFeeder
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
feeder = TrainFeeder(init_games=init_games)

class LoggingCallback(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"\nCurrent length mean: {feeder.length_mean()}")


# Start Training
logging.info("Starting training.")
from model import snakemodel
snakemodel.feeder = feeder
history = snakemodel.fit(x=feeder.feed,
    epochs=EPOCHS,
    verbose=1,
    callbacks=[ModelCheckpoint("models/epoch_{epoch}.h5", verbose=False), LoggingCallback()],
    steps_per_epoch=STEPS_PER_EPOCH,
#    workers=8
)

with open("models/history.pkl", "wb") as fout:
    pkl.dump(history.history, fout)
