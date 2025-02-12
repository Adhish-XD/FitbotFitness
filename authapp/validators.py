from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    """
    Custom password validator that ensures passwords contain:
    - At least one uppercase letter
    - At least one special character (!@#$%^&*)
    - At least one number
    - At least one lowercase letter
    - Minimum length of 8 characters
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        
        if not re.search(r'[!@#$%^&*]', password):
            raise ValidationError(
                _("Password must contain at least one special character (!@#$%^&*)."),
                code='password_no_special',
            )
        
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Password must contain at least one number."),
                code='password_no_number',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least %(min_length)d characters long and contain "
            "at least one uppercase letter, one special character (!@#$%^&*), "
            "one number, and one lowercase letter."
        ) % {'min_length': self.min_length} 