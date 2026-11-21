# D. github.com/pluris — attribution check

Question: does the GitHub account `pluris` belong to the Kaggle user "pluris" (leaderboard rank ~5) and does it host a competition repo?

## Result: nothing found, nothing attributable

Checks run on 2026-11-21 from the sandbox:

| Check | Result |
|---|---|
| `curl https://api.github.com/users/pluris/repos` | **Blocked** by the session proxy: "This GitHub API path is not available: sessions are bound to their configured repositories." The repo list could not be read. |
| `curl https://github.com/pluris?tab=repositories` | HTTP 403 from the proxy. Profile page not readable. |
| `git ls-remote https://github.com/pluris/pluris` | Succeeds (HEAD `edbc24607e42f64067b0de9d5b4f02d04a926710`). So a GitHub account named `pluris` exists and has a public profile repo. |
| `git ls-remote` on 15 guessed names: `gemma-4-developer-agent`, `gemma4-developer-agent`, `kaggle-gemma4-developer-agent`, `gemma-4-agent`, `gemma4-agent`, `kaggle-gemma-4-developer-agent`, `gemma-developer-agent`, `kaggle`, `gemma4`, `gemma-4`, `swe-gemma`, `gemma4-swe-agent`, `gemma-agent`, `gemma-4-dev-agent`, `kaggle-gemma4` | All return "could not read Username" (GitHub's response for a repo that does not exist **or** is private). No public repo under any of these names. |

## What this does and does not establish

- Established: a GitHub account `pluris` exists; none of the 15 guessed repo names is a public repo there.
- Not established: whether that account is the same person as Kaggle "pluris"; whether a competition repo exists under another name or privately. The full repository list could not be enumerated.
- The `pluris/pluris` profile repo was not cloned or read (no evidence it relates to the competition).

**No technique, config or score is attributed to "pluris" anywhere in this research folder.**

## How to close this out manually

- Open `https://github.com/pluris?tab=repositories` in a browser and look for a Gemma/Kaggle repo.
- Open the Kaggle profile `https://www.kaggle.com/pluris` and check for a linked GitHub account, public notebooks or discussion posts for this competition.
