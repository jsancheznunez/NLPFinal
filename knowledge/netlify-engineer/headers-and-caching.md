# Headers and caching

Sources:
- https://docs.netlify.com/manage/routing/headers.md
- https://docs.netlify.com/build/caching/caching-overview.md

## Declaring headers
- Two ways: a plain-text `_headers` file "to the publish directory of your site", or `[[headers]]` in `netlify.toml`:
  ```toml
  [[headers]]
    for = "/*"
    [headers.values]
      X-Frame-Options = "DENY"
  ```
- Multi-value headers can be written as a TOML multi-line string. Netlify collapses them into one header.
- Paths: "Wildcards (`*`) can be used at any place inside of a path segment... Placeholders (`:placeholders`) can only be used at the start of a path segment." The two can't be in the same segment.
- "the headers are global for all builds and cannot be scoped for specific branches or deploy contexts", unless you use the documented workaround of copying a context-specific `_headers` file during the build.
- These headers apply to **static CDN responses**, which is everything this project serves.

## Project header plan
| Path | Header | Why |
|---|---|---|
| `/data/*` | `Cache-Control: public, max-age=3600` | JSON changes only per deploy |
| `/nltk_data/*` | `Cache-Control: public, max-age=604800` | NLTK zips change rarely |
| `/py/*` | `Cache-Control: public, max-age=3600` | `nltk_layer.py` for Pyodide |
| `/*` | `X-Content-Type-Options: nosniff` | basic hardening |
- **No cross-origin-isolation headers are needed.** Basic single-threaded Pyodide works without `Cross-Origin-Opener-Policy`/`Embedder-Policy`. Adding COEP could block the jsDelivr CDN script unless it sends CORP headers, so leave them out.
- Netlify's CDN invalidates its cache on every deploy (caching overview), so a long `max-age` mainly affects browser caching. Keep the JSON's `max-age` short so viewers see new deploys quickly.
