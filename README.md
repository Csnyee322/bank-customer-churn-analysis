# Bank Customer Churn Analysis (SQL)

## Project Background

This project analyzes a U.S. bank's customer dataset to understand the key factors driving customer churn — i.e., which customers are leaving the bank and why. The goal is to identify actionable patterns that could help the bank design more effective customer retention strategies.

## Data Description

- **Data source:** [Kaggle – Bank Customer Churn Prediction](https://www.kaggle.com/datasets)
- **Rows:** 10,000 customers
- **Key fields:** CustomerId, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited (churn flag)

## Tools Used

- **PostgreSQL (pgAdmin 4)** — data storage, cleaning, and analysis
- **Excel / Python (scipy)** — statistical hypothesis testing (t-test)

---

## Key Findings

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

## Summary of Business Recommendations

1. **Investigate product bundling practices** for customers holding 3+ products — the unusually high churn rate suggests a possible cross-selling or product experience issue.
2. **Build an early-warning system** based on customer activity (IsActiveMember) to proactively flag at-risk customers.
3. **Prioritize retention resources for high-balance customers**, since they represent a disproportionate share of the bank's total deposits at risk.
4. **Investigate regional differences**, particularly the elevated churn rate in Germany.
5. Do not over-index on credit score as a churn driver — while statistically detectable, its practical impact is minimal.

## Limitations & Future Directions

- The dataset does not include specific product types (only a count of products held), limiting the ability to pinpoint which product or combination is driving the high churn among multi-product customers.
- Future analysis could incorporate customer service interaction logs, transaction history, or survey data to better understand the "why" behind these patterns.
- A predictive model (e.g., logistic regression or classification tree) could be built as a natural extension of this descriptive analysis.
