import tensorflow as tf
import numpy as np
import os
import time
from tensorflow.examples.tutorials.mnist import input_data


class Bench(object):
    total_ptime = 0

    def lrelu(self, x, th=0.2):
        return tf.maximum(th * x, x)

    def generator(self, x, isTrain=True, reuse=False):
        with tf.variable_scope('generator', reuse=reuse):
            # 1st hidden layer
            conv1 = tf.layers.conv2d_transpose(x, 1024, [4, 4], strides=(1, 1), padding='valid')
            lrelu1 = self.lrelu(tf.layers.batch_normalization(conv1, training=isTrain), 0.2)

            # 2nd hidden layer
            conv2 = tf.layers.conv2d_transpose(lrelu1, 512, [4, 4], strides=(2, 2), padding='same')
            lrelu2 = self.lrelu(tf.layers.batch_normalization(conv2, training=isTrain), 0.2)

            # 3rd hidden layer
            conv3 = tf.layers.conv2d_transpose(lrelu2, 256, [4, 4], strides=(2, 2), padding='same')
            lrelu3 = self.lrelu(tf.layers.batch_normalization(conv3, training=isTrain), 0.2)

            # 4th hidden layer
            conv4 = tf.layers.conv2d_transpose(lrelu3, 128, [4, 4], strides=(2, 2), padding='same')
            lrelu4 = self.lrelu(tf.layers.batch_normalization(conv4, training=isTrain), 0.2)

            # output layer
            conv5 = tf.layers.conv2d_transpose(lrelu4, 1, [4, 4], strides=(2, 2), padding='same')
            o = tf.nn.tanh(conv5)

            return o

    def discriminator(self, x, isTrain=True, reuse=False):
        with tf.variable_scope('discriminator', reuse=reuse):
            # 1st hidden layer
            conv1 = tf.layers.conv2d(x, 128, [4, 4], strides=(2, 2), padding='same')
            lrelu1 = self.lrelu(conv1, 0.2)

            # 2nd hidden layer
            conv2 = tf.layers.conv2d(lrelu1, 256, [4, 4], strides=(2, 2), padding='same')
            lrelu2 = self.lrelu(tf.layers.batch_normalization(conv2, training=isTrain), 0.2)

            # 3rd hidden layer
            conv3 = tf.layers.conv2d(lrelu2, 512, [4, 4], strides=(2, 2), padding='same')
            lrelu3 = self.lrelu(tf.layers.batch_normalization(conv3, training=isTrain), 0.2)

            # 4th hidden layer
            conv4 = tf.layers.conv2d(lrelu3, 1024, [4, 4], strides=(2, 2), padding='same')
            lrelu4 = self.lrelu(tf.layers.batch_normalization(conv4, training=isTrain), 0.2)

            # output layer
            conv5 = tf.layers.conv2d(lrelu4, 1, [4, 4], strides=(1, 1), padding='valid')
            o = tf.nn.sigmoid(conv5)

            return o, conv5

    def RunGan(self, ):
        # training parameters
        batch_size = 200
        lr = 0.0002
        train_epoch = 1

        # load MNIST
        mnist = input_data.read_data_sets("MNIST_data/", one_hot=True, reshape=[])

        # variables : input
        x = tf.placeholder(tf.float32, shape=(None, 64, 64, 1))
        z = tf.placeholder(tf.float32, shape=(None, 1, 1, 100))
        isTrain = tf.placeholder(dtype=tf.bool)

        # networks : generator
        G_z = self.generator(z, isTrain)

        # networks : discriminator
        D_real, D_real_logits = self.discriminator(x, isTrain)
        D_fake, D_fake_logits = self.discriminator(G_z, isTrain, reuse=True)

        # loss for each network
        D_loss_real = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(logits=D_real_logits, labels=tf.ones([batch_size, 1, 1, 1])))
        D_loss_fake = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(logits=D_fake_logits, labels=tf.zeros([batch_size, 1, 1, 1])))
        D_loss = D_loss_real + D_loss_fake
        G_loss = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(logits=D_fake_logits, labels=tf.ones([batch_size, 1, 1, 1])))

        # trainable variables for each network
        T_vars = tf.trainable_variables()
        D_vars = [var for var in T_vars if var.name.startswith('discriminator')]
        G_vars = [var for var in T_vars if var.name.startswith('generator')]

        # optimizer for each network
        with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
            D_optim = tf.train.AdamOptimizer(lr, beta1=0.5).minimize(D_loss, var_list=D_vars)
            G_optim = tf.train.AdamOptimizer(lr, beta1=0.5).minimize(G_loss, var_list=G_vars)

        # open session and initialize all variables
        sess = tf.InteractiveSession()
        tf.global_variables_initializer().run()

        # MNIST resize and normalization
        train_set = tf.image.resize_images(mnist.train.images, [64, 64]).eval()
        train_set = (train_set - 0.5) / 0.5  # normalization; range: -1 ~ 1

        # training-loop
        print('training start!')
        for epoch in range(train_epoch):
            G_losses = []
            D_losses = []
            for iter in range(mnist.train.num_examples // batch_size // 8):
                print("iter: ", iter, "//", mnist.train.num_examples // batch_size // 8)
                # update discriminator
                x_ = train_set[iter * batch_size:(iter + 1) * batch_size]
                z_ = np.random.normal(0, 1, (batch_size, 1, 1, 100))
                loss_d_, _ = sess.run([D_loss, D_optim], {x: x_, z: z_, isTrain: True})
                D_losses.append(loss_d_)
                # update generator
                z_ = np.random.normal(0, 1, (batch_size, 1, 1, 100))
                loss_g_, _ = sess.run([G_loss, G_optim], {z: z_, x: x_, isTrain: True})
                G_losses.append(loss_g_)
        sess.close()

    def Run(self, ):
        start_time = time.time()
        self.RunGan()
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark GAN: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        time.sleep(10)
        print("This is Benchmark GAN")
        return (10)

