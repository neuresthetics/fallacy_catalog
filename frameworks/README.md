# frameworks/

Sourced reference material that sits alongside the fallacy list but is not part of it.

## mindspace.json

A sourced reference on the MINDSPACE behavioural-influence framework: Dolan, Hallsworth, Halpern, King & Vlaev (2010), *MINDSPACE: Influencing behaviour through public policy* (Cabinet Office / Institute for Government). The nine element definitions and the examples are quoted from the full report, with page numbers.

The catalog uses it to **detect and openly name persuasion levers** (messenger, norms, defaults, affect and so on) in a text. A lever being present is not a fallacy. MINDSPACE entries are kept separate from `fallacies.json` and are not scored as fallacies. Where an obvious one exists, each element lists the related catalog entries.

The file also covers related frameworks (nudge, EAST, BIT, MINDSPACE X), the report's own guidance on permission and transparency, the ethics debate, replication evidence, and how MINDSPACE is used across the neuresthetics repos.

### Not part of the audit method
MINDSPACE is a contained, separate analysis. It is not part of `METHOD.md`, and fallacy audits never load or cite this file. A MINDSPACE pass runs only on request, writes its own output, and never changes a fallacy verdict. Blind fallacy reviewers do not see MINDSPACE material.

### Earlier covert use in the neuresthetics repos
Some older neuresthetics repos applied MINDSPACE covertly, for example the Steel Men Collider "AutoNudge" block. These were experiments, published on purpose to show how the framework was learned. They are not current practice, and this catalog uses MINDSPACE only to detect and openly name levers.

### Known gaps
- No publication titled "Mindspace and beyond" could be found. MINDSPACE X (2025) is the closest follow-up.
- The full texts of Dolan et al. 2012 and Hausman & Welch 2010 weren't accessible. They are cited from Crossref metadata only.
- The studies in the report's endnotes weren't individually re-verified.
- Evidence status is assessed only for Priming (weak), Defaults (meta-analytic support) and Norms (small at scale). The other elements are marked "not assessed".
- Several DOI links block automated fetching (403) but resolve for normal browsers. Their metadata was checked via Crossref.
