import odoo.tests

from odoo.addons.mail.tests.common import mail_new_test_user


@odoo.tests.tagged("-at_install", "post_install")
class TestCrowdfundingPortal(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        self.portal_user = mail_new_test_user(
            self.env,
            login="portal_test",
            groups="base.group_portal",
            name="Portal Test User",
            notification_type="email",
        )
        self.portal_user.password = self.portal_user.login
        self.demo_challenge = self.env.ref("crowdfunding.demo_challenge")
        self.challenge = self.env["crowdfunding.challenge"].create(
            {
                "name": "Test Challenge",
                "description": "A test crowdfunding challenge",
                "target_amount": 10000,
            }
        )
        self.challenge.action_open()

    def _pledge_challenge(self, challenge, partner, amount=100):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "crowdfunding_challenge_id": challenge.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Pledge for Test Challenge",
                            "price_unit": amount,
                            "quantity": 1,
                        },
                    )
                ],
            }
        )
        invoice.action_post()

    def test_portal_pledge_access(self):
        self.authenticate("portal_test", "portal_test")
        response = self.url_open("/my/crowdfunding")
        self.assertEqual(response.status_code, 200)

        self.assertNotIn("Test Challenge", response.text)

        self._pledge_challenge(
            challenge=self.challenge, partner=self.portal_user.partner_id
        )

        # Verify challenge is now visible in portal after pledging
        response = self.url_open("/my/crowdfunding")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Challenge", response.text)

        # Test portal access with authentication to specific challenge
        response = self.url_open(f"/my/crowdfunding/{self.challenge.id}")
        self.assertEqual(response.status_code, 200)

    def test_website_access(self):
        # Test anonymous access to website
        self.authenticate("portal_test", "portal_test")

        # Test that challenges are visible on the website without authentication
        response = self.url_open("/crowdfunding")

        # Parse response to verify challenge is listed on the website
        self.assertIn(self.demo_challenge.name, response.text)
        self.assertIn(self.challenge.name, response.text)

        response = self.url_open("/my/crowdfunding")
        self.assertNotIn(self.demo_challenge.name, response.text)
        self.assertNotIn(self.challenge.name, response.text)

        self._pledge_challenge(self.challenge, partner=self.portal_user.partner_id)
        response = self.url_open("/my/crowdfunding")
        self.assertIn(self.challenge.name, response.text)
        self.assertNotIn(self.demo_challenge.name, response.text)

        self.challenge.is_published = False

        response = self.url_open("/crowdfunding")
        self.assertIn(self.demo_challenge.name, response.text)
        self.assertNotIn(self.challenge.name, response.text)

        response = self.url_open("/my/crowdfunding")
        self.assertIn(self.challenge.name, response.text)
        self.assertNotIn(self.demo_challenge.name, response.text)
