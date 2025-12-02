from backend.modeling.preprocessor import DataPreprocessor
from backend.modeling.trainer import ModelTrainer
import pandas as pd

# 1. Charger les données propres
df = pd.read_csv('backend/data/output/dataset_final.csv')

# 2. Split Temporel MANUEL (Train = passé, Test = fin de la période)
# C'est important de garder un morceau "inédit" pour l'évaluation finale
cutoff_date = '2025-09-01' # Exemple
df['date'] = pd.to_datetime(df['date']) # Assurance

train = df[df['date'] < cutoff_date]
test = df[df['date'] >= cutoff_date]

print(f"Train set : {len(train)} lignes")
print(f"Test set  : {len(test)} lignes")

# 3. Préprocessing
preprocessor = DataPreprocessor()
X_train, y_train = preprocessor.fit(train).transform(train) # Fit uniquement sur le train !
X_test, y_test = preprocessor.transform(test)               # Transform sur le test

# 4. Entraînement
trainer = ModelTrainer()
trainer.train(X_train, y_train)

# 5. Évaluation
trainer.evaluate(X_test, y_test)

# 6. Sauvegarde
trainer.save('backend/data/models/xgboost_v1.pkl')
preprocessor.save('backend/data/models/preprocessor_v1.pkl')