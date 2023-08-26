import os
import random
from dataclasses import dataclass

import jinja2

EMAIL_JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)
ADMIN_JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)


_RgbChannel = int
_RgbTriplet = (_RgbChannel, _RgbChannel, _RgbChannel)


def _get_random_pastel_with_depth(depth: int) -> _RgbTriplet:
    # PT: This intentionally duplicates the logic in the axle blog `.blog-post-container` element
    # The general approach here is to generate all the combos in which one color channel is at full saturation,
    # and the other two have a smidge taken off.
    colors = set()
    for subtract1 in range(1, depth):
        for channel1 in range(3):
            for subtract2 in range(1, depth):
                for channel2 in range(3):
                    # Don't subtract from the same channel more than once
                    if channel1 == channel2:
                        continue
                    # Use a list just to get indexed assignment, then transform back into a tuple
                    triplet = [255, 255, 255]
                    triplet[channel1] -= subtract1
                    triplet[channel2] -= subtract2
                    colors.add((triplet[0], triplet[1], triplet[2]))
    return random.choice(list(colors))


@dataclass
class TemplateContext:
    """Context common to all templates"""
    generated_at: str

    should_include_unsubscribe_button: bool
    should_include_user_metadata: bool

    # The following fields contain auto-generated values and should not be explicitly set
    background_color: str
    border_color: str

    # The following fields are only set if `should_include_user_metadata` is set
    user_email: str | None = None
    subscription_duration: str | None = None

    def __init__(self, **kwargs) -> None:
        if any(x in kwargs for x in ["background_color", "border_color"]):
            raise ValueError(f"These arguments should not be manually specified")

        background_color = _get_random_pastel_with_depth(8)
        background_color_rgb = f'rgb({background_color[0]}, {background_color[1]}, {background_color[2]})'
        # PT: For now, omit the logic to color the border with a slightly darkened version of the background color,
        # as it's a bit hairy
        border_color="rgb(127, 127, 127)"

        merged_dict = {
            **{
                "background_color": background_color_rgb,
                "border_color": border_color,
            },
            **kwargs,
        }
        self.__dict__.update(merged_dict)
