# Git, review and merge flow

Sources:
- https://docs.github.com/en/get-started/using-github/github-flow
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
- https://git-scm.com/docs/git-merge
- https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/how-credits-work.md

## GitHub flow (docs steps)
1. **Create a branch** for each unit of work.
2. **Make changes**: commit small, coherent changes.
3. **Create a pull request** describing the change.
4. **Address review comments.**
5. **Merge your pull request.**
6. **Delete your branch.**

## Review decisions (GitHub)
| Decision | Meaning |
|---|---|
| Comment | "Leaves general feedback without explicitly approving or requesting changes." |
| Approve | "Signals that the changes are ready to merge." |
| Request changes | "Flags feedback that the author should address before merging." |

## Project rules
- One branch and one PR per task, e.g. `feat/spacy-layer`. Each PR gets a **free Netlify Deploy Preview**, which qa-engineer tests.
- Merging to `main` (production) costs **15 credits per production deploy**, and the Free plan has 300 credits a month. **Batch merges at milestones.**
- Prefer merge commits or squash merges. Never rewrite shared history. `git merge --no-ff` keeps a visible merge commit for each feature (git-merge docs: "With `--no-ff`, create a merge commit in all cases, even when the merge could instead be resolved as a fast-forward.").
- Merge gate: QA green (pytest, schema checks, Playwright on the Deploy Preview) **and** the owning agent's definition of done met.
