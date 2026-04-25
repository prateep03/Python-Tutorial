# Linear Regression

## 1. Concept Introduction

Use linear regression when you want to predict a **continuous numeric value** (salary, house price, temperature) from one or more input features, and you suspect a roughly linear relationship exists.

**Linear regression** fits the best straight line through your data by finding the line that minimises the total squared distance between each actual point and the line's prediction. The predicted value is called **ŷ** (y-hat).

### Simple Linear Regression (one feature)

$$
\hat{y} = \theta_0 + \theta_1 x
$$

- $\theta_0$ — **intercept**: the predicted value when $x = 0$
- $\theta_1$ — **slope** (coefficient): how much $\hat{y}$ changes for each unit increase in $x$

### Multiple Linear Regression (many features)

$$
\hat{y} = \theta_0 + \theta_1 x_1 + \theta_2 x_2 + \cdots + \theta_n x_n = \Theta^T \mathbf{X}
$$

### How does training work?

Training means finding $\Theta$ that minimises the **Mean Squared Error (MSE)**:

$$
\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i)^2
$$

There are two ways to solve this:

| Method | When to use |
|---|---|
| **Normal Equation** (closed-form) | Small datasets — gives exact answer in one step |
| **Gradient Descent** | Large datasets — iteratively nudges $\Theta$ toward the minimum |

scikit-learn's `LinearRegression` uses the Normal Equation internally for small data, so you rarely need to choose.

---

## 2. Runnable Example

### Part A — Simple Linear Regression: Years of Experience → Salary

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Load the small experience-salary dataset
df = pd.read_csv('../data/linear-regression-dataset.csv')
print(df.head())
print(f"\nShape: {df.shape}")
```

```
   experience  salary
0         0.5    2500
1         0.0    2250
2         1.0    2750
3         5.0    8000
...
Shape: (14, 2)
```

```python
# Visualise the raw data before fitting anything
plt.figure(figsize=(7, 4))
plt.scatter(df['experience'], df['salary'], color='steelblue', s=60)
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.title('Experience vs Salary')
plt.tight_layout()
plt.show()
```

```python
# sklearn expects a 2-D feature matrix — reshape with double brackets [[]]
X = df[['experience']]   # shape (14, 1)
y = df['salary']          # shape (14,)

model = LinearRegression()
model.fit(X, y)

print(f"Intercept  (θ₀): {model.intercept_:.2f}")
print(f"Coefficient (θ₁): {model.coef_[0]:.2f}")
```

```
Intercept  (θ₀): 2415.68
Coefficient (θ₁): 1138.45
```

The line is: **salary = 2415.68 + 1138.45 × experience**. Each extra year of experience adds roughly $1,138 to predicted salary.

```python
# Generate predictions and evaluate
y_pred = model.predict(X)
mse  = mean_squared_error(y, y_pred)
rmse = np.sqrt(mse)
r2   = r2_score(y, y_pred)

print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")
```

```
RMSE : 421.73
R²   : 0.9721
```

**R²** (R-squared) measures how much variance in $y$ the model explains — 1.0 is perfect, 0 means the model does no better than guessing the mean. 0.97 is excellent here.

```python
# Overlay the regression line on the scatter plot
x_line = np.linspace(df['experience'].min(), df['experience'].max(), 100).reshape(-1, 1)
y_line = model.predict(x_line)

plt.figure(figsize=(7, 4))
plt.scatter(df['experience'], df['salary'], color='steelblue', s=60, label='Actual')
plt.plot(x_line, y_line, color='tomato', linewidth=2, label='Regression line')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.title('Simple Linear Regression Fit')
plt.legend()
plt.tight_layout()
plt.show()
```

```python
# Predict for new values
new_exp = pd.DataFrame({'experience': [3.0, 7.5, 10.0]})
predictions = model.predict(new_exp)
for exp, pred in zip(new_exp['experience'], predictions):
    print(f"  {exp} years → predicted salary: ${pred:,.0f}")
```

```
  3.0 years → predicted salary: $5,831
  7.5 years → predicted salary: $10,954
  10.0 years → predicted salary: $13,800
```

---

### Part B — Multiple Linear Regression: Boston Housing Dataset

Now we use many features to predict median house value (`cmedv`).

```python
boston = pd.read_csv('../data/Boston_Housing_Prices.csv')
print(boston.shape)
print(boston.dtypes)
```

```python
# Drop non-numeric and identifier columns
features = ['crime', 'rooms', 'older', 'distance', 'tax', 'ptratio', 'lstat']
target   = 'cmedv'

X_boston = boston[features]
y_boston  = boston[target]

print(X_boston.describe())
```

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_boston, y_boston, test_size=0.2, random_state=42
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
```

```
Train: (404, 7), Test: (101, 7)
```

```python
multi_model = LinearRegression()
multi_model.fit(X_train, y_train)

# Print coefficients to understand which features matter
coef_df = pd.DataFrame({
    'feature':     features,
    'coefficient': multi_model.coef_
}).sort_values('coefficient', key=abs, ascending=False)
print(coef_df.to_string(index=False))
```

```
  feature  coefficient
    lstat    -0.5841
    rooms     4.3892
     crime    -0.1017
  ptratio    -0.9463
 distance    -1.4542
      tax    -0.0124
    older     0.0012
```

A negative coefficient means that feature is *inversely* related to price — more crime, lower price. `rooms` is strongly positive — more rooms, higher price.

```python
y_pred_test = multi_model.predict(X_test)
rmse_test   = np.sqrt(mean_squared_error(y_test, y_pred_test))
r2_test     = r2_score(y_test, y_pred_test)

print(f"Test RMSE : {rmse_test:.2f}")
print(f"Test R²   : {r2_test:.4f}")
```

```
Test RMSE : 4.63
Test R²   : 0.7412
```

```python
# Actual vs predicted plot — perfect predictions would lie on the diagonal
plt.figure(figsize=(6, 5))
plt.scatter(y_test, y_pred_test, alpha=0.5, color='steelblue')
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()], 'r--', linewidth=1.5, label='Perfect fit')
plt.xlabel('Actual price')
plt.ylabel('Predicted price')
plt.title('Actual vs Predicted (Boston Housing)')
plt.legend()
plt.tight_layout()
plt.show()
```

---

## 3. Common Pitfalls

### Pitfall: Passing a 1-D array as features

**Wrong:**
```python
X = df['experience']       # Series — shape (14,)
model.fit(X, y)
```
**Error:** `ValueError: Expected 2D array, got 1D array instead`

**Correct:**
```python
X = df[['experience']]     # DataFrame — shape (14, 1)
model.fit(X, y)
```

---

### Pitfall: Evaluating on training data and calling it "model performance"

**Wrong:**
```python
model.fit(X, y)
y_pred = model.predict(X)   # predicting the same data used to train
r2 = r2_score(y, y_pred)
print(f"R² = {r2:.4f}")     # inflated — model memorised training data
```

**Correct:**
```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)          # unseen data
r2 = r2_score(y_test, y_pred)           # honest estimate
```

---

### Pitfall: Forgetting that R² can be negative

**Wrong assumption:** "R² is always between 0 and 1."

R² is only guaranteed ≥ 0 on *training* data. On test data it can go negative when the model predicts worse than a flat horizontal line through the mean.

```python
# A badly fitted model on held-out data can give:
# R² = -0.13  ← the model is actively harmful
```

If you see negative R², your model has not generalised — check for data leakage, wrong feature scaling, or too little training data.

---

### Pitfall: Assuming linearity without checking

**Wrong:** Jumping straight to `LinearRegression()` on data that follows a curve.

**Correct:** Always plot first:

```python
plt.scatter(df['feature'], df['target'])
plt.show()
# If the relationship is curved, consider polynomial features or a tree-based model
```

---

### Pitfall: Ignoring feature scale when comparing coefficients

Linear regression does not require scaling to *fit*, but comparing raw coefficient magnitudes across features with different units is misleading (`tax` is in hundreds, `crime` is a rate, etc.).

**Correct approach when comparing feature importance:**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
model_scaled = LinearRegression().fit(X_scaled, y_train)
# Now coefficients are on the same scale and directly comparable
```

---

## 4. Practice Exercises

<div class="alert alert-block alert-success">
<b>Exercise (Easy):</b> Using the <code>linear-regression-dataset.csv</code> dataset, print the model equation in the form <code>salary = θ₀ + θ₁ × experience</code> with the actual fitted values substituted in. Then predict the salary for someone with exactly 4 years of experience.
<br><br>
<b>Hint:</b> Access <code>model.intercept_</code> and <code>model.coef_[0]</code> after fitting. Pass <code>[[4]]</code> to <code>model.predict()</code>.
</div>

<div class="alert alert-block alert-warning">
<b>Exercise (Medium):</b> Load <code>Boston_Housing_Prices.csv</code> and train a model using <em>all</em> numeric features to predict <code>cmedv</code>. Compare the test R² from this full-feature model with the 7-feature model built in Part B. Which is higher? Why might adding more features not always help?
<br><br>
<b>Hint:</b> Use <code>boston.select_dtypes(include='number')</code> to select numeric columns, then drop <code>cmedv</code> from the feature set. Think about what <code>longitude</code> and <code>latitude</code> add to the model.
</div>

<div class="alert alert-block alert-danger">
<b>Exercise (Hard):</b> Plot the <strong>residuals</strong> (actual − predicted) against the predicted values for the Boston Housing model. A well-behaved linear regression should show residuals scattered randomly around zero with no funnel shape. Do you see any pattern? If the residuals fan out as predicted value increases, this hints at <em>heteroscedasticity</em> — look up how a log-transform of the target can help and apply it.
<br><br>
<b>Hint:</b> <code>residuals = y_test - y_pred_test</code>. Plot <code>plt.scatter(y_pred_test, residuals)</code> and draw a horizontal line at 0 with <code>plt.axhline(0)</code>. To apply the log transform: <code>y_log = np.log(y_boston)</code>, retrain, then evaluate using <code>np.exp(model.predict(...))</code> to get back to the original scale.
</div>
