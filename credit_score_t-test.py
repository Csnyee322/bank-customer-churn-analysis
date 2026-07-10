"""
Credit Score vs. Customer Churn — Hypothesis Test
===================================================
Question: Does credit score actually differ between churned and retained
customers, or does it just look similar by coincidence?

We use Welch's two-sample t-test (does not assume equal variances),
based on summary statistics pulled directly from PostgreSQL:

    SELECT "Exited", COUNT(*) AS n,
           AVG("CreditScore") AS mean_creditscore,
           STDDEV("CreditScore") AS std_creditscore
    FROM "Churn"
    GROUP BY "Exited";

Requirements:
    pip install scipy
"""

from scipy import stats

# Summary statistics pulled from the SQL query above
n0, mean0, sd0 = 7963, 651.85, 95.65   # Retained customers (Exited = 0)
n1, mean1, sd1 = 2037, 645.35, 100.32  # Churned customers  (Exited = 1)

# Welch's t-test (equal_var=False), computed directly from summary stats
t_stat, p_value = stats.ttest_ind_from_stats(
    mean1=mean0, std1=sd0, nobs1=n0,
    mean2=mean1, std2=sd1, nobs2=n1,
    equal_var=False
)

print(f"t-statistic: {t_stat:.4f}")
print(f"p-value:     {p_value:.4f}")

alpha = 0.05
if p_value < alpha:
    print(f"\nResult: Statistically significant at alpha = {alpha}.")
    print("The difference in mean credit scores between the two groups")
    print("is unlikely to be due to random chance.")
else:
    print(f"\nResult: Not statistically significant at alpha = {alpha}.")

print("\nNote: Statistical significance does not imply practical")
print("importance. The observed difference (~6.5 points on a 300-850")
print("scale) is small, and credit score should not be treated as a")
print("primary driver of churn compared to activity level, product")
print("count, or balance.")


# =====================================================================
# Expected output:
#
# t-statistic: 2.6340
# p-value:     0.0086
#
# Result: Statistically significant at alpha = 0.05.
# The difference in mean credit scores between the two groups
# is unlikely to be due to random chance.
#
# Note: Statistical significance does not imply practical
# importance. The observed difference (~6.5 points on a 300-850
# scale) is small, and credit score should not be treated as a
# primary driver of churn compared to activity level, product
# count, or balance.
# =====================================================================
