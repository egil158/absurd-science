# They Published What? — The Replication Archive

An English-language collection of curious and contested published empirical findings. The default catalog view is a cross-disciplinary editorial Top 20. Inclusion does not imply a finding failed replication.

## Source of truth: CSV files

Each `data/*.csv` contains one field. Existing subfields and topics are preserved. Each discipline has a maximum of 1,000 entries. All files use the same columns, in this order:

```
field,sub,topic,headline,title,venue,year,url,note,featured_rank
```

- `field`, `sub`, `topic`, `headline`, `title`, `venue`, `year`, `url`, and `note` are required.
- `featured_rank`: blank for a regular entry; a unique integer 1–20 across all files for the front-page selection. To swap ranks, edit both entries before building. The featured category is generated, never duplicated.
- Add an entire discipline by creating a new CSV with the same header and a unique `field` name. The build detects it automatically. Save as UTF-8 CSV. Quote commas, quotes and line breaks using normal CSV rules.
- The build checks required fields, URL formats, duplicate source URLs, field consistency, a 1,000-entry limit per discipline, and duplicate ranks. It does not verify bibliographic facts or replication claims.

## Editing options

1. **Local**: open any CSV in Excel, VS Code, or Python and save it back to `data/`.
2. **Web editor**: open `editor.html`, choose a published category or load a local CSV, edit/add/delete entries, then export the CSV. Replace the matching file under `data/` and commit. The editor runs entirely in the browser and cannot directly save to the repository. Offline mode supports local CSV uploads.
3. **GitHub website**: edit or upload CSV files directly under `data/`, then commit the changes. With the Actions deployment below, the site will rebuild automatically.

## Publish with GitHub Pages (recommended, automatic rebuild)

Commit all files in this folder, including `.github/workflows/pages.yml`, to the root of the repository on `main`. In **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**. Push to `main` or manually run **Build and deploy archive** from the Actions tab. Future CSV changes trigger deployment without editing HTML or manually running Python.

## Local preview or branch-based deployment

Run `python build.py` (Python 3, standard library only). This regenerates `index.html` and `data/manifest.json`. Open `index.html` directly for offline browsing. To load published CSVs in the editor locally, use `python -m http.server 8000` and open `http://localhost:8000/editor.html`; alternatively open a local CSV in the editor.

If you prefer **Deploy from a branch**, select `main` / `(root)` in Pages settings and commit the rebuilt `index.html` and `data/manifest.json` after changing CSVs. The GitHub Actions workflow is intended for the GitHub Actions Pages source; remove or disable it if using branch deployment.

## Notes and editorial scope

The current archive excludes explicitly methodological demonstrations, deliberately satirical papers, and selected follow-up or review papers. It focuses on original empirical research with unusual claims or interpretations. The Top 20 is editorial, not a ranking of research validity. Inclusion is not a determination that a paper failed replication. Added records were checked against publication pages or bibliographic/abstract records, not systematically against full text; inherited records were not comprehensively reverified. The public page displays only clickable editorial headlines and journal names, with filters by discipline, subfield, topic and keyword. All matching entries are displayed as a compact list. Original titles, years and notes remain in the CSV/editor. All data remain in the CSV files. The 1,000-entry limit is a technical capacity, not a claim about the current number of curated cases.

## Minimal list edition

This edition retains the inherited 196 records and adds 69 candidate entries identified through publication or bibliographic search results (subject to deduplication). Added entries are not fully audited against full texts, and the inherited entries have not been reverified. The requested target of more than 100 entries per discipline has not been reached; do not interpret the counts as a complete survey.

## Bulk discovery edition

The archive now contains 303 records, including 38 additions from publication or bibliographic search results. The additions are not a full-text audit, and the 265 inherited records have not been reverified. The target of 400–500 curated original studies in each field has not been met.

To discover a larger pool on your own internet-connected computer, run:

```bash
python collect_candidates.py --limit 500
```

Or run one field at a time, for example `python collect_candidates.py --field neuroscience --limit 500`. The script uses the public Crossref API, not an AI API. It searches multiple topical queries and deduplicates normalized titles and DOI strings, retaining only records with basic bibliographic fields. It saves **unreviewed** metadata to `candidates/`, separate from `data/`. These files are deliberately excluded from the deployed website. The limit is a cap, not a guaranteed number of eligible original studies. Search matches can be irrelevant, negative, reviews, or demonstrations despite automated filtering. Title/DOI matching cannot catch every duplicate. The live network operation could not be tested in the development environment; local metadata processing and the website build were tested.

Read the original abstract, confirm that the claim is interesting, exclude deliberate methodological demonstrations and inappropriate entries, then fill in the editorial `headline` and `note`. Copy reviewed rows into the corresponding `data/` CSV using the original 10 columns only (omit `decision` and `query`). Rebuild with `python build.py`. Do not bulk-publish the unreviewed search output.

## Neuroscience expansion (2026-11-25)

Neuroscience expanded from 54 to 126 entries; the five other discipline CSV files and featured rankings are unchanged. The additional entries were selected from original publication records, PubMed abstracts, and bibliographies of relevant reviews and papers, not from random generated references. The bibliographic sources include https://pmc.ncbi.nlm.nih.gov/articles/PMC9856603/ (neuroforecasting), https://pmc.ncbi.nlm.nih.gov/articles/PMC13527413/ (neurotheology), and https://pmc.ncbi.nlm.nih.gov/articles/PMC9291242/ (political neuroscience). Links lead to DOI, publisher, or PubMed/PMC records for the original papers. Bibliography-derived entries have not all been individually checked against the original abstract or full text; the archive does not assert that all listed studies have failed replication. The requested 400–500 Neuroscience entries have not yet been reached. The optional collector is unchanged; network access is required to use it.

## Neuroscience expansion, round 2

Neuroscience now has 186 records (60 newly added in this round), with the other five CSV files and Top 20 unchanged. New records link to individual publication pages or PubMed/PMC records identified in bibliographic and abstract searches. Inclusion reflects editorial interest in unusual claims, not verified replication failure. The new records have not been systematically audited against full text; older records have not been comprehensively reverified. Normalized titles and source URLs were checked for duplicates. The 400–500 target remains unmet.
