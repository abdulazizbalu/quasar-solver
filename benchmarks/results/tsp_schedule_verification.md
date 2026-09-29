# Historical TSP schedule verification

The default remains `coefficient_scaled_linear`, preserving the schedule used for the published TSP table. This fresh run used the same benchmark design and seeds. Feasibility, objective, and gap were compared run-by-run; measured runtime is included as a diagnostic because it varies with machine load.

| Cities | Solver | Outcomes identical (100 runs) | Published mean runtime | Rerun mean runtime |
| ---: | --- | --- | ---: | ---: |
| 6 | qubo_sa | yes | 0.0424 s | 0.0284 s |
| 6 | qubo_sa_swap | yes | 0.0612 s | 0.0426 s |
| 6 | two_opt | yes | 0.0365 s | 0.0259 s |
| 10 | qubo_sa | yes | 0.1584 s | 0.1445 s |
| 10 | qubo_sa_swap | yes | 0.2173 s | 0.2045 s |
| 10 | two_opt | yes | 0.1282 s | 0.1205 s |
| 15 | qubo_sa | yes | 0.3930 s | 0.3535 s |
| 15 | qubo_sa_swap | yes | 0.5060 s | 0.4741 s |
| 15 | two_opt | yes | 0.3630 s | 0.3384 s |
| 20 | qubo_sa | yes | 0.7410 s | 0.6824 s |
| 20 | qubo_sa_swap | yes | 0.9126 s | 0.8616 s |
| 20 | two_opt | yes | 0.8145 s | 0.7671 s |
