# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import http
from odoo.http import request


class CrowdfundingController(http.Controller):
    @http.route(
        ["/crowdfunding", "/crowdfunding/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
    )
    def list(self, page=1):
        values = self._list_render_context(page)
        return request.render("crowdfunding.template_challenge_list", values)

    def _list_render_context(self, page):
        website = request.website
        CrowdfundingChallenge = request.env["crowdfunding.challenge"]
        domain = (
            request.env.user._is_public()
            and CrowdfundingChallenge._domain_website_access()
            or CrowdfundingChallenge._domain_portal_access()
        )
        result_count = CrowdfundingChallenge.search_count(domain)
        step = 5
        pager = website.pager(
            url="/crowdfunding",
            total=result_count,
            page=page,
            step=step,
            scope=5,
        )

        results = CrowdfundingChallenge.search(
            domain,
            offset=pager["offset"],
            limit=step,
        )

        return {
            "results": results,
            "pager": pager,
        }

    @http.route(
        ["/crowdfunding/<model('crowdfunding.challenge'):challenge>"],
        type="http",
        auth="public",
        website=True,
    )
    def detail(self, challenge):
        values = self._detail_render_context(challenge)
        return request.render("crowdfunding.template_challenge_website", values)

    def _detail_render_context(self, challenge, **kwargs):
        payment_access_token = None
        return {
            "object": challenge,
            "main_object": challenge,
            "payment_access_token": payment_access_token,
        }
