# NLTK data: downloading and locating resources

Sources:
- https://www.nltk.org/data.html
- https://www.nltk.org/api/nltk.downloader.html
- https://www.nltk.org/install.html

## Install
- "NLTK requires Python versions 3.9, 3.10, 3.11, 3.12 or 3.13." Install with `pip install -U nltk`. This project pins Python 3.12 on Netlify.
- After installing: "please do install the necessary datasets/models for specific functions to work."

## Download programmatically
- `nltk.download('vader_lexicon')` downloads a single package. Collections such as `'popular'`, `'book'`, `'all-corpora'` and `'all'` also exist, but **don't** download collections for this project.
- `download_dir=` sets a different install target. By default NLTK uses a system-wide directory if writable, otherwise the user's home directory (`Downloader.default_download_dir()`).
- Command line: `python -m nltk.downloader [-d DATADIR] [-q] [-f] [-k] PACKAGE_IDS`, e.g.
  `python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon`
- The downloader first fetches its index from `https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/index.xml` (`Downloader.DEFAULT_URL`). The build therefore needs network access to raw.githubusercontent.com, unless the data is committed.

## Where NLTK looks
- Central locations: `/usr/share/nltk_data` and `/usr/local/share/nltk_data` (Unix/Mac), `C:\nltk_data` (Windows).
- Anywhere else: "you will need to set the `NLTK_DATA` environment variable to specify the location of the data." At runtime you can also add a path with `nltk.data.path.insert(0, "/path/to/nltk_data")`.

## Manual install (used for Pyodide and offline builds)
- Create `nltk_data/` with subfolders such as `corpora`, `sentiment`, `tokenizers`.
- "Download individual packages from https://www.nltk.org/nltk_data/ ... Unzip them to the appropriate subfolder." Example: `.../packages/corpora/brown.zip` goes to `nltk_data/corpora/brown`.
- Package locations for this project:
  - `tokenizers/punkt_tab`
  - `corpora/stopwords`
  - `sentiment/vader_lexicon.zip`. VADER's default `lexicon_file` is `sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt`, so NLTK can read it **without unzipping**.

## Project rules
- The build sets `NLTK_DATA` to a repo folder and runs the downloader **once, quietly**, or the data is committed. Code must never call `nltk.download()` inside analysis functions.
- For Pyodide, the build copies `sentiment/vader_lexicon.zip`, `corpora/stopwords.zip` and `tokenizers/punkt_tab.zip` into `site/nltk_data/`. The worker writes them into Pyodide's virtual filesystem and adds the path with `nltk.data.path.insert(0, "/nltk_data")`. Stopwords and Punkt must be **unzipped** in the virtual filesystem, or read through their zip path. Test both.
