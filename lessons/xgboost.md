# XGBoost: Extreme Gradient Boosting

## Concept Introduction

**XGBoost (Extreme Gradient Boosting)** is used when you want to build a high-performance classifier or regressor that often wins machine learning competitions. It's an optimized implementation of the **gradient boosting** framework — a technique that combines many weak learners (usually shallow decision trees) into a single strong model.

The key idea behind gradient boosting is **sequential learning**: each new tree is trained to correct the mistakes made by all previous trees. Unlike random forests, which build trees independently and vote on the result, gradient boosting has trees learn from the **residuals** (errors) of prior trees. This focused approach typically yields better accuracy, especially on tabular data.

XGBoost stands out because it:
- Adds regularization to prevent overfitting (L1 and L2 penalties on leaf weights)
- Uses a clever tree-building algorithm that finds splits faster than standard methods
- Handles missing values automatically
- Supports both classification and regression
- Scales well to large datasets

The **mathematics**: each tree minimizes a loss function (like log-loss for classification) plus a regularization term. New trees are added one at a time, with each tree weighted by a learning rate `eta` to avoid overshooting. The predictions accumulate: `y_pred = tree_1(X) + eta * tree_2(X) + eta * tree_3(X) + ...`

## Runnable Example

Let's build a classifier to predict income (>50K or ≤50K) using XGBoost on the adult dataset.

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report

# Load the data
df = pd.read_csv('../data/adult.csv')
print(df.head())
print(f"Shape: {df.shape}")
```
Output:
```
   age  workclass  fnlwgt  education  education-num  ...
0   39  State-gov   77516  Bachelors             13  ...
1   50  Self-emp-not-inc   83311  Bachelors     13  ...
Shape: (32561, 14)
```

Prepare the data for XGBoost (encode categorical columns and split).

```python
# Create a copy and drop irrelevant columns
X = df.drop(['income'], axis=1)
y = (df['income'] == ' >50K').astype(int)  # Binary target

# Encode categorical columns
label_encoders = {}
categorical_cols = X.select_dtypes(include=['object']).columns

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le

print(f"X shape after encoding: {X.shape}")
print(f"Class distribution:\n{y.value_counts()}")
```
Output:
```
X shape after encoding: (32561, 13)
Class distribution:
0    24720
1     7841
dtype: int64
```

Split and train a basic XGBoost model.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create and train the model
model = xgb.XGBClassifier(
    n_estimators=100,      # Number of boosting rounds (trees)
    max_depth=5,           # Max depth of each tree
    learning_rate=0.1,     # Shrinkage (eta) — controls learning speed
    subsample=0.8,         # Fraction of samples used per tree
    colsample_bytree=0.8,  # Fraction of features used per tree
    random_state=42,
    tree_method='hist',    # Faster histogram-based tree building
    eval_metric='logloss'
)

model.fit(X_train, y_train, verbose=False)
print("Model trained!")
```

Evaluate the model.

```python
# Predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

# Feature importance
importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(f"\nTop 5 Features:\n{importance_df.head()}")
```
Output:
```
Accuracy: 0.8742

Classification Report:
              precision    recall  f1-score   support
           0       0.90      0.94      0.92     4894
           1       0.74      0.60      0.67     1561

Top 5 Features:
     feature  importance
8        age       0.2834
12   capital-gain  0.1623
...
```

Now let's tune hyperparameters using cross-validation to improve performance.

```python
from sklearn.model_selection import cross_val_score

# Test different max_depth values
depths = [3, 5, 7, 9]
cv_scores = []

for d in depths:
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=d,
        learning_rate=0.1,
        random_state=42
    )
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    cv_scores.append(scores.mean())
    print(f"max_depth={d}: CV Accuracy = {scores.mean():.4f} (+/- {scores.std():.4f})")
```
Output:
```
max_depth=3: CV Accuracy = 0.8610 (+/- 0.0015)
max_depth=5: CV Accuracy = 0.8718 (+/- 0.0012)
max_depth=7: CV Accuracy = 0.8698 (+/- 0.0020)
max_depth=9: CV Accuracy = 0.8645 (+/- 0.0035)
```

## Common Pitfalls

### Pitfall 1: Not Scaling Categorical Features Before Encoding

**Wrong:**
```python
# Using string values directly
model = xgb.XGBClassifier()
model.fit(df[['gender', 'city']], y)  # Fails! XGBoost expects numeric features
```
**Error:** `ValueError: X has non-numeric dtype object`

**Correct:**
```python
# Encode categorical columns first
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
X['gender'] = le.fit_transform(X['gender'])
model = xgb.XGBClassifier()
model.fit(X, y)  # Works!
```

### Pitfall 2: Over-tuning Hyperparameters Without Early Stopping

**Wrong:**
```python
# Increasing n_estimators indefinitely hoping for better performance
model = xgb.XGBClassifier(
    n_estimators=10000,  # Way too high!
    max_depth=10,
    learning_rate=0.01
)
model.fit(X_train, y_train)  # Takes forever and overfits
```

**Correct:**
```python
# Use early stopping to find the right n_estimators automatically
model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    early_stopping_rounds=10,
    verbose=False
)
print(f"Best n_estimators: {model.best_iteration + 1}")
```

### Pitfall 3: Using Default Parameters Without Checking for Class Imbalance

**Wrong:**
```python
# Dataset has 75% class 0 and 25% class 1
# Default threshold of 0.5 predicts mostly class 0
model = xgb.XGBClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(y_pred.value_counts())  # Mostly 0s — poor recall for class 1
```

**Correct:**
```python
# Adjust scale_pos_weight to account for class imbalance
scale_pos_weight = sum(y_train == 0) / sum(y_train == 1)  # ~3.15
model = xgb.XGBClassifier(
    scale_pos_weight=scale_pos_weight,
    random_state=42
)
model.fit(X_train, y_train)
print(f"Balanced predictions: {model.predict(X_test).value_counts()}")
```

### Pitfall 4: Forgetting That Tree Depth Needs Tuning

**Wrong:**
```python
# Using default max_depth=6 without checking if it's optimal for your data
model = xgb.XGBClassifier(n_estimators=100)
model.fit(X_train, y_train)
# May underfit (too shallow) or overfit (too deep for this dataset)
```

**Correct:**
```python
# Test different depths and pick the best
best_depth = None
best_score = 0
for d in range(3, 11):
    model = xgb.XGBClassifier(n_estimators=100, max_depth=d)
    scores = cross_val_score(model, X_train, y_train, cv=5)
    if scores.mean() > best_score:
        best_score = scores.mean()
        best_depth = d
print(f"Best max_depth: {best_depth} (CV score: {best_score:.4f})")
```

## Practice Exercise

<div class="alert alert-block alert-success">
<b>Exercise (Easy):</b> Load the Iris dataset (use `from sklearn.datasets import load_iris`), train a basic XGBoost classifier to predict the flower species, and print the accuracy on a test set.
<br><br>
<b>Hint:</b> XGBoost expects numeric input. Use `train_test_split` with `test_size=0.2` and `random_state=42`. The dataset has no categorical columns, so you can skip encoding.
</div>

<br>

<div class="alert alert-block alert-info">
<b>Exercise (Medium):</b> Using the adult dataset, find the optimal `max_depth` value by testing depths 2–8 with 5-fold cross-validation. Plot the CV accuracy for each depth and identify the depth with the best score.
<br><br>
<b>Hint:</b> Use `cross_val_score` with `cv=5` and `scoring='accuracy'`. Store results in a list and compare. (Optional: use matplotlib to plot the results.)
</div>

<br>

<div class="alert alert-block alert-success">
<b>Exercise (Hard):</b> Train an XGBoost classifier on the adult dataset with early stopping enabled. Use `eval_set` to monitor validation loss and `early_stopping_rounds=15` to stop training when the validation accuracy plateaus. Compare the number of boosting rounds used (via `model.best_iteration`) versus training without early stopping for 500 rounds.
<br><br>
<b>Hint:</b> Pass `eval_set=[(X_test, y_test)]` and `early_stopping_rounds=15` to the `.fit()` method. Access the best iteration via `model.best_iteration + 1` (add 1 because iteration indexing starts at 0). Time each fit with `%%time` if running in a Jupyter cell.
</div>
