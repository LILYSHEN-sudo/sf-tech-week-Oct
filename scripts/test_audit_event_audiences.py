import unittest

from audit_event_audiences import audit_row, clean_description, evidence_for


class AudienceAuditTest(unittest.TestCase):
    def row(self, name="", description="", audience="", **fields):
        return {
            "event_id": "example", "name": name, "partiful_description": description,
            "audience_inferred": audience, "themes": "", "tracks": "", "formats": "",
            "primary_host": "", **fields,
        }

    def test_footer_variants_are_removed(self):
        description = "An art show. This event is part of **#SFTechWeek** — a week of events hosted by VCs and startups to bring together the tech ecosystem."
        self.assertNotIn("VCs", clean_description(description))
        self.assertEqual(evidence_for(self.row(description=description)), {})

    def test_time_is_not_product_manager(self):
        self.assertNotIn("PM", evidence_for(self.row(description="Doors open at 6 PM.")))
        self.assertIn("PM", evidence_for(self.row(name="PM Dinner")))

    def test_weak_cue_queued_without_automatic_removal(self):
        record = audit_row(self.row(description="Meet executives from a company.", audience="Founder"), {})
        self.assertEqual(record["weak_only"], "Founder")
        self.assertEqual(record["review_remove"], "Founder")
        self.assertEqual(record["auto_add"], "")

    def test_explicit_title_is_auto_added(self):
        record = audit_row(self.row(name="Creators Meetup"), {})
        self.assertEqual(record["auto_add"], "Creator")

    def test_fundraising_theme_adds_founder_and_investor(self):
        record = audit_row(self.row(themes="AI; Fundraising / Investing"), {})
        self.assertEqual(record["auto_add"], "Founder; Investor")

    def test_hr_hiring_theme_adds_hr(self):
        record = audit_row(self.row(themes="AI; HR / Hiring"), {})
        self.assertEqual(record["auto_add"], "HR")

    def test_manual_override_can_clear_labels(self):
        record = audit_row(self.row(audience="Founder; Investor"), {"example": []})
        self.assertTrue(record["manual_override"])
        self.assertEqual(record["candidate"], "")
        self.assertEqual(record["review_remove"], "Founder; Investor")


if __name__ == "__main__":
    unittest.main()
