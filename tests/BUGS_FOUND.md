# Critical Bugs Found in Financial Calculations

## Summary
Edge case testing revealed **5 critical bugs** in the core financial calculation functions that affect accuracy.

## Bug #1: Fractional Months Calculation Uses Wrong Month
**Function:** `fractional_months_between()`
**Issue:** Uses destination month for day calculation instead of source month
**Impact:** Incorrect time period calculations

```python
# Current buggy logic:
_, days_in_month = calendar.monthrange(current_recording_date.year, current_recording_date.month)
return months + (days / days_in_month)

# Example bug:
# Jan 31 -> Feb 28: Should be ~0.9 months, but calculates as 1.0 months
# Uses February (28 days) instead of January (31 days) for fraction
```

## Bug #2: Far Future Dates Return Zero
**Function:** `budgeted_spending_between_dates()`
**Issue:** Logic flaw in date range comparison
**Impact:** No spending calculated for long time periods

```python
# Current logic only includes budgets that START within the date range
if start_date <= budget_start < end_date:
    # This excludes budgets that start before the range but should apply throughout

# Example:
# Budget starts 2024-04-07, request 2024-04-07 to 2074-04-07
# Budget qualifies but fractional_months_between(2024-04-07, 2074-04-07) creates huge result
# But actual result is 0.0 - suggesting deeper logic error
```

## Bug #3: Multiple Budget Periods Incorrect Logic
**Function:** `budgeted_spending_between_dates()`
**Issue:** Doesn't handle multiple budget periods correctly
**Impact:** Wrong spending calculations when budgets change

```python
# Expected: Feb 1 - May 1 with budgets starting Jan 1 and Mar 1
# Should calculate:
# - Feb 1 to Mar 1: budget1 (1 month) = 905.89
# - Mar 1 to May 1: budget2 (2 months) = 1358.335 * 2
# Total expected: 3622.56

# Actual result: 2717.67 (much lower)
```

## Bug #4: Income Calculation Wrong Month Logic
**Function:** `income_between_dates()`
**Issue:** Uses simple year/month arithmetic instead of proper date arithmetic
**Impact:** Incorrect income calculations over time periods

```python
# Current buggy logic:
months = (cropped_end.year - cropped_start.year) * 12 + (cropped_end.month - cropped_start.month)

# This ignores day-level precision and uses integer months only
# Should use fractional_months_between() for consistency
```

## Bug #5: Multiple Income Periods Wrong Calculation
**Function:** `income_between_dates()`
**Issue:** Combination of Bug #4 + wrong period logic
**Impact:** Massive over-calculation of income

```python
# Expected: 5 months @ 3291.39 + 7 months @ 3949.67 = 44,104.63
# Actual: 67,144.36 (52% over-calculation!)
```

## Root Cause Analysis

### Core Issue 1: Inconsistent Date Arithmetic
- `budgeted_spending_between_dates()` uses `fractional_months_between()`
- `income_between_dates()` uses simple integer month arithmetic
- This creates inconsistencies between spending and income calculations

### Core Issue 2: Range Logic Errors
Both functions use `start_date <= budget_start < end_date` which:
- Excludes budgets that start before the requested range but should apply
- Doesn't properly handle budget transitions within the range

### Core Issue 3: Month Fraction Calculation
`fractional_months_between()` uses the wrong month for day calculations, affecting all downstream calculations.

## Severity Assessment
- **CRITICAL**: All financial analysis results are incorrect
- **CRITICAL**: Predictions and balance analysis are unreliable
- **CRITICAL**: Dashboard displays wrong financial data

## Next Steps
1. Fix `fractional_months_between()` to use correct month for fractions
2. Rewrite budget/income date range logic to handle overlapping periods
3. Make income calculation consistent with spending calculation
4. Verify all fixes with comprehensive edge case tests
5. Test with real-world data to ensure accuracy