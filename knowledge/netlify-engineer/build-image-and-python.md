# Build image and Python on Netlify

Sources:
- https://docs.netlify.com/build/configure-builds/available-software-at-build-time.md
- https://docs.netlify.com/build/configure-builds/manage-dependencies.md

## Build image
- "Our current build is based on Ubuntu version 24.04 (also called Noble Numbat)."
- Python: default `3.x`. Available: "Any official Python version". Set the version with "Build environment variable `PYTHON_VERSION`, `Pipfile` file, or `runtime.txt` file". pip "Corresponds with the installed Python version." Pipenv is also available.
- Node.js default `24`. The build can also run Node if needed (it isn't needed here).

## Choosing the Python version (manage-dependencies)
- "Set a `PYTHON_VERSION` environment variable."
- or "Add a `runtime.txt` file to the site's base directory... The file must include the version number _only_: `x.y`, with no trailing newline."
- or use a Pipenv `Pipfile`.
- "If the site's base directory includes both a `runtime.txt` file and a `Pipfile`, Netlify will use the version specified in `runtime.txt`."
- **Project choice:** `PYTHON_VERSION = "3.12"` in `[build.environment]` of `netlify.toml`. That's one place, it's visible in review, and NLTK and spaCy both support it (NLTK: 3.9–3.13; spaCy 3.8.x: >=3.10).

## Python dependencies are installed automatically
- "If your build requires any Python dependencies, you must provide a list of these for installation using pip or Pipenv."
- `pip freeze > requirements.txt` "creates a `requirements.txt` file that Netlify will use to install your dependencies by running `pip install`."
- "If the site's base directory includes both a `requirements.txt` file and a `Pipfile`, Netlify will run `pip install` to install the dependencies in `requirements.txt`, and ignore the dependencies in the `Pipfile`."
- ⇒ **The build command doesn't need to run `pip install -r requirements.txt` itself.** Netlify runs it before the build command when `requirements.txt` is in the base directory. Running it again just costs time. The command can be `python scripts/build_analysis.py`. Check the order in the deploy log on the first Deploy Preview.

## Dependency cache
- "After the initial build, we'll cache the dependencies so we don't have to install them every time you push an update."
- "If you change your dependency requirements, the next build will re-run the installation command... It isn't guaranteed a change will take place if the previous dependencies still satisfy the installer."
- "If a build fails, it's worth retrying with a cleared build cache." Use **Deploys → Trigger deploy → Clear cache and deploy site**.
- Pin exact versions (`nltk==3.9.4`, `spacy==3.8.x`, the model wheel URL) so cached and fresh builds behave the same.
