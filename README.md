# Junsheng Fu's personal website

A responsive, dependency-free static academic homepage. The published page needs
no JavaScript, API, external fonts, or build service. Open `index.html` directly
in a browser. Original project assets are retained.

## Add news

Edit `_data/news.json` and add an entry:

```json
{
	"date": "2026-10",
	"text": "Your update goes here.",
	"url": "https://example.com/your-paper"
}
```

- `date`: `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`. Only use known date precision.
- The page displays these as `2026`, `Oct 2026`, or `Oct 7, 2026`, respectively.
- `text`: plain text, not HTML.
- `url`: optional complete HTTP or HTTPS link. Omit the field for unlinked news.
- Separate entries with commas; JSON does not allow trailing commas.
- Entries are sorted newest first. Equal dates retain their order in the file.
	Year-only entries sort as January 1; this is a sorting convention, not a claim
	about the actual event date.
- The first five entries are visible; older entries use a native All news
	disclosure, which also works without JavaScript.

From this directory, regenerate the page with Python 3.9 or newer:

```sh
python3 build.py
```

Then publish the updated `index.html` together with the site's assets. On a
static hosting service such as GitHub Pages, no Python runtime is needed by
visitors. This folder contains a Git repository; deployment has not been changed
or automated by this redesign.

## Edit the page

- `_templates/index.html`: biography, research, publications, talks, and layout.
- `_data/news.json`: news content.
- `assets/css/home.css`: responsive styles.
- `build.py`: validates news and writes `index.html`.

Edit the template rather than the generated `index.html`, then run the build.
Paper venue/year labels and initial news come from the October 7, 2026 CV;
precise event dates and direct paper links should be added when confirmed.
Images use local compressed previews; below-the-fold images load lazily.
Full-size originals are unchanged.

## Validate

```sh
python3 -m unittest -v test_build
python3 build.py --check
```

The tests cover dates, ordering, escaping, URL validation, and News disclosure.
Check mode detects a generated page that no longer matches its source.
