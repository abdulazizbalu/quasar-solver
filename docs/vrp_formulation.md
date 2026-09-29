# Tiny CVRP QUBO

The QUBO supports integer-distance CVRP with exactly two available vehicles and at most six customers. This is a small comparison model, not a general VRP solver. It has one binary variable `x[v,t,i]` for each vehicle `v`, tour slot `t` (one slot per customer), and item `i` (depot/empty marker 0 or a customer). There are `2m(m+1)` slot variables for `m` customers. Each vehicle also gets `ceil(log2(capacity+1))` binary slack variables, for a total of `2m(m+1) + 2ceil(log2(capacity+1))` bits. The implementation refuses more than 100 bits.

The objective sums depot-to-first, adjacent-slot, and last-to-depot distances. An empty slot is node 0, so trailing empty slots add zero travel. The penalties are:

- `(sum_i x[v,t,i] - 1)^2`: one item per slot.
- `(sum_v,t x[v,t,i] - 1)^2` for each customer: exactly one visit.
- `x[v,t,0] * x[v,t+1,i]` for `i>0`: no customer after an empty slot.
- `(sum_t,i demand[i] x[v,t,i] + binary_slack[v] - capacity)^2`: load at most capacity. Slack is nonnegative and can represent every integer from zero through capacity.

The default penalty is `4 * m * max_distance`. It exceeds the maximum possible travel cost in these tiny models, but the annealer can still return infeasible states. Squared-penalty constants are omitted from the QUBO matrix; `build_cvrp_qubo` returns the offset needed to compare a feasible QUBO energy with its route distance. The bit-flip annealer starts from arbitrary binary states. Feasibility is checked independently after decoding, and infeasible runs have no route objective or gap.

The standard CVRPLIB files use TSPLIB `EUC_2D` integer rounding. Solomon travel times and distances are truncated to one decimal, matching the cited 25-customer reference. OR-Tools uses these values as integer tenths. It also applies a large fixed vehicle cost to prioritize fleet size before distance. A solution is independently checked against the parsed time windows.
