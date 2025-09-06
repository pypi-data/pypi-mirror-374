import numpy as np

class SingleNeuron:
    def __init__(self, input_size, learning_rate=0.01, epochs=100):
        self.weights = np.random.randn(input_size)
        self.bias = np.random.randn()
        self.learning_rate = learning_rate
        self.epochs = epochs

    @staticmethod
    def activation_function(x):
        # تابع فعال‌ساز سیگموئید
        return 1 / (1 + np.exp(-x))

    def forward(self, inputs):
        # محاسبه جمع وزنی و اعمال تابع فعال‌ساز
        weighted_sum = np.dot(inputs, self.weights) + self.bias
        return self.activation_function(weighted_sum)

    def train(self, X, y):
        for epoch in range(self.epochs):
            for inputs, label in zip(X, y):
                # پیش‌بینی
                prediction = self.forward(inputs)

                # محاسبه خطا
                error = label - prediction

                # به روزرسانی وزن‌ها و بایاس
                self.weights += self.learning_rate * error * inputs
                self.bias += self.learning_rate * error

            # نمایش خطا در هر دوره (اختیاری)
            if epoch % 10 == 0:
                total_error = np.mean(np.square(y - [self.forward(x) for x in X]))
                print(f"Epoch {epoch}, Error: {total_error:.4f}")


if __name__ == "__main__":
    # داده‌های آموزشی (OR Gate)
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 1, 1, 1])

    # ایجاد و آموزش نورون
    neuron = SingleNeuron(input_size=2, learning_rate=0.1, epochs=100)
    neuron.train(X, y)

    # تست پس از آموزش
    print("\nPredictions after training:")
    for x in X:
        print(f"{x} -> {neuron.forward(x):.4f}")