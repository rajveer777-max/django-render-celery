from django.contrib import admin
from .models import Case, PastIllness

# Basic registration
# admin.site.register(Case)
# admin.site.register(PastIllness)

# --- OR ---

# More advanced registration to show PastIllness inline when editing a Case
class PastIllnessInline(admin.TabularInline): # Or admin.StackedInline for different layout
    model = PastIllness
    extra = 1 # Number of empty forms to show

class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'user', 'status', 'created_at') # Columns to show in the list view
    list_filter = ('status', 'user', 'created_at') # Filters on the right side
    search_fields = ('patient_name', 'user__username', 'presenting_complaints') # Fields to search
    inlines = [PastIllnessInline] # Show related PastIllness forms on the Case edit page

admin.site.register(Case, CaseAdmin)
admin.site.register(PastIllness) # Can still register separately if needed for direct access