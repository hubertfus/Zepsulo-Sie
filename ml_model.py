import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

class MLModel:
    def __init__(self, model_path='ml_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
                if hasattr(self.model, 'feature_names_in_'):
                    self.feature_names = self.model.feature_names_in_
        else:
            self.train_new_model()
            self.save_model()

    def save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def train_new_model(self, csv_path='sensor_data.csv'):
        df = pd.read_csv(csv_path)

        # Przygotowanie danych
        X = df.drop('fail', axis=1)
        y = df['fail']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Trenowanie modelu
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

    def predict_failure(self, sensor_data):
        if not self.model:
            raise ValueError("Model not loaded or trained")

        input_data = pd.DataFrame([sensor_data])

        if 'fail' in input_data.columns:
            input_data = input_data.drop('fail', axis=1)

        if self.feature_names is not None:
            input_data = input_data[self.feature_names]

        # Predykcja prawdopodobieństwa
        proba = self.model.predict_proba(input_data)[0][1]
        return proba * 100