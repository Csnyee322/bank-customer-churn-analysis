# Bank Customer Churn Analysis

## Executive Summary
This analysis identifies which customers a U.S. bank is losing and why, then translates those patterns into a prioritized retention action plan. Three findings stand out: customers holding 3+ products churn at 82–100% (likely a cross-selling/bundling problem, not loyalty), inactive members churn at nearly 2x the rate of active ones, and churned customers disproportionately hold high-value balances (24% of deposits from only 20% of customers). A Random Forest model built on these drivers flags ~475 high-risk customers for proactive outreach, giving the bank a concrete, ranked list rather than a population-wide guess.

## Project Background

This project analyzes a U.S. bank's customer dataset to understand the key factors driving customer churn — i.e., which customers are leaving the bank and why. The goal is to identify actionable patterns that could help the bank design more effective customer retention strategies.

## Data Description

- **Data source:** [Kaggle – Bank Customer Churn Prediction](https://www.kaggle.com/datasets)
- **Rows:** 10,000 customers
- **Key fields:** CustomerId, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited (churn flag)

## Tools Used

- **PostgreSQL (pgAdmin 4)** — data storage, cleaning, and analysis
- **Excel / Python (scipy)** — statistical hypothesis testing (t-test)
- **Python (pandas, scikit-learn, matplotlib)** — predictive modeling, class imbalance handling, threshold analysis
- **Tableau Public** — interactive dashboard and visualization

---

## Key Findings (SQL Exploratory Analysis)

### 1. Product Holdings Strongly Predict Churn (Most Significant Finding)

```sql
SELECT "NumOfProducts",
       COUNT(*) AS total_customers,
       SUM("Exited") AS churned_customers,
       ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "NumOfProducts"
ORDER BY "NumOfProducts" DESC;
```

**Finding:** Customers holding 1–2 products show a relatively low churn rate (7.58%–27.71%), consistent with the intuition that customers who buy more products tend to be more loyal. However, customers holding 3–4 products show a dramatically higher churn rate (82.71%–100%), despite the smaller sample sizes (266 and 60 customers respectively). This pattern is consistent across both groups and is unlikely to be coincidental.

**Business implication:** This counter-intuitive trend suggests these customers may not be more loyal — they may instead be victims of aggressive product bundling/cross-selling, or there may be a systemic issue with a specific product combination causing broader dissatisfaction. This warrants further investigation by the bank.

---

### 2. Inactive Customers Churn at Nearly 2x the Rate of Active Customers

```sql
SELECT "IsActiveMember",
       COUNT(*) AS total_customers,
       SUM("Exited") AS churned_customers,
       ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "IsActiveMember";
```

**Finding:** Inactive customers (IsActiveMember = 0) churn at a rate of 26.85%, compared to 14.27% for active customers — nearly double the risk.

**Business implication:** Customer activity level can serve as an early warning signal. The bank could proactively reach out to long-inactive customers (e.g., targeted offers, relationship manager check-ins) before they churn entirely.

---

### 3. Churned Customers Disproportionately Represent High-Value Balances

```sql
SELECT "Exited",
       COUNT(*) AS total_customers,
       AVG("Balance") AS avg_balance
FROM "Churn"
GROUP BY "Exited";

SELECT
  ROUND(SUM(CASE WHEN "Exited" = 1 THEN "Balance" ELSE 0 END)
      / SUM("Balance") * 100, 2) AS pct_balance_from_churned,
  ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS pct_customers_churned
FROM "Churn";
```

**Finding:** Churned customers make up only 20.37% of total customers, but their combined balances account for 24.26% of the bank's total deposits — a disproportionately high share relative to their headcount.

**Business implication:** The financial impact of churn is understated by the raw churn rate alone. The bank should prioritize retention strategies specifically for high-balance customers, rather than distributing retention resources evenly across all customers.

---

### 4. Geography: Germany Shows Significantly Higher Churn

```sql
SELECT "Geography",
       COUNT(*) AS total_customers,
       SUM("Exited") AS churned_customers,
       ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "Geography";
```

**Finding:** Germany has a churn rate of 32.44%, roughly double that of Spain (16.67%) and France (16.15%).

**Business implication:** This may point to region-specific service issues, competitive pressure, or local market conditions. Further investigation (outside the scope of this dataset) would be needed to confirm the cause.

---

### 5. Gender: Female Customers Churn at a Higher Rate

```sql
SELECT "Gender",
       COUNT(*) AS total_customers,
       SUM("Exited") AS churned_customers,
       ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "Gender";
```

**Finding:** Female customers churn at 25.07%, compared to 16.46% for male customers.

---

### 6. Credit Score: Statistically Significant but Practically Insignificant

```sql
SELECT "Exited",
       COUNT(*) AS n,
       AVG("CreditScore") AS mean_creditscore,
       STDDEV("CreditScore") AS std_creditscore
FROM "Churn"
GROUP BY "Exited";
```

A Welch's two-sample t-test was performed to formally test whether credit score differs between churned and retained customers:

- Retained customers (Exited=0): mean = 651.85, n = 7,963
- Churned customers (Exited=1): mean = 645.35, n = 2,037
- **t ≈ 2.63, p ≈ 0.0086** (statistically significant at α = 0.05)

**Finding:** While the difference is statistically significant, the effect size is very small (only ~6.5 points on a 300–850 scale). Statistical significance does not imply practical importance — this small difference has limited value for real-world retention decision-making, especially compared to the much larger effect sizes seen for product count, activity level, and balance.

**Business implication:** Credit score should not be prioritized as a key driver of churn. Activity level, product holdings, and balance are far more actionable signals.

---

## Predictive Modeling (Python)

The SQL analysis above identifies *which* factors correlate with churn. As a natural extension, a predictive model was built to estimate each customer's probability of churning, so that the bank could proactively flag at-risk customers rather than only observing patterns after the fact.

### Model 1: Logistic Regression

A logistic regression model was trained using scikit-learn (`LogisticRegression`), with categorical variables (`Geography`, `Gender`) one-hot encoded and an 80/20 train-test split.

**Handling class imbalance:** The dataset is imbalanced (~20% churned vs. ~80% retained). Training a baseline model without adjustment resulted in strong overall accuracy but very poor recall on churned customers (recall ≈ 0.21), meaning the model missed the majority of customers who actually churned. Setting `class_weight='balanced'` significantly improved recall to 0.72 (at the default 0.5 threshold), at the cost of lower precision and overall accuracy — a deliberate trade-off, since failing to identify a customer who will churn (a missed retention opportunity) is generally more costly to the bank than mistakenly flagging a loyal customer (a low-cost, unnecessary retention outreach).

### Threshold Analysis

Because failing to catch a churning customer (false negative) is costlier than a false alarm (false positive), the default 0.5 classification threshold was tested against alternative thresholds:

| Threshold | Precision (Churn) | Recall (Churn) | F1 | Accuracy |
|---|---|---|---|---|
| 0.3 | 0.26 | 0.94 | 0.41 | 0.46 |
| 0.4 | 0.31 | 0.85 | 0.45 | 0.59 |
| 0.5 (default) | 0.37 | 0.72 | 0.49 | 0.70 |
| 0.6 | 0.45 | 0.56 | 0.50 | 0.78 |

**Finding:** Lowering the threshold to 0.4 recovers substantially more true churners (recall 0.85 vs. 0.72) at a moderate cost to precision and accuracy, and was selected as a reasonable operating point given the asymmetric cost of missed churners vs. false alarms.

### Model 2: Random Forest (Comparison)

A Random Forest classifier (`RandomForestClassifier`, `n_estimators=100`, `class_weight='balanced'`) was trained on the same data for comparison.

| Model | Threshold | Precision (Churn) | Recall (Churn) | Accuracy |
|---|---|---|---|---|
| Logistic Regression | 0.4 | 0.31 | 0.85 | 0.59 |
| Random Forest | 0.3 | 0.55 | 0.66 | 0.83 |
| Random Forest | 0.5 | 0.78 | 0.45 | 0.87 |

A Precision-Recall curve comparing both models confirmed that Random Forest dominates Logistic Regression across nearly the entire recall range — at any given recall level, Random Forest achieves meaningfully higher precision, indicating it captures the non-linear patterns in the data more effectively. **Random Forest at a 0.3 threshold** was selected as the final model, balancing a strong recall (0.66) with much higher precision (0.55) and accuracy (0.83) than the logistic regression alternative.

### Feature Importance

Logistic regression coefficients highlighted the most influential predictors of churn:

- **IsActiveMember** (strongest predictor): inactive members are markedly more likely to churn — consistent with the SQL finding above.
- **Geography_Germany**: being a German customer is associated with higher churn risk — directly confirming the elevated German churn rate found in the SQL analysis.
- **Gender_Male**: male customers are somewhat less likely to churn than female customers — also consistent with the SQL findings.
- **NumOfProducts**: holding more products is associated with lower churn risk in the linear model, though the SQL analysis shows this relationship breaks down sharply at 3+ products, suggesting a non-linear effect that the Random Forest model is better equipped to capture.

---

## Interactive Dashboard

View the interactive Tableau dashboard here: [Bank Customer Churn Analysis Dashboard](https://public.tableau.com/views/BankCustomerChurnAnalysisDashboard_17841154606870/BankCustomerChurnAnalysisDashboard?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

The dashboard includes:
- **Overall churn rate** (19.65% churned vs. 80.35% retained)
- **Churn rate by geography** (Germany 32.73% vs. France 15.78% and Spain 14.32%)
- **High-risk customer list** — customers flagged by the Random Forest model (threshold 0.3), sorted by predicted churn probability, to support prioritized retention outreach

---

## Summary of Business Recommendations

1. **Investigate product bundling practices** for customers holding 3+ products — the unusually high churn rate suggests a possible cross-selling or product experience issue.
2. **Build an early-warning system** based on customer activity (IsActiveMember) to proactively flag at-risk customers.
3. **Prioritize retention resources for high-balance customers**, since they represent a disproportionate share of the bank's total deposits at risk.
4. **Investigate regional differences**, particularly the elevated churn rate in Germany.
5. Do not over-index on credit score as a churn driver — while statistically detectable, its practical impact is minimal.
6. **Use the Random Forest model (threshold 0.3) to prioritize outreach**, focusing retention efforts on the ~475 customers flagged as high-risk in the Tableau dashboard.

## Limitations & Future Directions

- The dataset does not include specific product types (only a count of products held), limiting the ability to pinpoint which product or combination is driving the high churn among multi-product customers.
- Future analysis could incorporate customer service interaction logs, transaction history, or survey data to better understand the "why" behind these patterns.
- The classification threshold (0.3) was chosen based on the general assumption that missed churners are costlier than false alarms, but this project does not have access to the bank's actual customer acquisition cost, retention outreach cost, or customer lifetime value. In a real deployment, the threshold should be recalibrated using these actual cost figures to minimize total business cost, rather than relying on recall/precision trade-offs alone.
- A predictive model (logistic regression and Random Forest) was built as a natural extension of the descriptive SQL analysis; further improvements could include hyperparameter tuning, additional model types (e.g., XGBoost), and cross-validation.
