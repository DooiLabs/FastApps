from __future__ import annotations

from typing import Any, Dict

from fastapps import BaseWidget

from .pizzaz_common import WIDGET_COPY, PizzaInput, build_response


class PizzaCarouselWidget(BaseWidget):
    identifier = "pizza-carousel"
    title = WIDGET_COPY[identifier].title
    input_schema = PizzaInput
    invoking = WIDGET_COPY[identifier].invoking
    invoked = WIDGET_COPY[identifier].invoked

    widget_csp = {
        "resource_domains": ["https://persistent.oaistatic.com"],
        "connect_domains": [],
    }

    async def execute(
        self, input_data: PizzaInput, context=None, user=None
    ) -> Dict[str, Any]:
        return build_response(input_data.pizza_topping)
