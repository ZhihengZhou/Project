import os
import cv2
import numpy as np
import tqdm
from layer import *
from network import *

def load(dir_='../data/npy'):
    x_train = np.load(os.path.join(dir_, 'x_train.npy'))
    x_test = np.load(os.path.join(dir_, 'x_test.npy'))
    return x_train, x_test

# Hyperparameters
IMAGE_SIZE2 = 160
IMAGE_SIZE1 = 256
LOCAL_SIZE = 64
HOLE_MIN = 24
HOLE_MAX = 48
LEARNING_RATE = 1e-3
BATCH_SIZE = 16
PRETRAIN_EPOCH = 100

x = tf.placeholder(tf.float32, [BATCH_SIZE, IMAGE_SIZE1, IMAGE_SIZE2, 3])
mask = tf.placeholder(tf.float32, [BATCH_SIZE, IMAGE_SIZE1, IMAGE_SIZE2, 1])
local_x = tf.placeholder(tf.float32, [BATCH_SIZE, LOCAL_SIZE, LOCAL_SIZE, 3])
global_completion = tf.placeholder(tf.float32, [BATCH_SIZE, IMAGE_SIZE1, IMAGE_SIZE2, 3])
local_completion = tf.placeholder(tf.float32, [BATCH_SIZE, LOCAL_SIZE, LOCAL_SIZE, 3])
is_training = tf.placeholder(tf.bool, [])

model = Network(x, mask, local_x, global_completion, local_completion, is_training, batch_size=BATCH_SIZE)

global_step = tf.Variable(0, name='global_step', trainable=False)
epoch = tf.Variable(0, name='epoch', trainable=False)

opt = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)

g_train_op = opt.minimize(model.g_loss, global_step=global_step, var_list=model.g_variables)

d_train_op = opt.minimize(model.d_loss, global_step=global_step, var_list=model.d_variables)
