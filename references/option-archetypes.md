# Making options structurally different

When the user wants N options, vary these **axes**, one or two per option, never only the palette.
Name each option by its idea ("Ledger", "Gauge", "Timeline"), not "Option 3".

| Axis | Variants |
|---|---|
| Information hierarchy | one hero number / ranked list / small multiples / timeline / map |
| Navigation model | tabs / sidebar / command palette / single scroll / drawer / paged stepper |
| Interaction model | persistent / appears on trigger / expands in place / opens beside / modal |
| Density | glanceable (1-2 facts) / working (6-10 facts) / expert (tabular) |
| Metaphor | ledger, instrument gauge, notebook, terminal, receipt, schedule, switchboard, map |
| Layout axis | horizontal strip / vertical stack / radial / grid with one dominant cell / split pane |
| Input | pointer-first / keyboard-first / touch-first / voice or hotkey-only |
| Data encoding | numbers / bars / rings / sparklines / heat strips / text sentences |

Rules:
1. Every option differs on at least two axes from every other option.
2. Every option gets the same required states (idle, active, one edge case) so they compare fairly.
3. Each option gets one line: the idea, what it optimises, what it costs.
4. One option is the "boring but safest" reading of the reference. One is the boldest. Recommend one.
5. A palette swap of option A is not option B. Use `palette.py` once per concept family, not per option,
   unless the concept itself differs.
