import unittest

from build import news_date, render_news


class NewsTests(unittest.TestCase):
    def test_date_precision(self):
        self.assertEqual(news_date("2026")[1], "2026")
        self.assertEqual(news_date("2026-10")[1], "Oct 2026")
        self.assertEqual(news_date("2026-10-07")[1], "Oct 7, 2026")

    def test_invalid_dates(self):
        for value in (None, "2026-13", "2025-02-29", "26", "2026-1", "0000"):
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                news_date(value)

    def test_sorting_and_same_date_order(self):
        result = render_news([
            {"date": "2024", "text": "Older"},
            {"date": "2026", "text": "First"},
            {"date": "2026", "text": "Second"},
            {"date": "2026-10", "text": "Newest"},
        ])
        self.assertLess(result.index("Newest"), result.index("First"))
        self.assertLess(result.index("First"), result.index("Second"))
        self.assertLess(result.index("Second"), result.index("Older"))

    def test_archive_and_escaping(self):
        result = render_news([{"date": "2026", "text": "<script>&"}] * 6)
        self.assertEqual(result.count("<li>"), 6)
        self.assertEqual(result.split("<details")[0].count("<li>"), 5)
        self.assertIn("&lt;script&gt;&amp;", result)
        self.assertIn("<summary>", result)

    def test_url_validation(self):
        for url in ("javascript:alert(1)", "/relative", "https://", 123, "https://bad host"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                render_news([{"date": "2026", "text": "News", "url": url}])
        self.assertIn('href="https://example.com/?a=1&amp;b=2"', render_news([
            {"date": "2026", "text": "News", "url": "https://example.com/?a=1&b=2"}
        ]))

    def test_partial_news_link(self):
        result = render_news([{
            "date": "2026-09",
            "text": "At the ECCV WMEAI Workshop: keynote.",
            "url": "https://example.com/workshop",
            "link_text": "WMEAI Workshop",
        }])
        self.assertIn(
            'At the ECCV <a href="https://example.com/workshop">WMEAI Workshop</a>: keynote.',
            result,
        )
        for text, news_text in (
            ("missing", "WMEAI Workshop"),
            ("WMEAI Workshop", "WMEAI Workshop and WMEAI Workshop"),
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                render_news([{
                    "date": "2026",
                    "text": news_text,
                    "url": "https://example.com/workshop",
                    "link_text": text,
                }])
        with self.assertRaises(ValueError):
            render_news([{
                "date": "2026",
                "text": "WMEAI Workshop",
                "link_text": "WMEAI Workshop",
            }])

    def test_empty_and_invalid_content(self):
        self.assertIn("Updates coming soon", render_news([]))
        self.assertNotIn("<details", render_news([{"date": "2026", "text": "News"}]))
        for items in ({}, [None], [{"date": "2026", "text": " "}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                render_news(items)


if __name__ == "__main__":
    unittest.main()