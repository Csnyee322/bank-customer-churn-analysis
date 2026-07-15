import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
)

# matplotlib's default font doesn't support Chinese characters, these two lines fix that
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# -----------------------------------------------------------
# 1. Load and inspect the data
# -----------------------------------------------------------
df = pd.read_csv("churn_data.csv")

print(df.head())
print(df.info())
print(df["Exited"].value_counts())

# -----------------------------------------------------------
# 2. Prepare features and target
# -----------------------------------------------------------
features = ["CreditScore", "Geography", "Gender", "Age", "Tenure",
            "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
            "EstimatedSalary"]
X = df[features]
y = df["Exited"]

# One-hot encode categorical variables (Geography, Gender)
X = pd.get_dummies(X, columns=["Geography", "Gender"], drop_first=True)
X = X.astype(int)

# 80/20 train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training set size:", X_train.shape)
print("Test set size:", X_test.shape)
print(X_train.head())

# -----------------------------------------------------------
# 3. Train logistic regression (with class_weight='balanced' to address class imbalance, ~20% churned vs. ~80% retained)
# -----------------------------------------------------------
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_train, y_train)

# Predictions at the default 0.5 threshold
y_pred = model.predict(X_test)
y_scores = model.predict_proba(X_test)[:, 1]

# -----------------------------------------------------------
# 4. Evaluate logistic regression at the default threshold
# -----------------------------------------------------------
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -----------------------------------------------------------
# 5. Threshold analysis (logistic regression)
#    Since missing a churner (false negative) is costlier than
#    a false alarm, test alternative thresholds vs. the default 0.5
# -----------------------------------------------------------
print("\n" + "=" * 50)
print("Logistic Regression: Threshold Comparison")
print("=" * 50)

for threshold in [0.3, 0.4, 0.5, 0.6]:
    y_pred_custom = (y_scores >= threshold).astype(int)
    print(f"\n=== Threshold = {threshold} ===")
    print(classification_report(y_test, y_pred_custom))

# Precision-Recall vs. Threshold plot
precisions, recalls, thresholds = precision_recall_curve(y_test, y_scores)

plt.figure(figsize=(8, 5))
plt.plot(thresholds, precisions[:-1], label="Precision", color="blue")
plt.plot(thresholds, recalls[:-1], label="Recall", color="orange")
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.title("Precision-Recall vs Threshold")
plt.legend()
plt.grid(True)
plt.show()

# -----------------------------------------------------------
# 6. Feature importance (logistic regression coefficients)
# -----------------------------------------------------------
feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'coefficient': model.coef_[0]
}).sort_values(by='coefficient', key=abs, ascending=False)

print("\nFeature Importance (Logistic Regression Coefficients):")
print(feature_importance)

# -----------------------------------------------------------
# 7. Train Random Forest for comparison
# -----------------------------------------------------------
rf_model = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)
rf_model.fit(X_train, y_train)

rf_y_pred = rf_model.predict(X_test)
rf_scores = rf_model.predict_proba(X_test)[:, 1]

print("\n=== Random Forest Classification Report (default threshold) ===")
print(classification_report(y_test, rf_y_pred))

# Threshold analysis (Random Forest)
print("\n" + "=" * 50)
print("Random Forest: Threshold Comparison")
print("=" * 50)

for threshold in [0.3, 0.4, 0.5]:
    rf_pred_custom = (rf_scores >= threshold).astype(int)
    print(f"\n=== RF Threshold = {threshold} ===")
    print(classification_report(y_test, rf_pred_custom))

# -----------------------------------------------------------
# 8. Compare both models via Precision-Recall Curve
# -----------------------------------------------------------
rf_precisions, rf_recalls, rf_thresholds = precision_recall_curve(y_test, rf_scores)

plt.figure(figsize=(8, 6))
plt.plot(recalls, precisions, label="Logistic Regression", color="blue")
plt.plot(rf_recalls, rf_precisions, label="Random Forest", color="green")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve: Logistic Regression vs Random Forest")
plt.legend()
plt.grid(True)
plt.show()

# -----------------------------------------------------------
# 9. Export predictions for Tableau visualization (keep original text labels for Geography, Gender, etc.)
# -----------------------------------------------------------
export_df = df.loc[X_test.index].copy()

export_df["rf_predicted_churn_probability"] = rf_scores
export_df["rf_predicted_churn_flag_threshold_0.3"] = (rf_scores >= 0.3).astype(int)

export_df.to_csv("churn_predictions.csv", index=False)
print("\nPredictions exported to churn_predictions.csv")
