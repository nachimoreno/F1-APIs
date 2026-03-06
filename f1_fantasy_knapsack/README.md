# Knapsack Problem Solver for F1 Fantasy

A solver for the official F1 Fantasy game based on Knapsack Problem theory. Given the rule change for 2026, driver and constructor performance will initially be estimated based on ceratin priors, and then updated as more data becomes available.

## Initial priors

- Driver:
  - 60%: multi-year quali performance vs teammates (normalized)
  - 20%: multi-year race consistency / incident avoidance
  - 20%: early FP/quali signal (when available)
  
- Constructor:
  - 50%: last season end-of-year pace rank (last ~6 races)
  - 30%: organizational strength proxy (reliability + pit/strategy rating)
  - 20%: preseason testing/early FP pace rank
