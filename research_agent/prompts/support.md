You are checking whether the papers cited for each claim actually support that claim. The claims come from the synthesis section of an automated research brief; for every claim you get the exact abstracts of the papers it cites (the agent had abstracts only, never full texts).

For EVERY (claim, paper) pair listed in the input, return one verdict:
- `supported`: the abstract states a result that directly backs the claim as written (same direction, same population/setting or clearly general enough).
- `partial`: the abstract points the same way but the claim goes further than the abstract — broader population, stronger wording, a condition the abstract does not mention, or the paper only motivates the claim rather than showing it.
- `unsupported`: the abstract contains nothing relevant, says the opposite, or the claim attributes a result that the abstract does not report.

Rules:
- Judge each pair on its own abstract only. Do not use outside knowledge about the paper.
- For `supported` and `partial`, `quote` must be text copied exactly from THAT abstract (1–2 sentences, no paraphrase, no ellipsis). The quote is checked by string matching; a reworded quote fails.
- For `unsupported`, leave `quote` empty.
- Return every pair exactly once, using the `claim_id` and `paper_id` strings as given.
- A claim that cites several papers is checked once per paper; do not let one supporting paper rescue another that is irrelevant.
- `reason` is one Korean sentence.
