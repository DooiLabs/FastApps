from __future__ import annotations

from typing import Any, Dict

from fastapps import BaseWidget

from .pizzaz_common import WIDGET_COPY, PizzaInput, build_response


class PizzaMapWidget(BaseWidget):
    identifier = "pizza-map"
    title = WIDGET_COPY[identifier].title
    input_schema = PizzaInput
    invoking = WIDGET_COPY[identifier].invoking
    invoked = WIDGET_COPY[identifier].invoked

    widget_csp = {
        "resource_domains": [
            "https://api.mapbox.com",
            "https://events.mapbox.com",
            "https://*.tiles.mapbox.com",
            "https://tile.mapbox.com",
            "https://persistent.oaistatic.com",
        ],
        "connect_domains": [
            "https://api.mapbox.com",
            "https://events.mapbox.com",
        ],
    }

    async def execute(
        self, input_data: PizzaInput, context=None, user=None
    ) -> Dict[str, Any]:
        return build_response(input_data.pizza_topping)
