from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel, Field

from fastapps import ConfigDict

DEFAULT_TOPPING = "Margherita"


class PizzaInput(BaseModel):
    """Shared input schema for all Pizzaz widgets."""

    pizza_topping: str = Field(
        DEFAULT_TOPPING,
        alias="pizzaTopping",
        description="Topping to mention when rendering the widget.",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


@dataclass(frozen=True)
class WidgetCopy:
    title: str
    invoking: str
    invoked: str


WIDGET_COPY: Dict[str, WidgetCopy] = {
    "pizza-map": WidgetCopy(
        title="Show Pizza Map",
        invoking="Hand-tossing a map",
        invoked="Served a fresh map",
    ),
    "pizza-carousel": WidgetCopy(
        title="Show Pizza Carousel",
        invoking="Carousel some spots",
        invoked="Served a fresh carousel",
    ),
    "pizza-albums": WidgetCopy(
        title="Show Pizza Album",
        invoking="Hand-tossing an album",
        invoked="Served a fresh album",
    ),
    "pizza-list": WidgetCopy(
        title="Show Pizza List",
        invoking="Hand-tossing a list",
        invoked="Served a fresh list",
    ),
    "pizza-shop": WidgetCopy(
        title="Open Pizzaz Shop",
        invoking="Opening the shop",
        invoked="Shop opened",
    ),
}


def build_response(topping: str) -> Dict[str, str]:
    """Structured content returned to the widget."""
    display_topping = topping or DEFAULT_TOPPING
    return {
        "pizzaTopping": display_topping,
        "message": f"Rendered a pizza experience featuring {display_topping}.",
    }
