"""The input layer VGG16 expects, as an object CONFIG can name.

A pretrained model is only as good as the inputs it is fed: VGG16 was trained
on 0-255 images in BGR order with the ImageNet channel means subtracted, and
keras ships that exact transformation as a function. Wrapping it in a layer is
what lets the pipeline declare it like any other step, in this example's own
module rather than in the library.
"""
import tensorflow as tf


@tf.keras.utils.register_keras_serializable()
class VGGPreprocessing(tf.keras.layers.Layer):
    """Applies keras' own vgg16 preprocessing to a batch of 0-255 RGB images.

    Registered as serializable so a model holding this layer can be written to
    disk and read back.
    """

    def call(self, inputs):
        return tf.keras.applications.vgg16.preprocess_input(inputs)
