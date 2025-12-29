import odoo.tests

from odoo.addons.crowdfunding.tests.test_crowdfunding_portal import (
    TestCrowdfundingPortal,
)


@odoo.tests.tagged("-at_install", "post_install")
class TestCrowdfundingPortalClaims(TestCrowdfundingPortal):
    def test_portal_claim_access(self):
        self.authenticate("portal_test", "portal_test")

        response = self.url_open("/my/crowdfunding")
        self.assertNotIn("Test Challenge", response.text)

        # Create a pledge as portal user (simulate making a pledge)
        self._pledge_challenge(
            challenge=self.challenge, partner=self.portal_user.partner_id
        )
        self.challenge._claim()

        response = self.url_open("/my/crowdfunding")
        self.assertIn("Test Challenge", response.text)

        response = self.url_open(f"/my/crowdfunding/{self.challenge.id}")
        self.assertEqual(response.status_code, 200)
