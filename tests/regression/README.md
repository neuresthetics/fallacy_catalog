# Regression checks (not blind)

After each round's fixes were applied, the catalog builder re-applied METHOD.md to the earlier test passages that the changes could affect and compared the results with the adjudicated keys. The builder had the keys and the scorer's error lists in view, so these checks are **not blind**. They catch a rule that now points the wrong way, but they are not evidence of accuracy.

- [regression_v050.md](regression_v050.md): v0.5.0 against round-1 and round-2 error, disagreement and "fragile" passages plus 10 random legitimate passages from each set.
- [regression_v060.md](regression_v060.md): v0.6.0 against every round-1, round-2 and round-3 passage whose key or reviewer verdicts name a changed entry, every no-argument passage, all 20 real excerpts, and the passages FIXES.md cites for method rules (159 passages).

Every mismatch found was either fixed in the catalog before commit or is listed in the file as outstanding.
