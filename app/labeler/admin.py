from django.contrib import admin
from .models import ShoeBox


class ShoeBoxAdmin(admin.ModelAdmin):
    """Admin view class for ShoeBox model"""

    # Fields to display on admin page
    list_display = ('__str__', 'from_receipt_id', 'to_receipt_id', 'num_receipts', 'user')
    ordering = ['id']
    # Add filtering
    list_filter = ('user',)


# Register admin model
admin.site.register(ShoeBox, ShoeBoxAdmin)