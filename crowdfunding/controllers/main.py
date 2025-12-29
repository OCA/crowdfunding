# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import http
from odoo.http import request


class CrowdfundingController(http.Controller):
    _step = 10
    _scope = 10

    @http.route(
        [
            "/crowdfunding",
            "/crowdfunding/page/<int:page>",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def list(self, page=1, filterby=False, **searchvals):
        values = self._list_render_context(page, filterby, searchvals)
        return request.render("crowdfunding.template_challenge_list", values)

    def _list_render_context(self, page, filterby=False, searchvals=None):
        website = request.website
        CrowdfundingChallenge = request.env["crowdfunding.challenge"]
        searchbar_filters = CrowdfundingChallenge._searchbar_filters()

        domain = CrowdfundingChallenge._domain_website_access()

        url_args = {}
        if filterby and filterby != "all":
            domain.append(searchbar_filters.get(filterby, {}).get("domain", [])[0])
            url_args["filterby"] = filterby

        if searchvals.get("search"):
            domain.append(["name", "ilike", searchvals["search"]])
            url_args["search"] = searchvals["search"]

        result_count = CrowdfundingChallenge.search_count(domain)
        pager = website.pager(
            url="/crowdfunding",
            total=result_count,
            page=page,
            step=self._step,
            scope=self._scope,
            url_args=url_args,
        )

        results = CrowdfundingChallenge.search(
            domain,
            offset=pager["offset"],
            limit=self._step,
        )

        # Reusing searchbar_filters for the portal view,
        # but manipulating to ensure this works when rendering
        # website templates
        filters = []
        for x in searchbar_filters:
            searchbar_filters[x]["key"] = x
            filters.append(searchbar_filters[x])

        return {
            "results": results,
            "pager": pager,
            "filters": filters,
            "request": request,
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
