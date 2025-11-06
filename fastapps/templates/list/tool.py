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
    description = "A ranked list widget"
    invoking = "Loading list..."
    invoked = "List ready!"
    input_schema = {ClassName}Input

    async def execute(self, input_data: {ClassName}Input, context=None, user=None):
        # Example: Return sample items
        return {
            "title": "Sample List",
            "description": "A list of items",
            "items": [
                {
                    "id": 1,
                    "name": "Sample Item 1",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-1.png",
                    "rating": 4.5,
                    "info": "Additional info 1"
                },
                {
                    "id": 2,
                    "name": "Sample Item 2",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-5.png",
                    "rating": 4.2,
                    "info": "Additional info 2"
                },
                {
                    "id": 3,
                    "name": "Sample Item 3",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-7.png",
                    "rating": 4.7,
                    "info": "Additional info 3"
                },
                {
                    "id": 4,
                    "name": "Sample Item 4",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-9.png",
                    "rating": 3.8,
                    "info": "Additional info 4"
                },
                {
                    "id": 5,
                    "name": "Sample Item 5",
                    "thumbnail": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-10.png",
                    "rating": 3.9,
                    "info": "Additional info 5"
                },
            ]
        }
