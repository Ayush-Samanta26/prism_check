import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analysis import Evidence, assess, analyze_one, content_terms, numbers_in  # noqa: E402


def ev(text, title="Test", reliability=0.8, hint=None):
    return Evidence("Test", title, "https://example.org", text, reliability=reliability, stance_hint=hint)


class AnalysisTests(unittest.TestCase):
    def test_terms_drop_stopwords(self):
        self.assertIn("water", content_terms("The water boils at 100 degrees"))
        self.assertNotIn("the", content_terms("The water boils"))

    def test_numbers(self):
        self.assertEqual(numbers_in("About 1,000 people and 3.5 cats"), {"1000", "3.5"})

    def test_supports(self):
        a = analyze_one("Water boils at 100 degrees Celsius at sea level",
                        ev("Water boils at 100 degrees Celsius at sea level pressure."))
        self.assertEqual(a.stance, "supports")

    def test_refutation_word(self):
        a = analyze_one("Humans use only ten percent of their brains",
                        ev("The claim that humans use only ten percent of their brains is a myth."))
        self.assertEqual(a.stance, "contradicts")

    def test_number_mismatch(self):
        a = analyze_one("The Eiffel Tower is 500 metres tall",
                        ev("The Eiffel Tower is 330 metres tall including antennas."))
        self.assertEqual(a.stance, "contradicts")

    def test_unrelated(self):
        a = analyze_one("Water boils at 100 degrees", ev("Bananas are rich in potassium and grow in tropical climates."))
        self.assertEqual(a.stance, "unrelated")

    def test_insufficient_when_little_evidence(self):
        r = assess("Water boils at 100 degrees Celsius", [ev("Water boils at 100 degrees Celsius.")])
        self.assertEqual(r["verdict"], "insufficient")

    def test_supported_verdict(self):
        items = [ev("Water boils at 100 degrees Celsius at sea level."),
                 ev("At sea level, water boils at 100 degrees Celsius, a standard reference."),
                 ev("The boiling point of water is 100 degrees Celsius at sea level.")]
        r = assess("Water boils at 100 degrees Celsius at sea level", items)
        self.assertEqual(r["verdict"], "supported")

    def test_contradicted_verdict(self):
        claim = "Vaccines cause autism in children"
        items = [ev("The idea that vaccines cause autism in children is a debunked myth.", reliability=0.9),
                 ev("Large studies found no evidence that vaccines cause autism in children.", reliability=0.9),
                 ev("Claims that vaccines cause autism in children are false and misleading.", reliability=0.9)]
        r = assess(claim, items)
        self.assertEqual(r["verdict"], "contradicted")

    def test_stance_hint(self):
        a = analyze_one("The moon landing was faked",
                        ev("The moon landing was faked. Rated: False.", hint="contradicts", reliability=0.9))
        self.assertEqual(a.stance, "contradicts")


if __name__ == "__main__":
    unittest.main()
