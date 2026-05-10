import tensorflow as tf
import numpy as np
import cv2

# Wczytanie gotowego modelu
model = tf.keras.models.load_model('ocr-mnist.keras')

# Przygotowanie własnego zdjęcia z cyfrą (musi być przygotowane tak jak MNIST: czarne tło, biała cyfra, 28x28 pikseli)
img = cv2.imread('moja_cyfra.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (28, 28))
img = img / 255.0  # Normalizacja
img = np.expand_dims(img, axis=0)  # Dodanie wymiaru "batch", bo model oczekuje listy obrazków

# Rozpoznanie cyfry
przewidywania = model.predict(img)
rozpoznana_cyfra = np.argmax(przewidywania)

print(f"Model myśli, że to cyfra: {rozpoznana_cyfra}")