"""Check edge cases against known answers, as well as implementation agreement."""
import contextlib
import csv
import io
import tempfile
import unittest
from pathlib import Path
from pure_python_stats import summarize, numeric_stats
from pandas_stats import summarize as pandas_summary
from compare_results import compare

class StatisticsTests(unittest.TestCase):
    def test_known_numeric_answers(self):
        s = numeric_stats([0, 2, 4])
        self.assertEqual(s["mean"], 2)
        self.assertEqual(s["median"], 2)
        self.assertEqual(s["std"], 2)
        self.assertIsNone(numeric_stats([5])["std"])
        self.assertIsNone(numeric_stats([])["mean"])

    def test_missing_invalid_ties_ids_and_cleaning(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.csv"
            with path.open("w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["amount", "empty", "single", "mixed", "label", "ad_id", "zeros"])
                writer.writerows([
                    ["$1,000", "", "7", "4", "b", "001", "0"],
                    ["(200)", "NA", "", "oops", "a", "002", "0"],
                    ["0", "null", "", "", "a", "003", "0"],
                    ["N/A", "NaN", "", "", "b", "004", "0"]])
            a = summarize(path)
            with contextlib.redirect_stdout(io.StringIO()):
                b = pandas_summary(path)
            compare(a, b)
            c = a["columns"]
            self.assertAlmostEqual(c["amount"]["mean"], 800 / 3)
            self.assertEqual(c["amount"]["median"], 0)
            self.assertEqual(c["empty"]["missing"], 4)
            self.assertIsNone(c["single"]["std"])
            self.assertEqual(c["mixed"]["type"], "categorical")
            self.assertEqual(c["label"]["mode"], "a")
            self.assertEqual(c["ad_id"]["type"], "categorical")
            self.assertEqual(c["zeros"]["std"], 0)

if __name__ == "__main__":
    unittest.main()
