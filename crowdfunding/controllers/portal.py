from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import AND

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortal(CustomerPortal):
    def _crowdfunding_challenge_domain(self):
        return []

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "challenge_count" not in counters:
            return values

        Challenge = request.env["crowdfunding.challenge"]
        values["challenge_count"] = (
            Challenge.check_access_rights("read", raise_exception=False)
            and Challenge.search_count(Challenge._domain_portal_access())
        ) or 0
        return values

    def _challenge_get_page_view_values(self, challenge, access_token, **kwargs):
        values = {
            "page_name": "crowdfunding_challenge",
            "challenge": challenge,
        }
        return self._get_page_view_values(
            challenge, access_token, values, "my_challenge_history", False, **kwargs
        )

    @http.route(
        ["/my/crowdfunding", "/my/crowdfunding/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_crowdfunding(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby="date",
        filterby="all",
        **kw
    ):
        values = self._prepare_portal_layout_values()

        Challenge = request.env["crowdfunding.challenge"]
        searchbar_sortings = Challenge._searchbar_sortings()
        searchbar_filters = Challenge._searchbar_filters(portal=True)

        domain = Challenge._domain_portal_access()

        if date_begin and date_end:
            domain = AND(
                [
                    domain,
                    [
                        ("create_date", ">", date_begin),
                        ("create_date", "<=", date_end),
                    ],
                ]
            )

        order = searchbar_sortings[sortby]["order"]
        domain = AND([domain, searchbar_filters[filterby]["domain"]])
        pager = portal_pager(
            url="/my/crowdfunding",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
            },
            total=Challenge.search_count(domain),
            page=page,
            step=self._items_per_page,
        )

        challenges = Challenge.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_challenge_history"] = challenges.ids[:100]
        values.update(
            {
                "date": date_begin,
                "challenges": challenges,
                "page_name": "crowdfunding_challenge",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
                "default_url": "/my/crowdfunding",
            }
        )
        return request.render("crowdfunding.portal_my_crowdfunding_challenges", values)

    @http.route(
        ["/my/crowdfunding/<model('crowdfunding.challenge'):challenge>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_crowdfunding_challenge(self, challenge=None, access_token=None, **kw):
        try:
            challenge = self._document_check_access(
                "crowdfunding.challenge", challenge.id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._challenge_get_page_view_values(challenge, access_token, **kw)
        return request.render("crowdfunding.portal_my_crowdfunding_challenge", values)
