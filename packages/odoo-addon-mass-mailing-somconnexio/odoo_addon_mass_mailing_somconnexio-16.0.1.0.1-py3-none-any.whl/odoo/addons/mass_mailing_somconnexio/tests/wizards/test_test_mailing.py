import odoo
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class TestMassMailingTestCase(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.mailing_mailing = self.env["mailing.mailing"].create(
            {
                "name": "A",
                "subject": "test",
            }
        )
        self.partner = self.env.ref("somconnexio.res_partner_1_demo")

    def test_mailing_test(self):
        """Test the mailing test wizard."""
        wizard = self.env["mailing.mailing.test"].create(
            {
                "mass_mailing_id": self.mailing_mailing.id,
                "partner_email_to": self.partner.id,
            }
        )
        wizard._onchange_partner_email_to()
        self.assertEqual(wizard.email_to, self.partner.email)
