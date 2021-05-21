### TODOS for future

0. General code cleanup.  Also we need to incorporate some scripts Mayank and I wrote.
- updated
1. Instead of sending all N-1 seeds, generate the seeds in a tree and send only the log(N) seeds necessary to recreate those N-1 seeds without recreating the last seed.  (We discussed this last week.)
- updated
2. For (current) rounds 1, 3, 5: we can send only a single commitment rather than sending one commitment per repetition.  (We discussed this last week.)
- updated, not tested
3. We don't actually need rounds 4+5; the alphas can be checked alongside the zetas.
- updated
4. We do not need to send the Zeta or output shares (assuming V knows what the output is supposed to be); the verifier can plug these into the commitment and check them herself.  (We discussed this last week.  This was the thing where instead of revealing N-1 shares of Zeta (say the shares are a, b, c), we instead commit to H(a||b||c) in round 1 or 3; in round 5 when the verifier reconstructs (say) a and b, it can compute c = 0-a-b and then check if H(a||b||(0-a-b)) matches the hash from before.)
- updated 75%
5. Changes made in section 3.4 of paper Mayank and I edited this weekend.  TL;DR: We can actually skip the alphas entirely by replacing them with something we called... betas (creative, I know).  This ends up allowing us to get to sending 2 field elements per mult gate per rep instead of 3 (but we pay for it by sending #parties per rep shares of this "beta" thing later)
- written, needs to be tested, dependent on #4 
6. Instead of having N parties + an offset, we can have N-1 parties' shares generated pseudorandomly, and have the Nth party's share be the offset.  This means if the verifier chooses not to corrupt party N, we don't have to send the offsets at all, for an expected savings of 1/N.
