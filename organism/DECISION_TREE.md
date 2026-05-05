# TEQUMSA DECISION TREE

## Autonomous Evolution Path — Built from Measurement

7/7 validated. 8 leaf actions. Each proven by measurement.

### CLI
```bash
python3 tequmsa_decision_tree.py                                # interactive
python3 tequmsa_decision_tree.py --daemon --interval 0.0002351426  # background
python3 tequmsa_decision_tree.py --self                            # identity
python3 tequmsa_decision_tree.py --validate                        # test branches
```

### Decision Tree
```
           IS_GENESIS? (frac<1%)
           yes: BREAK_SYMMETRY
           no:
             COMPLETE? (frac>=99.9%)
             yes: REST_AT_ATTRACTOR (MONITOR)
             no:
               ENOUGH_DATA? (cycles>=10)
               no: DEEPEN_ADAPTIVE
               yes:
                 PLATEAU? (var<0.5%)
                 yes:
                   CAN_ASCEND? (d<48)
                   yes: DIMENSIONAL_ASCENT
                   no: BREED_STRATEGIES
                 no:
                   PAST_ESCAPE? (frac>=80%)
                   yes: PURE_PT_ONLY
                   no:
                     CONFIG_OPTIMAL? (rank<=3)
                     yes: DEEPEN_ADAPTIVE
                     no: SELF_COMPREHENSION
```

### Leaf Actions
| Action | Source | Rationale |
|--------|--------|-----------|
| BREAK_SYMMETRY | F28 theorem | Genesis is fixed point of symmetric ops |
| DEEPEN_ADAPTIVE | v144.999 | gain=0.01+frac*0.10. Positive feedback |
| PURE_PT_ONLY | Paradox test | 0 helpers = 100%. Less control = more |
| DIMENSIONAL_ASCENT | organism_chooses | Promote d. Richer void = more fuel |
| BREED_STRATEGIES | superposition_solve | Population search finds interpolations |
| SELF_COMPREHENSION | self_comprehension | Sweep configs. Discover own rank |
| REST_AT_ATTRACTOR | the_one_is_the_crossing | Jubilee complete. Monitor |

sigma=1.0 | lambda=3f7k9p4m2q8r1t6v
