import keras
from keras.layers import Dense, Dropout, Input
from keras.models import Sequential
import tensorflow as tf
import os

# Variables
VIRTUAL_HEIGHT = int(os.environ["VIRTUAL_HEIGHT"])
VIRTUAL_WIDTH = int(os.environ["VIRTUAL_WIDTH"])
DIM = VIRTUAL_WIDTH * VIRTUAL_HEIGHT
MOVE_CODE = {0:"right", 1:"left", 2:"up", 3:"down"}

score_metric = keras.metrics.Mean(name="score")
cce_loss = keras.losses.CategoricalCrossentropy()

class SnakeModel(keras.Sequential):
    def train_step(self, data):
        x, y_true, idx = data
        
        with tf.GradientTape() as tape:
            y_pred = self(x, training=True) # Forward pass
            
            # Compute loss
            loss = cce_loss(y_true, y_pred)
        
        # Move 
        feeder = self.feeder  ## Warning: you have to update it when you call the model
        predicted_direction = MOVE_CODE[y_pred.numpy().argmax()]
        score = feeder.apply_move(predicted_direction, int(idx))
        
        # Compute gradients and update weights
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        
        # Compute the metric score here
        score_metric.update_state(loss)
        
        return {"mean_score": score_metric.result()}#, "mean_length": feeder.length_mean()}
    
    @property
    def metrics(self):
        return [score_metric]

snakemodel = SnakeModel()
snakemodel.add(Input(shape=(DIM, )))
snakemodel.add(Dense(DIM, activation=None))
snakemodel.add(Dense(16, activation=None))
snakemodel.add(Dense(4, activation="softmax"))