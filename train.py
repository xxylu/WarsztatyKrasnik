import tensorflow as tf
from tensorflow.keras import layers, models

# 1. Pobranie i przygotowanie danych MNIST
# Keras ma ten zbiór wbudowany, więc pobierze go automatycznie
print("Pobieranie danych...")
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Normalizacja danych: wartości pikseli (0-255) zamieniamy na ułamki (0.0-1.0).
# Dzięki temu sieć neuronowa uczy się znacznie szybciej i stabilniej.
x_train, x_test = x_train / 255.0, x_test / 255.0

# 2. Budowa architektury modelu
model = models.Sequential([
    # Obrazki w MNIST mają 28x28 pikseli. Flatten spłaszcza je do wektora 784 liczb.
    layers.Flatten(input_shape=(28, 28)),

    # Ukryta warstwa z 128 neuronami (mózg naszej sieci) z funkcją aktywacji ReLU
    layers.Dense(128, activation='relu'),

    # Dropout "wyłącza" losowo 20% neuronów podczas treningu, aby zapobiec
    # zapamiętywaniu danych na pamięć (tzw. overfitting)
    layers.Dropout(0.2),

    # Warstwa wyjściowa: 10 neuronów (dla cyfr 0-9).
    # Funkcja softmax sprawia, że wynik to procentowe prawdopodobieństwo dla każdej cyfry.
    layers.Dense(10, activation='softmax')
])

# 3. Kompilacja modelu (ustawienie sposobu uczenia)
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 4. Trenowanie modelu
print("\nRozpoczynam trenowanie...")
# W parametrze epochs podajemy, ile razy model ma "zobaczyć" cały zbiór danych.
history = model.fit(x_train, y_train, epochs=5, validation_split=0.1)

# 5. Ewaluacja (testowanie) modelu
# Sprawdzamy, jak model radzi sobie na danych testowych, których NIGDY wcześniej nie widział.
print("\nTestowanie modelu na nowych danych...")
test_loss, test_acc = model.evaluate(x_test,  y_test, verbose=2)
print(f"\nDokładność (accuracy) na danych testowych: {test_acc * 100:.2f}%")

# 6. Zapisanie modelu do pliku
model.save('ocr-mnist.keras')
print("\nGotowe! Model został zapisany jako 'moj_model_mnist.keras'")
