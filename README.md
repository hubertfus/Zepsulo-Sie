# ZepsułoSię.py

---

## 🧠 **Cel projektu**

Zbudowanie systemu symulującego działanie maszyny przemysłowej, który:

* cyklicznie pobiera dane z czujników (symulowanych),
* analizuje dane w czasie rzeczywistym przy pomocy modelu ML wbudowanego,
* podejmuje decyzje o „wyłączeniu” maszyny,
* w razie niepewności konsultuje się z zewnętrznym serwerem–ekspertem.

---

## 🧩 **Moduły systemu (architektura)**

### 1. **Symulacja czujników (czyli źródło danych)**

* Jeden plik CSV z danymi historycznymi z czujników (symulowane dane np. temperatura, ciśnienie, drgania).
* Skrypt w Pythonie odczytuje dane w pętli (co np. 1 sekunda), linia po linii – tak jakby dane przychodziły w czasie rzeczywistym.
* Dane trafiają do „maszyny”.

**Plik ************`sensor_simulator.py`************:**

* odczyt CSV linia po linii,
* symulacja opóźnienia (`time.sleep()`),
* przekazywanie danych do maszyny (np. przez kolejkę lub bezpośrednio do funkcji).

---

### 2. **Model predykcyjny (ML)**

* Uczenie modelu ML offline (np. klasyfikator awarii – logistic regression, random forest, itp.).
* Model ma za zadanie przewidywać prawdopodobieństwo awarii na podstawie zestawu parametrów.
* Jeżeli prawdopodobieństwo > 70%, maszyna się „wyłącza” na chwilę (czyli pauzuje cykl).

**Plik ************`ml_model.py`************:**

* Funkcja `predict_failure(sensor_data) -> float`,
* Model wcześniej wytrenowany, zapisany jako `.pkl`.

---

### 3. **Logika maszyny**

* Cykl: odczyt danych → analiza → decyzja.
* Jeśli prawdopodobieństwo awarii > 70% → **stop** na 10 sekund.
* Jeśli prawdopodobieństwo między 40–70% → pytanie do **eksperta (serwera)**.
* Jeśli < 40% → kontynuuj normalnie.

**Plik ************`machine_controller.py`************:**

* Główna pętla symulacji pracy maszyny,
* Import modelu ML i logiki eksperta.

---

### 4. **Ekspert (serwer)**

* Serwer Flask/FastAPI nasłuchujący zapytań,
* Odbiera dane z maszyny i również uruchamia swój model ML (np. inny albo lepiej wytrenowany),
* Zwraca rekomendację (np. `OK` lub `STOP`).

**Plik ************`expert_server.py`************:**

* Endpoint `/analyze` przyjmujący dane JSON,
* Zwraca `{"decision": "STOP"}` lub `{"decision": "OK"}`.

---

### 5. **Komunikacja (opcjonalnie)**

* Maszyna → serwer poprzez HTTP (np. `requests.post()`).

---

## 📂 **Struktura projektu**

```
machine_simulation/
├── sensor_data.csv
├── sensor_simulator.py
├── ml_model.py
├── train_model.py
├── machine_controller.py
├── expert_server.py
├── utils/
│   └── data_preprocessing.py
└── models/
    └── model.pkl
```

---

## 📌 **Przykładowy scenariusz działania**

1. `sensor_simulator.py` odczytuje linię z CSV co sekundę.
2. `machine_controller.py` pobiera dane i podaje je do `ml_model.py`.
3. Jeśli wynik > 70%, maszyna „wyłącza się” na 10 sekund (`time.sleep(10)`).
4. Jeśli wynik 40–70%, wysyła zapytanie do `expert_server.py`.
5. Serwer odpowiada – maszyna podejmuje decyzję.

---

## 🛠️ **Technologie**

* Python 
* Scikit-learn / XGBoost (model ML)
* Pandas (dane CSV)
* FastAPI / Flask (serwer ekspercki)
* Matplotlib 

---

## 🔮 Co dalej?

* Logger z zapisem do pliku.
* UI do wizualizacji statusu maszyny.
* Baza danych na historię zdarzeń.
* Kilka maszyn symultanicznie.

---

