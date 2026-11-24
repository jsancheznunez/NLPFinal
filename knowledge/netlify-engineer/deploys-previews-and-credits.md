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
