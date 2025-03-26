from django.db.models import DateTimeField
from .lookups import DateTimeOffsetLookup

# Register lookup globally
DateTimeField.register_lookup(DateTimeOffsetLookup)
