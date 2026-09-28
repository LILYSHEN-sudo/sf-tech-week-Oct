import unittest

from infer_event_intents import classify, infer


class IntentRulesTest(unittest.TestCase):
    def event(self, name="", description="", formats="", tracks="", themes=""):
        return {"name": name, "partiful_description": description, "formats": formats, "tracks": tracks, "themes": themes}

    def test_boilerplate_does_not_add_goals(self):
        row = self.event("Coffee", "This event is a part of #SF TechWeek—a week of events hosted by VCs and startups. Learn more at www.tech-week.com")
        self.assertEqual(infer(row), set())

    def test_content_after_boilerplate_is_preserved(self):
        row = self.event("AI in XR", "This event is a part of #SFTechWeek. Learn more at www.tech-week.com\nJoin a panel and Q&A on XR.")
        self.assertEqual(infer(row), {"Learning"})

    def test_footer_without_url(self):
        row = self.event("Quiet morning", "This event is part of #SFTechWeek, a week of events hosted by VCs and startups to bring together the tech ecosystem.\nJoin a panel on XR.")
        self.assertEqual(infer(row), {"Learning"})

    def test_multiple_explicit_opportunities(self):
        row = self.event("Matched by NEXA", "Meet your next investor, customer, or hire.", "Matchmaking")
        self.assertEqual(infer(row), {"Funding", "Networking", "Consumer", "Hiring"})

    def test_building_requires_participation(self):
        self.assertEqual(infer(self.event("How to build agents", "A panel about architecture.", "Panel / Fireside Chat")), {"Learning"})
        self.assertEqual(infer(self.event("Agent lab", "Build your own agent during the hands-on workshop.")), {"Building"})

    def test_demo_without_investor_access_is_not_funding(self):
        row = self.event("Demos After Dark", "Five teams demo, no investor poker faces. Stay for the happy hour.", "Pitch Event / Demo Day")
        self.assertEqual(infer(row), {"Learning", "Networking"})

    def test_topic_alone_does_not_imply_consumer_without_mapped_theme(self):
        self.assertEqual(infer(self.event("GTM Strategy", "A panel about sales strategy.", "Panel / Fireside Chat")), {"Learning"})

    def test_founder_investor_breakfast(self):
        self.assertEqual(infer(self.event("Founders & Investors Breakfast")), {"Funding", "Networking"})

    def test_fundraising_track_adds_funding(self):
        row = self.event("Quiet session", tracks="Enterprise AI; Fundraising & Investing")
        self.assertEqual(infer(row), {"Funding"})

    def test_fundraising_theme_adds_funding(self):
        self.assertEqual(infer(self.event("Quiet session", themes="AI; Fundraising / Investing")), {"Funding"})

    def test_breakfast_format_adds_networking(self):
        row = self.event("Quiet session", formats="Breakfast, Brunch or Lunch; Panel / Fireside Chat")
        self.assertEqual(infer(row), {"Networking", "Learning"})

    def test_unlabeled_event_defaults_to_networking(self):
        self.assertEqual(classify(self.event("Unspecified event")), {"Networking"})
        self.assertEqual(classify(self.event("Panel", formats="Panel / Fireside Chat")), {"Learning"})

    def test_live_entertainment_can_overlap_networking(self):
        row = self.event("AI Karaoke", "Sing with us, then meet other guests.", "Networking; Experiential")
        self.assertEqual(infer(row), {"Networking", "Entertainment"})

    def test_entertainment_preserves_networking_fallback(self):
        self.assertEqual(classify(self.event("Murder Mystery")), {"Networking", "Entertainment"})

    def test_other_entertainment_examples(self):
        for name in ("Comedy Show", "DJ Set", "Murder Mystery", "Mahjong Night", "Poker Tournament"):
            with self.subTest(name=name):
                self.assertIn("Entertainment", infer(self.event(name)))

    def test_entertainment_theme_or_experiential_format_alone_is_not_enough(self):
        row = self.event("Media Industry Panel", "A talk about the entertainment business.", "Panel / Fireside Chat")
        self.assertEqual(infer(row), {"Learning"})
        self.assertEqual(infer(self.event("Lab Tour", formats="Experiential")), set())

    def test_media_theme_adds_entertainment(self):
        row = self.event("Industry Panel", formats="Panel / Fireside Chat", themes="AI; Media / Entertainment")
        self.assertEqual(infer(row), {"Learning", "Entertainment"})

    def test_gaming_and_ar_vr_themes_add_entertainment(self):
        for theme in ("Gaming", "AR / VR"):
            with self.subTest(theme=theme):
                self.assertIn("Entertainment", infer(self.event("Quiet session", themes=theme)))

    def test_consumer_theme_and_customer_opportunity_share_one_label(self):
        row = self.event("Consumer Gathering", themes="B2C / Consumer")
        self.assertEqual(infer(row), {"Consumer"})
        self.assertEqual(classify(row), {"Networking", "Consumer"})
        self.assertEqual(infer(self.event("Meet your next customer")), {"Consumer"})

    def test_both_themes_preserve_other_intents(self):
        row = self.event("Meet customers", themes="B2C / Consumer; Media / Entertainment")
        self.assertEqual(infer(row), {"Consumer", "Entertainment"})

    def test_poker_faces_is_not_entertainment(self):
        row = self.event("Demo Day", "No investor poker faces.", "Pitch Event / Demo Day")
        self.assertNotIn("Entertainment", infer(row))

    def test_performance_metrics_and_unrelated_poker_promo_are_not_entertainment(self):
        row = self.event("Hardware Demo", "See live performance metrics on our amplifiers.")
        self.assertNotIn("Entertainment", infer(row))
        row = self.event("Investor Session", "A discussion with investors. " + "Details. " * 210 + "Another event: Poker Night.")
        self.assertNotIn("Entertainment", infer(row))


if __name__ == "__main__":
    unittest.main()
