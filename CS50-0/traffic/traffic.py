import cv2
import numpy as np
import os
import sys
import tensorflow as tf
from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43      # the full dataset
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    data_directory = sys.argv[1] if len(
        sys.argv) > 1 else "/Users/dsparks/Github/Projects/CS50-0/traffic/gtsrb"
    model_filename = sys.argv[2] if len(
        sys.argv) > 2 else "/Users/dsparks/Github/Projects/CS50-0/traffic/traffic.keras"

    # Load data
    images, labels = load_data(data_directory)
    
    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file it it was provided as a command line argument
    if (model_filename):
        model.save(model_filename)
        print(f"Model saved to {model_filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    # Starting with the provied data_dir, process each file while making sure it is a directory
    images = []
    labels = []
    sign_names = os.listdir(data_dir)
    for sign_folder in sign_names:
        sign_folder_full_name = os.path.join(data_dir, sign_folder)
        if os.path.isdir(sign_folder_full_name):

            # We are in a directory, look at each file and process it
            image_names = os.listdir(sign_folder_full_name)
            for image_file in image_names:
                image_full_name = os.path.join(sign_folder_full_name, image_file)
                image_data = cv2.imread(image_full_name)

                # Make sure the image file is valid, if so - change the size and save the image and label
                if image_data is not None:
                    image_data = cv2.resize(image_data, (IMG_WIDTH, IMG_HEIGHT))
                    images.append(image_data)
                    labels.append(int(sign_folder))
                else:
                    print("Invalid image file found:", image_full_name)
    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    
    # Define input shape
    input_shape = (IMG_WIDTH, IMG_HEIGHT, 3)
    
    # Create a convolutional neural network
    model = tf.keras.Sequential([
        # Specify input shape using Input layer
        tf.keras.layers.Input(shape=input_shape),

        # Convolutional layer with 32 filters, 3x3 kernel size, and ReLU activation
        tf.keras.layers.Conv2D(32, (3, 3), activation='sigmoid'),
        tf.keras.layers.Conv2D(16, (5, 5), activation='sigmoid'),
        
        # Max pooling layer with 2x2 pool size
        tf.keras.layers.MaxPooling2D((2, 2)),
        
        # Flatten layer to convert 3D feature maps into 1D feature vectors
        tf.keras.layers.Flatten(),
        
        # Dense (fully connected) layer with 128 neurons, ReLU activation
        tf.keras.layers.Dense(128, activation='sigmoid'),
        
        # Output layer with number of neurons equal to the number of categories and softmax activation
        tf.keras.layers.Dense(NUM_CATEGORIES, activation='softmax')
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model


if __name__ == "__main__":
    main()
