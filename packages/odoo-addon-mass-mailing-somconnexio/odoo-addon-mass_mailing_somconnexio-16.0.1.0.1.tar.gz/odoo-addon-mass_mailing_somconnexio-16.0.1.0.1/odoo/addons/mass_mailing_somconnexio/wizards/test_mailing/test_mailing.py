from odoo import fields, models, api


class TestMassMailing(models.TransientModel):
    _inherit = "mailing.mailing.test"
    partner_email_to = fields.Many2one(
        "res.partner", "Test Partner", domain=[("mass_mailing_contacts_count", ">", 0)]
    )

    @api.onchange("partner_email_to")
    def _onchange_partner_email_to(self):
        """Set the email_to field based on the selected partner."""
        if self.partner_email_to:
            self.email_to = self.partner_email_to.email
        else:
            self.email_to = ""
