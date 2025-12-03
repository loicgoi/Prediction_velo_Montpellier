from modeling.preprocessor import DataPreprocessor
from modeling.trainer import ModelTrainer
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Charger les données propres
print("Chargement des données...")
# Assure-toi que ce chemin est bon depuis l'endroit où tu lances le script
df = pd.read_csv('data/output/features_ready_for_training.csv')

# 2. Split Temporel MANUEL
cutoff_date = '2025-09-01'
df['date'] = pd.to_datetime(df['date'])

# Tri chronologique indispensable
df = df.sort_values(by=['date', 'station_id'])

train = df[df['date'] < cutoff_date]
test = df[df['date'] >= cutoff_date]

print(f"Train set : {len(train)} lignes")
print(f"Test set  : {len(test)} lignes")

# 3. Préprocessing
print("Préprocessing...")
preprocessor = DataPreprocessor()
X_train, y_train = preprocessor.fit(train).transform(train)
X_test, y_test = preprocessor.transform(test)

# 4. Entraînement
print("Entraînement en cours...")
trainer = ModelTrainer()
trainer.train(X_train, y_train)

# 5. Évaluation détaillée
print("\n--- CALCUL DES MÉTRIQUES ---")

# On récupère le modèle entraîné pour faire nos propres prédictions
model = trainer.best_model
y_pred = model.predict(X_test)

# Calcul des scores
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("-" * 40)
print(f"RMSE (Root Mean Squared Error) : {rmse:.2f}")
print(f"MAE  (Mean Absolute Error)     : {mae:.2f}")
print(f"R²   (Coefficient de dét.)     : {r2:.4f}")
print("-" * 40)

# Interprétation rapide pour toi
print(f"En moyenne, le modèle se trompe de {mae:.0f} vélos par prédiction.")
if r2 > 0.8:
    print("Performance : EXCELLENTE (> 0.8)")
elif r2 > 0.6:
    print("Performance : BONNE (> 0.6)")
else:
    print("Performance : MOYENNE/FAIBLE (À améliorer)")

print("\n--- 🧠 ANALYSE DE L'IMPORTANCE DES FEATURES ---")

# 1. Récupération des noms et des scores
# Le modèle entraîné est dans trainer.best_model
model = trainer.best_model

# Les noms des colonnes sont stockés dans ton préprocesseur
feature_names = preprocessor.features_cols 
importances = model.feature_importances_

# 2. Création d'un DataFrame pour trier
df_importance = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Affichage tableau
print(df_importance.head(10))

# 3. Visualisation Graphique
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=df_importance.head(15), palette="viridis")

plt.title('Top 15 des Features les plus déterminantes (XGBoost)')
plt.xlabel('Poids (Gain d\'information)')
plt.ylabel('Features')
plt.grid(True, axis='x', alpha=0.3)
plt.tight_layout()
plt.show()

print("Graphique généré.")

# 6. Sauvegarde
print("\nSauvegarde...")
trainer.save('backend/data/models/xgboost_test.pkl')
preprocessor.save('backend/data/models/preprocessor_test.pkl')
print("Terminé.")