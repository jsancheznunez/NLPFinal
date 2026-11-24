# Knowledge: netlify-engineer

Reference notes from the official Netlify docs (docs.netlify.com, Markdown versions, read Nov 2026). Read this index first.

| File | Covers | Main sources |
|---|---|---|
| [build-image-and-python.md](build-image-and-python.md) | Ubuntu 24.04 image, Python version pinning, automatic `pip install`, dependency cache | …/available-software-at-build-time.md, …/manage-dependencies.md |
| [build-settings-and-netlify-toml.md](build-settings-and-netlify-toml.md) | Base, publish and command settings; `netlify.toml`; deploy contexts; `ignore` | …/configure-builds/overview.md, …/file-based-configuration.md, …/ignore-builds.md |
| [headers-and-caching.md](headers-and-caching.md) | `[[headers]]`, `_headers`, Cache-Control | …/manage/routing/headers.md, …/caching-overview.md |
| [deploys-previews-and-credits.md](deploys-previews-and-credits.md) | Deploy Previews, permalinks, credit costs per plan | …/deploy-previews.md, …/how-credits-work.md |
| [functions-and-env-vars.md](functions-and-env-vars.md) | Why we use no Functions; environment variable scopes | …/functions/overview.md, …/environment-variables/overview.md |

Project context: [docs/04-netlify-deployment.md](../../docs/04-netlify-deployment.md). Shared with `build-pipeline-engineer`.
