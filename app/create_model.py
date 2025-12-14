import pickle
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Загрузка датасета Iris
iris = load_iris()
X = iris.data  # 4 признака: sepal length, sepal width, petal length, petal width
y = iris.target  # Классы: 0,1,2 (setosa, versicolor, virginica)

# Разделение на train/test (для проверки)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Обучение модели
model = LogisticRegression(max_iter=200)  # Или другой: from sklearn.tree import DecisionTreeClassifier; model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Проверка accuracy (опционально)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model accuracy on test set: {accuracy:.2f}")

# Сохранение модели
with open('app/model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model trained on Iris and saved to app/model.pkl")