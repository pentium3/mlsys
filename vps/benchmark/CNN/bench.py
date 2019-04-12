import tensorflow as tf
import numpy as np
import os
import time
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.examples.tutorials.mnist import input_data


class Bench(object):
    total_ptime = 0

    def init_weights(self, shape):
        return tf.Variable(tf.random_normal(shape, stddev=0.01))

    def model(self, X, w, w2, w3, w4, w_o, p_keep_conv, p_keep_hidden):
        l1a = tf.nn.relu(tf.nn.conv2d(X, w, strides=[1, 1, 1, 1], padding='SAME'))
        l1 = tf.nn.max_pool(l1a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        l1 = tf.nn.dropout(l1, p_keep_conv)
        l2a = tf.nn.relu(tf.nn.conv2d(l1, w2, strides=[1, 1, 1, 1], padding='SAME'))
        l2 = tf.nn.max_pool(l2a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        l2 = tf.nn.dropout(l2, p_keep_conv)
        l3a = tf.nn.relu(tf.nn.conv2d(l2, w3, strides=[1, 1, 1, 1], padding='SAME'))
        l3 = tf.nn.max_pool(l3a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        l3 = tf.reshape(l3, [-1, w4.get_shape().as_list()[0]])  # reshape to (?, 2048)
        l3 = tf.nn.dropout(l3, p_keep_conv)
        l4 = tf.nn.relu(tf.matmul(l3, w4))
        l4 = tf.nn.dropout(l4, p_keep_hidden)
        pyx = tf.matmul(l4, w_o)
        return pyx

    def Run(self, ):
        start_time = time.time()
        mnist = input_data.read_data_sets("benchmark/CNN/MNIST-data/", one_hot=True)
        trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels
        trX = trX.reshape(-1, 28, 28, 1)
        teX = teX.reshape(-1, 28, 28, 1)
        X = tf.placeholder("float", [None, 28, 28, 1])
        Y = tf.placeholder("float", [None, 10])
        w = self.init_weights([3, 3, 1, 32])
        w2 = self.init_weights([3, 3, 32, 64])
        w3 = self.init_weights([3, 3, 64, 128])
        w4 = self.init_weights([128 * 4 * 4, 625])
        w_o = self.init_weights([625, 10])
        p_keep_conv = tf.placeholder("float")
        p_keep_hidden = tf.placeholder("float")
        py_x = self.model(X, w, w2, w3, w4, w_o, p_keep_conv, p_keep_hidden)
        cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=py_x, labels=Y))
        train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)
        predict_op = tf.argmax(py_x, 1)
        batch_size = 512
        test_size = 256
        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            for i in range(5):
                training_batch = zip(range(0, len(trX), batch_size), range(batch_size, len(trX) + 1, batch_size))
                for start, end in training_batch:
                    # print(start, end)
                    sess.run(train_op,
                             feed_dict={X: trX[start:end], Y: trY[start:end], p_keep_conv: 0.8, p_keep_hidden: 0.5})
                test_indices = np.arange(len(teX))
                np.random.shuffle(test_indices)
                test_indices = test_indices[0:test_size]
                print(i, np.mean(np.argmax(teY[test_indices], axis=1) ==
                                 sess.run(predict_op,
                                          feed_dict={X: teX[test_indices], p_keep_conv: 1.0, p_keep_hidden: 1.0})))
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark CNN: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        time.sleep(10)
        print("This is Benchmark CNN")
        return (10)

