# core/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import os # For deleting files

class Case(models.Model):
    # --- Metadata & Patient Demographics ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateField(default=timezone.now, blank=True, null=True) # Made optional
    # Removed unique=True - rely on filename logic in task for uniqueness if needed
    opd_no = models.CharField(max_length=50, blank=True, null=True)
    patient_name = models.CharField(max_length=200) # Required
    patient_age = models.CharField(max_length=20, blank=True, null=True)
    patient_sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    patient_occupation = models.CharField(max_length=100, blank=True, null=True)
    patient_address = models.TextField(blank=True, null=True)
    patient_phone = models.CharField(max_length=20, blank=True, null=True)

    # --- Core Case Details ---
    presenting_complaints = models.TextField() # Required
    history_of_present_illness = models.TextField(blank=True, null=True)
    past_history_vaccination = models.TextField(blank=True, null=True) # Corresponds to past_history.vaccination
    family_history = models.TextField(blank=True, null=True)

    # Use JSONField for structured *input* data (easier to build prompt payload)
    personal_history = models.JSONField(blank=True, null=True, default=dict)
    menstrual_history = models.JSONField(blank=True, null=True, default=dict)
    physical_examination = models.JSONField(blank=True, null=True, default=dict)

    patient_as_person = models.TextField(blank=True, null=True)
    systemic_examination = models.TextField(blank=True, null=True)

    # --- AI Results & Status ---
    # Store the PATH to the result file, not the content itself
    result_file_path = models.CharField(max_length=512, blank=True, null=True) # Store relative path?

    STATUS_CHOICES = [
        ('PENDING', 'Pending Analysis'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Case {self.id or 'New'} for {self.user.username} (OPD: {self.opd_no or 'N/A'})"

    def delete(self, *args, **kwargs):
        # Override delete to remove the associated result file
        if self.result_file_path:
            # Construct full path using settings.CASE_RESULTS_DIR
            full_path = os.path.join(settings.CASE_RESULTS_DIR, self.result_file_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    print(f"Deleted result file: {full_path}")
                except OSError as e:
                    print(f"Error deleting result file {full_path}: {e}")
            else:
                 print(f"Result file path exists in DB but not found on disk: {full_path}")
        super().delete(*args, **kwargs) # Call the original delete method

    class Meta:
        ordering = ['-created_at']

class PastIllness(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='past_illnesses')
    disease = models.CharField(max_length=200, blank=True, null=True)
    approximate_age = models.CharField(max_length=50, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    completely_recovered = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.disease or 'Unnamed Illness'} for Case {self.case_id}"

    class Meta:
        verbose_name_plural = "Past Illnesses"