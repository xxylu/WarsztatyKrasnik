import tensorflow as tf
import numpy as np
import cv2

# 1. Konfiguracja - podaj bezpośrednią ścieżkę do zdjęcia
file_path = 'data/cyfra.png'

# 2. Wczytanie modelu
model = tf.keras.models.load_model('ocr-mnist.keras')

# 3. Wczytanie i przygotowanie zdjęcia
img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

img_resized = cv2.resize(img, (28, 28))
img_normalized = img_resized / 255.0
img_batch = np.expand_dims(img_normalized, axis=0)

# 4. Predykcja
predict = model.predict(img_batch, verbose=0)
recognised = np.argmax(predict)

print("-" * 30)
print(f"Wynik dla {file_path}: {recognised}")
print("-" * 30)