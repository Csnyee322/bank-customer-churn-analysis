-- =====================================================================
-- Bank Customer Churn Analysis
-- Data source: Kaggle - Bank Customer Churn Prediction (10,000 rows)
-- Tool: PostgreSQL (pgAdmin 4)
-- =====================================================================


-- =====================================================================
-- SETUP: Table creation
-- =====================================================================

CREATE TABLE "Churn" (
    "RowNumber" INT,
    "CustomerId" BIGINT,
    "Surname" VARCHAR(50),
    "CreditScore" INT,
    "Geography" VARCHAR(20),
    "Gender" VARCHAR(10),
    "Age" INT,
    "Tenure" INT,
    "Balance" NUMERIC(20,2),
    "NumOfProducts" INT,
    "HasCrCard" INT,
    "IsActiveMember" INT,
    "EstimatedSalary" NUMERIC(20,2),
    "Exited" INT
);


-- =====================================================================
-- QUESTION 1: What is the overall churn rate?
-- =====================================================================

SELECT
    COUNT(*) AS total_customers,
    SUM("Exited") AS churned_customers,
    ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn";

-- Finding: The overall churn rate is 20.37%, i.e. roughly 1 in every 5
-- customers has churned.


-- =====================================================================
-- QUESTION 2: Which customer characteristics are most related to churn?
-- =====================================================================

-- 2a. Gender
SELECT
    "Gender",
    COUNT(*) AS total_customers,
    SUM("Exited") AS churned_customers,
    ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "Gender";

-- Finding: Female customers churn at 25.07%, compared to 16.46% for male
-- customers.


-- 2b. Geography
SELECT
    "Geography",
    COUNT(*) AS total_customers,
    SUM("Exited") AS churned_customers,
    ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "Geography";

-- Finding: Germany has the highest churn rate (32.44%), roughly double
-- that of Spain (16.67%) and France (16.15%).


-- 2c. Activity level (IsActiveMember)
SELECT
    "IsActiveMember",
    COUNT(*) AS total_customers,
    SUM("Exited") AS churned_customers,
    ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "IsActiveMember";

-- Finding: Inactive customers churn at 26.85%, vs. 14.27% for active
-- customers - nearly double the risk.


-- 2d. Number of products held
SELECT
    "NumOfProducts",
    COUNT(*) AS total_customers,
    SUM("Exited") AS churned_customers,
    ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS churn_rate_pct
FROM "Churn"
GROUP BY "NumOfProducts"
ORDER BY "NumOfProducts" DESC;

-- Finding: Customers holding 1-2 products churn at 7.58%-27.71%, but
-- those holding 3-4 products churn at 82.71%-100%, despite smaller
-- sample sizes (266 and 60 customers). Likely linked to product
-- bundling / cross-selling issues.


-- 2e. Balance - the financial impact of churn
SELECT
    "Exited",
    COUNT(*) AS total_customers,
    AVG("Balance") AS avg_balance
FROM "Churn"
GROUP BY "Exited";

SELECT
    ROUND(SUM(CASE WHEN "Exited" = 1 THEN "Balance" ELSE 0 END)
        / SUM("Balance") * 100, 2) AS pct_balance_from_churned,
    ROUND(SUM("Exited")::numeric / COUNT(*) * 100, 2) AS pct_customers_churned
FROM "Churn";

-- Finding: Churned customers make up 20.37% of customers by headcount,
-- but 24.26% of total deposits - churn skews toward higher-balance
-- customers.


-- =====================================================================
-- QUESTION 3: Is credit score actually related to churn?
-- (Follow-up hypothesis test, since the average credit scores looked
-- similar between the two groups)
-- =====================================================================

SELECT
    "Exited",
    COUNT(*) AS n,
    AVG("CreditScore") AS mean_creditscore,
    STDDEV("CreditScore") AS std_creditscore
FROM "Churn"
GROUP BY "Exited";

-- A Welch's two-sample t-test was run on these summary statistics
-- (see python/credit_score_ttest.py for the calculation):
--   Retained (Exited=0): mean = 651.85, n = 7,963
--   Churned  (Exited=1): mean = 645.35, n = 2,037
--   t ~ 2.63, p ~ 0.0086 (statistically significant at alpha = 0.05)
--
-- Finding: Statistically significant, but the effect size (~6.5 points
-- on a 300-850 scale) is too small to be practically useful for
-- retention decisions. Statistical significance != practical importance.
