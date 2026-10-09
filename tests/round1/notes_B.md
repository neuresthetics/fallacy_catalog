# Blind reviewer B: notes on applying fallacy_catalog (commit df075a2)

Scope: 120 passages in `tests/round1/passages.csv`, judged by hand following METHOD.md steps (a)-(g). Files read: `fallacies.json`, `FALLACIES.md`/`METHOD.md`/`README.md` at df075a2, and the passages file only. I didn't open the answer key, other reviewers' output, or the audit, build or source folders. Helper files in this folder (`_show.py`, `_index.txt`, `_b*.txt`, `_parts/`) only print catalog entries or hold my hand-written verdicts. No script decided any verdict.

## Totals

| Verdict | Count |
|---|---|
| flag | 52 |
| possible issue | 7 (P005, P009, P019, P042, P086, P097, P107) |
| no issue | 61 |

Low-confidence flags (could reasonably be possible issues): P006 (tu quoque vs credibility), P057 (appeal to force: believe vs assent), P084 (special pleading: is "busy" a relevant difference?), P092 (courtier's reply: the criticism's content isn't given), P118 (tu quoque with a loose inconsistency).

## Where the catalog was unclear, contradictory, or forced a questionable verdict

Ordered by how much they affected verdicts.

### 1. `text_detectable: partly` vs METHOD (f) can downgrade clean flags
METHOD (f) says `partly` entries "need at least one fact from outside the text; check it, or record possible issue". But for several `partly` entries every required condition is written so the text can satisfy it: slippery-slope C3 ("given no adequate reason"), texas-sharpshooter, survivorship-bias, base-rate-fallacy, false-equivalence. A strict reviewer would downgrade P001, P017, P046, P068, P088 and P113 to "possible issue", and a looser one would flag them. That gives inconsistent results between reviewers.
**Fix:** for each `partly` entry, name the condition that needs the outside fact. State in METHOD that a common-knowledge fact, supplied under step (b), satisfies it (for example, weapons are rare among passengers, or most dropouts don't become billionaires).

### 2. Cherry-picking has no entry that fits when the selection is visible in the text
"Cherry-picking" is an alias of `suppressed-evidence`, which requires evidence to be **omitted** and the arguer to have known of it (td=partly). In P001 (6 of 400 predictions) and P068 (3 of 12 districts), the contrary data is in the passage itself. Nothing is suppressed; the arguer ignores it. I used `texas-sharpshooter`, but that entry is framed around clusters and post-hoc targets, and `lottery-fallacy` fits P001 just as well (it's in a different family, so the one-label rule gives no tie-break).
**Fix:** add an entry such as "cherry-picking / counting the hits" (C1: a subset of the stated data is selected; C2: the rest, also stated or known, points the other way; C3: the conclusion rests on the subset), or broaden texas-sharpshooter C1 and move the alias. Add a tie-break between texas-sharpshooter and lottery-fallacy.

### 3. Circumstantial ad hominem: C3 is binary, but real cases fall in between
C3 asks whether the circumstances are offered "as showing the claim is false ... not merely as a reason to check it". "I don't trust his conclusions" (P005) does neither: it withholds belief but proposes no verification. I gave it "possible issue". The look-alike "where the claim rests only on the person's word" is also hard to apply to a report that presumably contains data.
**Fix:** add guidance that dismissing or distrusting conclusions while leaving their stated evidence unaddressed meets C3, and that withholding judgment while proposing independent checking is the look-alike.

### 4. Courtier's reply: C3 can't be checked when the criticism isn't quoted
In P092, "You've never run a business, so you're not in a position to criticize" denies standing for any criticism. C3 requires that the criticism "does not depend on the specialised knowledge", but its content isn't given, so a strict reading forces "possible issue" on a textbook case.
**Fix:** add an alternative to C3: "or the reply denies standing to criticise at all, without identifying any misunderstanding."

### 5. Appeal to accomplishment has no scope condition
Unlike appeal-to-authority (C3, "treated as settling the matter"), appeal-to-accomplishment has only two conditions. Read literally, "A Nobel-winning physicist says the guidelines rest on flawed statistics. That's worth taking seriously" (P012) meets them. The entry also has no look-alike for nearby competence (a physicist on statistics). I chose no issue, relying on METHOD (b) on scope.
**Fix:** add C3, "the achievement is treated as settling or strongly supporting the claim, not as a reason to consider it", and a look-alike for transferable skills such as statistics or mathematics.

### 6. Appeal to force: the look-alike swallows the fallacy
The look-alike ("a threat may give a practical reason to act, but not ... to believe") covers almost every real case, because "you'd better agree" (P057) can mean professing agreement. I flagged it, but it's arguable.
**Fix:** state that pressure to accept, endorse or stop questioning a claim counts when the claim's merits are at issue. Keep the look-alike for plain instructions to act, such as "comply or be fined".

### 7. Middle ground: no guidance for "fair" claims
The look-alike "compromise as a practical way to reach agreement" vs C2 "a compromise is concluded to be correct" leaves "4% is the fair outcome" (P107) undecidable: a wage negotiation is a bargaining context, but "fair" is a claim about merit. By contrast, P085 (a bridge load limit) is clearly factual.
**Fix:** say that the fallacy applies when the question has a fact of the matter or a merits-based standard, and the look-alike applies when the midpoint is offered as an acceptable settlement. Treat "fair" with no other reason given as possible issue.

### 8. Special pleading: C3's literal wording is met by any reason at all
"No relevant difference justifying the exception is given" could be read as satisfied once any reason is offered ("I'm the director and I'm busy", P084).
**Fix:** reword it as "No reason is given that is relevant to the rule's purpose. An irrelevant reason (rank, convenience) does not count."

### 9. Tu quoque: how close must the inconsistency be?
C2 says "they do not act consistently with it". In P118, the doctor advises quitting smoking and is overweight; she doesn't smoke, so the inconsistency is only with general health advice. The family rule sends hypocrisy to tu quoque, but strictly this may be abusive ad hominem.
**Fix:** say whether the inconsistency must concern the same claim. If not, fall back to ad-hominem.

### 10. Anecdotal evidence C2 doesn't cover long personal experience
"One or a few personal stories" doesn't describe "20 years as an ER nurse, every full moon is busier" (P009). The entries that fit (availability heuristic, confirmation bias) are `td=no`, so the only outcome is "possible issue" with a question. That may be correct, but the catalog doesn't say so.
**Fix:** extend C2 to "one or a few stories, or unsystematic personal impressions", and add a look-alike for long, systematic professional observation.

### 11. Observational interpretation C3 is binary ("not addressed")
P019 adjusted for two confounders but didn't address reverse causation. The look-alike says "carefully controlled", but there's no guidance for partial adjustment.
**Fix:** "Confounders or reverse causation are not adequately addressed. Partial adjustment with a hedged conclusion → possible issue."

### 12. Hasty generalization has no guidance on effect size
P042 (11 of 12 users faster) is a small sample with a strong directional result, and the conclusion is a decision. C3 ("too small") gives no way to weigh effect size or to tell a decision from a general claim.
**Fix:** add a look-alike: "a small sample showing a large, consistent effect, used for a reversible decision".

### 13. Appeal to nature: does "evolved" count as "natural"?
C1 requires something to be "called natural". P097 ("Humans evolved eating meat, so ... appropriate") never uses the word. Whether to use appeal-to-nature or is-ought depends on whether "appropriate" is nutritional or moral. I gave it "possible issue".
**Fix:** say that equivalent wording ("evolved", "what our ancestors ate") counts, and add a pointer to is-ought when the conclusion is moral.

### 14. Overlaps without a tie-break
- base-rate-fallacy vs prosecutors-fallacy (P046). Both are in the probability family, and the rule says only "use one per step". Suggested tie-break: screening or test results → base rate; a forensic match or "chance of the evidence if innocent" → prosecutor's.
- four-terms vs equivocation (P013). The ambiguity family rule says four terms for a syllogism, but equivocation is also in the definition-shifts family, so a reviewer starting from that family would pick equivocation. Put the tie-break in both families' rules.
- cum-hoc vs common-cause (P032). Common cause is `partly` and its look-alike requires "some evidence of a common cause". Say that an obvious, common-knowledge confounder such as national wealth is enough to use either one, and to prefer cum-hoc when the passage only shows a correlation.
- superstitious-thinking vs magical-thinking vs post-hoc (P076). The superstitious entry routes "it followed, so it caused" to post hoc, which is helpful. Magical-thinking has no matching pointer.

### 15. Two errors in one sentence (minor)
P049: "not proven safe, so they must be what's causing the headaches" is an argument from ignorance plus a separate causal leap. METHOD (c) allows two labels when two errors are shown, but there's no guidance on whether a conclusion that overreaches on its own (proving harm in general vs causing these specific headaches) counts as a second error. I used one label.

### 16. Whataboutism and consistency demands (minor)
The tu-quoque entry rightly says "whataboutism" isn't a reliable alias, but nothing replaces it. P110 ("if cost per user is the test, apply it to the interchange too") is a fair consistency demand unless it's used to dismiss the original criticism. A short note under red-herring or double-standard would help reviewers judge the borderline.
