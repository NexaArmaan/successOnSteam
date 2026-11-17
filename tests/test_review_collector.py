import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import collect_individual_reviews as collector


class TestReviewCollector(unittest.TestCase):
    def test_extract_review(self):
        data = {"recommendationid": "123", "voted_up": False,
                "review": "Played a lot; do not recommend.",
                "author": {"playtime_at_review": 7500, "playtime_forever": 8000}}
        row = collector.extract_review(620, data)
        self.assertEqual(row["appid"], 620)
        self.assertEqual(row["playtime_at_review_min"], 7500)
        self.assertFalse(row["voted_up"])
        self.assertEqual(row["recommendationid"], "123")

    @patch.object(collector.time, "sleep", return_value=None)
    @patch.object(collector, "request_page")
    def test_collect_two_pages_and_skip_duplicate(self, request_page, sleep):
        first = {"reviews": [{"recommendationid": "a", "author": {"playtime_at_review": 10}},
                              {"recommendationid": "b", "author": {"playtime_at_review": 30}}],
                 "cursor": "page2"}
        second = {"reviews": [{"recommendationid": "b", "author": {"playtime_at_review": 30}},
                               {"recommendationid": "c", "author": {"playtime_at_review": 50}}],
                  "cursor": "page3"}
        third = {"reviews": [], "cursor": "page3"}
        request_page.side_effect = [first, second, third]
        rows = collector.collect_game(620, 5, 0)
        self.assertEqual(len(rows), 3)
        self.assertEqual([row["recommendationid"] for row in rows], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
