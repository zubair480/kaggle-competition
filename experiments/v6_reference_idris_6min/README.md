# v6 candidate: the published 0.24 bundle with a 6-minute cap (not submitted)

`research/competitor_repositories/idris_v24/v24/` (Apache-2.0, MUHAMMED IDRIS BIN YACOOB) with two changes:
`max_time_minutes` 8 -> 6 and the same number in the prompt's budget sentence. Purpose: a reference point on
the leaderboard from a configuration with a known 0.24 draw, without the 8-minute runtime risk.
Worst case for 120 tasks at 6 minutes plus overhead is about 13 hours, so this relies on most tasks finishing
early; our measured mean at a 5-minute cap was 217 s.
