# Deploys, Deploy Previews and credits

Sources:
- https://docs.netlify.com/deploy/deploy-types/deploy-previews.md
- https://docs.netlify.com/deploy/deploy-overview.md
- https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/how-credits-work.md

## Deploy Previews
- "By default, Netlify automatically builds Deploy Previews when you... open pull / merge requests in a connected site repository from GitHub..."
- "The base branch must either be a production branch, or a branch that has branch deploys enabled."
- URL: the prefix `deploy-preview` plus the PR number, e.g. `deploy-preview-42--<site>.netlify.app`. "While the initial deploy... is pending, this URL will result in a `Not Found` error." Later pushes update it.
- "Every deploy also has a permalink that starts with the deploy ID number... The contents of this URL never change." Use permalinks in the report and in QA records.
- A Deploy Preview status appears on the PR. With deploy notifications enabled, Netlify also comments the preview link.

## Credits (credit-based plans; all new accounts since Sept 4, 2025)
| Plan | Monthly credits |
|---|---|
| Free | **300**, a hard limit ("all of your web projects... are paused" when they run out) |
| Personal | 1,000 (can buy more) |
| Pro | from 3,000 |

| Usage | Credit cost |
|---|---|
| **Production deploys** | **15 credits each** ("build minutes no longer calculated") |
| **Deploy Previews or branch deploys** | **0 credits** |
| Compute (functions etc.) | 10 credits per GB-hour (we use none) |
| Bandwidth | 20 credits per GB |
| Web requests | 2 credits per 10,000 requests |

## Project deploy policy
- Free plan: 300 / 15 = **at most 20 production deploys a month** before counting bandwidth. **Merge to the production branch only at milestones.** Do all iteration on PRs, where Deploy Previews are free.
- Pyodide is loaded from jsDelivr, so its roughly 10 MB download doesn't count against our bandwidth. Our own `site/` (JSON, zips, HTML) does. Keep `site/data` small: aim for under 5 MB in total.

## Skipping a deploy (saves 15 credits for test- or docs-only commits)
Source: https://docs.netlify.com/deploy/manage-deploys/manage-deploys-overview.md
- "To avoid generating a branch or production deploy for a commit pushed directly to a branch, add `[skip ci]` or `[skip netlify]` anywhere in the Git commit message."
- For several commits pushed together, put it in the most recent commit: "it will apply to all other commits in the push."
- "The next commit pushed without one of those messages will trigger a new branch deploy or production deploy, including all changes from the skipped commits as well."
- For PRs, put `[skip ci]` or `[skip netlify]` in the PR title to skip its Deploy Preview.

## Pretty URLs (observed on the live site, Nov 2026)
Netlify's asset post-processing ("Pretty URLs") rewrites internal links on deploy, e.g. `href="resources.html"` becomes `href='/resources'`. Both URLs return 200. Tests that select links must accept both forms (see `RES_LINK` in tests/e2e/test_site.py).
