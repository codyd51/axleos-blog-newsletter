import os
from dataclasses import dataclass

import jinja2

EMAIL_JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)
ADMIN_JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)


@dataclass
class TemplateContext:
    """Context common to all templates"""
    background_color: str
    border_color: str
    generated_at: str

    should_include_unsubscribe_button: bool
    should_include_user_metadata: bool

    # The following fields are only set if `should_include_user_metadata` is set
    user_email: str | None = None
    subscription_duration: str | None = None
