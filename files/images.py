from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

def load_and_preprocess_image(image_path, target_size=(32, 32)):

    image = load_img(image_path, target_size=target_size)
    def preprocess_images(image, label):
        image = preprocess_input(image)
        return image, label

    image = image.map(preprocess_images)

    return image
