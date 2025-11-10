from fastapps import BaseWidget, ConfigDict
from pydantic import BaseModel, Field


class {ClassName}Input(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Example parameter - customize based on your widget's needs
    query: str = Field(
        default="",
        description="Search query or filter parameter"
    )


class {ClassName}Tool(BaseWidget):
    identifier = "{identifier}"
    title = "{title}"
    description = "A horizontal scrolling carousel widget"
    invoking = "Loading carousel..."
    invoked = "Carousel ready!"
    input_schema = {ClassName}Input

    # Optional: Configure widget-specific CSP (if needed)
    # For project-wide domains, use global_resource_domains in WidgetMCPServer instead
    # widget_csp = {
    #     "resource_domains": ["https://example.com"],
    #     "connect_domains": []
    # }

    async def execute(self, input_data: {ClassName}Input, context=None, user=None):
        # Example: Return sample cards for carousel
        return {
            "cards": [
                {
                    "id": 1,
                    "name": "Sample Card 1",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-1.png",
                    "rating": 4.5,
                    "price": "$$",
                    "description": "Description for Card 1"
                },
                {
                    "id": 2,
                    "name": "Sample Card 2",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-5.png",
                    "rating": 4.2,
                    "price": "$$$",
                    "description": "Description for Card 2"
                },
                {
                    "id": 3,
                    "name": "Sample Card 3",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-7.png",
                    "rating": 4.7,
                    "price": "$$",
                    "description": "Description for Card 3"
                },
                {
                    "id": 4,
                    "name": "Sample Card 4",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-9.png",
                    "rating": 3.8,
                    "price": "$",
                    "description": "Description for Card 4"
                },
                {
                    "id": 5,
                    "name": "Sample Card 5",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-10.png",
                    "rating": 4.9,
                    "price": "$$$$",
                    "description": "Description for Card 5"
                },
            ]
        }
