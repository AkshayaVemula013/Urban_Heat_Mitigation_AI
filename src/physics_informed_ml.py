import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================================
# PHASE 3: PHYSICS-INFORMED ML MODELING
# =========================================================================

# 1. Load the high-contrast single-event summer data file (V4 Baseline)
df_v4 = pd.read_csv('sample_data/Chennai_Urban_Heat_AI_Data_V4.csv')
df_v4 = df_v4.dropna()

# 2. Physics-Informed Feature Engineering: Calculate thermodynamic surface contrasts
df_v4['Thermal_Absorptive_Index'] = df_v4['NDBI'] - df_v4['NDVI']

# 3. Define Inputs (X) and Target Land Surface Temperature (y)
X = df_v4[['NDVI', 'NDBI', 'Thermal_Absorptive_Index']]
y = df_v4['LST']

# 4. Split data into Training (80%) and Test Validation sets (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Initialize and train a robust ensemble Gradient Boosting Regressor
ai_brain = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
ai_brain.fit(X_train, y_train)

# 6. Evaluate initial baseline predictive performance
preds = ai_brain.predict(X_test)
r2 = r2_score(y_test, preds)
rmse = np.sqrt(mean_squared_error(y_test, preds))

print("--- CHENNAI SATELLITE AI TRAINING COMPLETE ---")
print(f"Model Predictive Accuracy (R2 Score): {r2 * 100:.2f}%")
print(f"Average Temperature Deviation Margin (RMSE): {rmse:.2f}°C\n")

# =========================================================================
# PHASE 4: QUANTIFYING DRIVERS & INTERVENTION SIMULATION
# =========================================================================

# 1. Output Feature Importance Weights to reveal physical drivers
importances = ai_brain.feature_importances_
feature_names = ['NDVI (Trees)', 'NDBI (Concrete)', 'Thermal_Absorptive_Index']

print("--- URBAN HEAT DRIVER WEIGHTS ---")
for name, importance in zip(feature_names, importances):
    print(f"{name}: {importance * 100:.2f}% impact on temperature spikes")
print("\n")

# 2. Define the policy mitigation simulation engine
def simulate_cooling_intervention(input_data, ml_model, green_increase=0.20, concrete_decrease=0.10):
    simulated_df = input_data.copy()
    
    # Inject policy variations while maintaining physical boundary bounds [-1, 1]
    simulated_df['NDVI'] = np.clip(simulated_df['NDVI'] + green_increase, -1.0, 1.0)
    simulated_df['NDBI'] = np.clip(simulated_df['NDBI'] - concrete_decrease, -1.0, 1.0)
    simulated_df['Thermal_Absorptive_Index'] = simulated_df['NDBI'] - simulated_df['NDVI']
    
    # Run predictions through the model
    X_simulated = simulated_df[['NDVI', 'NDBI', 'Thermal_Absorptive_Index']]
    predicted_lst_new = ml_model.predict(X_simulated)
    
    avg_baseline_temp = input_data['LST'].mean()
    avg_simulated_temp = predicted_lst_new.mean()
    temperature_drop = avg_baseline_temp - avg_simulated_temp
    
    print("--- POLICY INTERVENTION SIMULATION RESULT ---")
    print(f"Policy: +{green_increase*100}% Trees, -{concrete_decrease*100}% Concrete Absorption")
    print(f"Average Baseline Temperature: {avg_baseline_temp:.2f}°C")
    print(f"Average Simulated Post-Intervention Temp: {avg_simulated_temp:.2f}°C")
    print(f"Predicted Drop in Urban Heat: {temperature_drop:.2f}°C\n")
    
    return simulated_df

# Execute cooling policy simulation scenarios
simulated_dataset = simulate_cooling_intervention(df_v4, ai_brain)

# =========================================================================
# STEP 4.3: VISUALIZATION DENSITY GENERATION
# =========================================================================
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

sns.kdeplot(df_v4['LST'], color='crimson', fill=True, alpha=0.4, linewidth=2.5, label='Original Baseline (Chennai Today)')
sim_preds = ai_brain.predict(simulated_dataset[['NDVI', 'NDBI', 'Thermal_Absorptive_Index']])
sns.kdeplot(sim_preds, color='forestgreen', fill=True, alpha=0.4, linewidth=2.5, label='Simulated Policy (+20% Trees, -10% Concrete)')

plt.axvline(df_v4['LST'].mean(), color='crimson', linestyle='--', linewidth=1.5)
plt.axvline(sim_preds.mean(), color='forestgreen', linestyle='--', linewidth=1.5)

plt.title('AI-Simulated Cooling Impact: Before vs. After Urban Intervention', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Land Surface Temperature (°C)', fontsize=12)
plt.ylabel('Density of Hotspots', fontsize=12)
plt.xlim(30, 50)
plt.legend(fontsize=11, loc='upper left')

plt.tight_layout()
plt.savefig('outputs/cooling_simulation_plot.png', dpi=300, bbox_inches='tight')
print("--- GRAPH GENERATION ARCHIVED SUCCESSFULLY ---")
