#https://www.tensorflow.org/tutorials/keras/save_and_restore_models 
# Recreate the exact same model, including weights and optimizer.
import matplotlib.pylab as plt
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras import layers
import numpy as np

# [DATA INPUT] Where You put your Data MEANT FOR PREDICTIOn
data_root = (r'D:\\CBIS_DDSM_PNG\\UNMASKED\\CALC')
# Generate Data from directory
image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1/255)

# [Classifier]
feature_extractor_url = "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/2"

def feature_extractor(x):
  feature_extractor_module = hub.Module(feature_extractor_url)
  return feature_extractor_module(x)

IMAGE_SIZE = hub.get_expected_image_size(hub.Module(feature_extractor_url))

# [RESTORE model]
saved_model_path = r'D:\\CBIS_DDSM_PNG\\Classification_Keras_mobilenet_v2_100_224\\1555009140'
new_model = tf.contrib.saved_model.load_keras_model(saved_model_path)
new_model.summary()

# The model has to be compiled before evaluating.
# This step is not required if the saved model is only being deployed.

new_model.compile(optimizer=tf.keras.optimizers.Adam(), 
              loss=tf.keras.losses.sparse_categorical_crossentropy,
              metrics=['accuracy'])

# [TFHub Initialize] - based on current parameters
import tensorflow.keras.backend as K
sess = K.get_session()
init = tf.global_variables_initializer()
sess.run(init)


#  PREDICTIONS
# Check Prediction # modify this!
image_dataPredict = image_generator.flow_from_directory(str(data_root),shuffle=False, target_size=IMAGE_SIZE)

#FInd filenames
#print (image_data.filenames)

nb_samples = len(image_dataPredict.filenames)
result_batch = new_model.predict_generator(image_dataPredict, steps = nb_samples)

label_names = sorted(image_dataPredict.class_indices.items(), key=lambda pair:pair[1])
label_names = np.array([key.title() for key, value in label_names])
labels_batch = label_names[np.argmax(result_batch, axis=-1)]

print(labels_batch)