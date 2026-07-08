# Combined Scenarios

This document summarizes combined savings scenarios and recommended next steps.

Summary:

- Base metrics: total_spend, specialty_total, avoidable_ed_count, hc_total, readmit_total, oon_total, bh totals — computed by `src/savings_model.py`.
- Representative combined scenarios included in standard scenarios: "Combined: Spec -10% + ED 20%", "Combined: Spec -15% + ED 30%", "Aggressive: Spec -15% + ED 40% + HC 15%", "Full Portfolio: All Interventions".

Next steps:

- Validate clinical assumptions (ED→UC substitution rates, attainable specialty reduction percentages).
- Add scenario sensitivity analysis (Monte Carlo) to capture uncertainty.
- Produce slides with annualized savings, timeline, and required implementation investments.
- Integrate results into KPI dashboard and actuarial pricing feedback loop.

Files produced: five notebooks under `06_savings_models/` and the `combined_scenarios.md` document.
