import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.layers import Layer, Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from Common_Model import Common_Model
from TIMNET import TIMNET


def smooth_labels(labels, factor=0.1):
    # smooth the labels
    labels *= (1 - factor)
    labels += (factor / labels.shape[1])
    return labels


class WeightLayer(Layer):
    def __init__(self, **kwargs):
        super(WeightLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.kernel = self.add_weight(name='kernel',
                                      shape=(input_shape[1], 1),
                                      initializer='uniform',
                                      trainable=True)
        super(WeightLayer, self).build(input_shape)

    def call(self, x):
        tempx = tf.transpose(x, [0, 2, 1])
        x = K.dot(tempx, self.kernel)
        x = tf.squeeze(x, axis=-1)
        return x

    def compute_output_shape(self, input_shape):
        return input_shape[0], input_shape[2]


def softmax(x, axis=-1):
    ex = K.exp(x - K.max(x, axis=axis, keepdims=True))
    return ex / K.sum(ex, axis=axis, keepdims=True)


class TIMNET_Model(Common_Model):

    def __init__(self,
                 input_shape,
                 class_labels,
                 filter_size,
                 kernel_size,
                 stack_size,
                 dilation_size,
                 dropout,
                 activation,
                 lr,
                 beta1,
                 beta2,
                 epsilon,
                 **params):
        super(TIMNET_Model, self).__init__(**params)

        self.inputs = Input(shape=(input_shape[0], input_shape[1]))
        self.multi_decision = TIMNET(nb_filters=filter_size,
                                     kernel_size=kernel_size,
                                     nb_stacks=stack_size,
                                     dilations=dilation_size,
                                     dropout_rate=dropout,
                                     activation=activation,
                                     return_sequences=True,
                                     name='TIMNET')(self.inputs)

        self.decision = WeightLayer()(self.multi_decision)
        self.predictions = Dense(len(class_labels), activation='softmax')(self.decision)
        self.model = Model(inputs=self.inputs, outputs=self.predictions)

        self.model.compile(loss="categorical_crossentropy",
                           optimizer=Adam(learning_rate=lr, beta_1=beta1, beta_2=beta2,
                                          epsilon=epsilon),
                           metrics=['accuracy'])

    def load_weights(self, model_path):
        self.model.load_weights(model_path)

    def predict(self, x):
        return self.model.predict(x)[0]
