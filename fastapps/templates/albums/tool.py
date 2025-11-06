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
    description = "Photo albums gallery widget with fullscreen viewer"
    invoking = "Loading albums..."
    invoked = "Albums ready!"
    input_schema = {ClassName}Input

    async def execute(self, input_data: {ClassName}Input, context=None, user=None):
        # Example: Return sample albums
        return {
            "albums": [
                {
                    "id": "album-1",
                    "title": "Sample Album 1",
                    "cover": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-1.png",
                    "photos": [
                        {
                            "id": "p1",
                            "title": "Photo 1",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-1.png"
                        },
                        {
                            "id": "p2",
                            "title": "Photo 2",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-2.png"
                        },
                        {
                            "id": "p3",
                            "title": "Photo 3",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-3.png"
                        }
                    ]
                },
                {
                    "id": "album-2",
                    "title": "Sample Album 2",
                    "cover": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-5.png",
                    "photos": [
                        {
                            "id": "p4",
                            "title": "Photo 4",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-4.png"
                        },
                        {
                            "id": "p5",
                            "title": "Photo 5",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-5.png"
                        }
                    ]
                },
                {
                    "id": "album-3",
                    "title": "Sample Album 3",
                    "cover": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-7.png",
                    "photos": [
                        {
                            "id": "p6",
                            "title": "Photo 6",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-6.png"
                        },
                        {
                            "id": "p7",
                            "title": "Photo 7",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-7.png"
                        },
                        {
                            "id": "p8",
                            "title": "Photo 8",
                            "url": "https://pub-d9760dbd87764044a85486be2fdf7f9f.r2.dev/example-8.png"
                        }
                    ]
                }
            ]
        }
