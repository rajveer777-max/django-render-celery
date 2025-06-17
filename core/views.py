# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages  # For user feedback
from .models import Case, PastIllness
from .forms import CaseForm, PastIllnessFormSet  # Import updated forms
from .tasks import process_case_analysis # Import the Celery task
import json
from django.conf import settings
import os
from django.http import JsonResponse # For check_case_status_view
import time

# Create your views here.

# DUMMY_WAITING_CASE_START_TIME = {} 

# def test_wait_page(request, case_id):
#     # Convert case_id to string for consistent dictionary key usage
#     case_id_str = str(case_id)

#     # Always set/reset the start time for this case_id when this page is loaded
#     DUMMY_WAITING_CASE_START_TIME[case_id_str] = time.time() 
    
#     print(f"[test_wait_page] Setting start time for case {case_id_str}: {DUMMY_WAITING_CASE_START_TIME[case_id_str]}") # Debug

#     case_dummy_data = {
#         'id': case_id, # Pass the original int case_id to the template
#         'patient_name': 'Dev Test Patient ' + str(case_id),
#         'status': 'PROCESSING', 
#         'get_status_display': 'Processing (Dev Mode)...'
#     }
#     context = {'case': case_dummy_data}
#     return render(request, 'waiting.html', context)

# def test_check_status(request, case_id):
#     case_id_str = str(case_id)
#     start_time = DUMMY_WAITING_CASE_START_TIME.get(case_id_str, None)

#     if start_time is None:
#         # This scenario means test_check_status was called before test_wait_page for this case_id in the current server session
#         # Or the server restarted. We'll start the timer now.
#         print(f"[test_check_status] Warning: start_time not found for case {case_id_str}. Initializing now.")
#         DUMMY_WAITING_CASE_START_TIME[case_id_str] = time.time()
#         start_time = DUMMY_WAITING_CASE_START_TIME[case_id_str]
#         # Return PROCESSING immediately as it's effectively the "first" check
#         return JsonResponse({'status': 'PROCESSING', 'status_display': 'Processing (Dev Mode - Timer Reset)'})

#     elapsed_time = time.time() - start_time

#     current_status = 'PROCESSING' 
#     current_status_display = 'Processing (Dev Mode)...'

#     # Target durations for each state for clarity
#     PROCESSING_DURATION = 10  # seconds
#     ERROR_DURATION = 10       # seconds (will show error from PROCESSING_DURATION to PROCESSING_DURATION + ERROR_DURATION)
#     # COMPLETED state is after PROCESSING_DURATION + ERROR_DURATION

#     if elapsed_time > (PROCESSING_DURATION + ERROR_DURATION): # e.g., > 20 seconds
#         current_status = 'COMPLETED'
#         current_status_display = 'Completed (Dev Mode)'
#     elif elapsed_time > PROCESSING_DURATION: # e.g., > 10 seconds (but not > 20)
#         current_status = 'ERROR'
#         current_status_display = 'Error in Processing (Dev Mode)'
#     # else (0 to PROCESSING_DURATION seconds): status remains 'PROCESSING'

#     print(f"[test_check_status] Case ID: {case_id_str}, Elapsed: {elapsed_time:.2f}s, StartTime: {start_time:.2f}, CurrentTime: {time.time():.2f}, Status: {current_status}")
#     return JsonResponse({'status': current_status, 'status_display': current_status_display})

def home_page(request):
    context = {}
    return render(request, "landing_page.html", context)


def start_trial_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("core:dashboard"))
    else:
        return redirect(reverse("auth_app:account"))


@login_required
def dashboard_view(request):
    user_cases = Case.objects.filter(user=request.user)
    context = {
        "username": request.user.username,
        "cases": user_cases,
    }
    return render(request, "dashboard.html", context)


@login_required
def new_case_view(request):
    if request.method == "POST":
        form = CaseForm(request.POST)
        formset = PastIllnessFormSet(request.POST, prefix="illnesses")

        if form.is_valid() and formset.is_valid():
            case_instance = form.save(commit=False)
            case_instance.user = request.user
            case_instance.status = "PENDING"

            # --- Construct JSON data including 'other' fields ---
            case_instance.personal_history = {
                "thermal_state": form.cleaned_data.get("personal_thermal_state"),
                "perspiration": form.cleaned_data.get("personal_perspiration"),
                "appetite": form.cleaned_data.get("personal_appetite"),
                "diet": form.cleaned_data.get("personal_diet"),
                "desire": form.cleaned_data.get("personal_desire"),
                "aversion": form.cleaned_data.get("personal_aversion"),
                "thirst": form.cleaned_data.get("personal_thirst"),
                "urine": form.cleaned_data.get("personal_urine"),
                "bowels": form.cleaned_data.get("personal_bowels"),
                "habits_addiction": form.cleaned_data.get("personal_habits_addiction"),
                "sleep": form.cleaned_data.get("personal_sleep"),
                "dreams": form.cleaned_data.get("personal_dreams"),
                "other": form.cleaned_data.get("personal_other") # <-- ADDED OTHER
            }
            case_instance.menstrual_history = {
                "age_of_puberty": form.cleaned_data.get("menstrual_age_of_puberty"),
                "menses": form.cleaned_data.get("menstrual_menses"),
                "menses_complaints": form.cleaned_data.get("menstrual_menses_complaints"),
                "age_at_marriage": form.cleaned_data.get("menstrual_age_at_marriage"),
                "lmp": form.cleaned_data.get("menstrual_lmp"),
                "menses_triggers": form.cleaned_data.get("menstrual_menses_triggers"),
                "leucorrhea": form.cleaned_data.get("menstrual_leucorrhea"),
                "pregnancy": form.cleaned_data.get("menstrual_pregnancy"),
                "menopause": {
                    "age": form.cleaned_data.get("menstrual_menopause_age"),
                    "complaints": form.cleaned_data.get("menstrual_menopause_complaints"),
                },
            }
            case_instance.physical_examination = {
                 "built": form.cleaned_data.get("physical_built"),
                 "head": form.cleaned_data.get("physical_head"),
                 "throat": form.cleaned_data.get("physical_throat"),
                 "hair": form.cleaned_data.get("physical_hair"),
                 "mouth": form.cleaned_data.get("physical_mouth"),
                 "ear": form.cleaned_data.get("physical_ear"),
                 "nails": form.cleaned_data.get("physical_nails"),
                 "tongue": form.cleaned_data.get("physical_tongue"),
                 "eyes": form.cleaned_data.get("physical_eyes"),
                 "extremities": form.cleaned_data.get("physical_extremities"),
                 "teeth": form.cleaned_data.get("physical_teeth"),
                 "skin": form.cleaned_data.get("physical_skin"),
                 "lymph_glands": form.cleaned_data.get("physical_lymph_glands"),
                 "gums": form.cleaned_data.get("physical_gums"),
                 "nose": form.cleaned_data.get("physical_nose"),
                 "bp": form.cleaned_data.get("physical_bp"),
                 "temperature": form.cleaned_data.get("physical_temperature"),
                 "pulse": form.cleaned_data.get("physical_pulse"),
                 "rr": form.cleaned_data.get("physical_rr"),
                 "spo2": form.cleaned_data.get("physical_spo2"),
                 "other": form.cleaned_data.get("physical_other") # <-- ADDED OTHER
            }
            # --- End JSON Construction ---

            case_instance.save() # Save case FIRST to get ID

            # --- Save Formset ---
            illnesses = formset.save(commit=False)
            for illness in illnesses:
                illness.case = case_instance
                illness.save()
            for form_to_delete in formset.deleted_forms:
                if form_to_delete.instance.pk:
                    form_to_delete.instance.delete()
            # --- End Formset Save ---

            # --- Trigger ASYNCHRONOUS Task ---
            try:
                process_case_analysis.delay(case_instance.id)
                print(f"AI analysis task queued for Case ID: {case_instance.id}")
                messages.success(request, "Case submitted! Analysis is processing in the background.")
                return redirect(reverse('core:wait_for_results', kwargs={'case_id': case_instance.id}))
            except Exception as task_err:
                 print(f"Error queueing analysis task for Case {case_instance.id}: {task_err}")
                 messages.error(request, "Could not submit case for analysis. Please contact support.")
                 context = {'form': form, 'illness_formset': formset}
                 return render(request, 'new_case.html', context)

        else:
            messages.error(request, "Please correct the errors below.")
            context = {'form': form, 'illness_formset': formset}
            return render(request, 'new_case.html', context)
    else:
        # GET request
        form = CaseForm()
        formset = PastIllnessFormSet(prefix='illnesses')
        context = {'form': form, 'illness_formset': formset}
        return render(request, 'new_case.html', context)


@login_required
def wait_for_results_view(request, case_id):
    case = get_object_or_404(Case, id=case_id, user=request.user)
    context = {"case": case, "case_status": case.status}
    return render(request, "waiting.html", context)


@login_required
def case_detail_view(request, case_id):
    case = get_object_or_404(Case.objects.prefetch_related('past_illnesses'), id=case_id, user=request.user)
    results_data = None
    error_message = None
    case_type_value = None # Initialize variable for case type

    if case.status == 'COMPLETED' and case.result_file_path:
        full_path = os.path.join(settings.CASE_RESULTS_DIR, case.result_file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                results_data = json.loads(file_content)
                # Extract the specific value for case_type(Acute/Chronic)
                if results_data:
                    case_type_value = results_data.get("case_type(Acute/Chronic)")
            except json.JSONDecodeError:
                error_message = "Error: The result file contains invalid JSON."
                print(f"JSONDecodeError for file: {full_path}")
            except Exception as e:
                error_message = f"Error reading result file: {e}"
                print(f"Error reading file {full_path}: {e}")
        else:
            error_message = f"Error: Result file not found ({case.result_file_path}), although case is marked completed."
            print(f"Result file not found: {full_path}")

    elif case.status == 'ERROR':
         error_message = "An error occurred during the analysis process."
    elif case.status == 'PROCESSING' or case.status == 'PENDING':
         error_message = "Analysis is still in progress. Please check back later."

    context = {
        'case': case,
        'results_data': results_data,
        'error_message': error_message,
        'case_type_value': case_type_value, # Pass the extracted value to the template
    }
    return render(request, 'case_detail.html', context)

@login_required
def delete_case_view(request, case_id):
    case = get_object_or_404(Case, id=case_id, user=request.user)
    if request.method == 'POST':
        case_id_display = case.id
        try:
            case.delete()
            messages.success(request, f'Case {case_id_display} and associated results deleted successfully.')
        except Exception as e:
             messages.error(request, f'Error deleting case {case_id_display}: {e}')
             print(f"Error during case deletion {case_id_display}: {e}")
        return redirect('core:dashboard')
    else:
        # Redirect for GET requests to avoid accidental deletion
        return redirect('core:dashboard')

@login_required
def check_case_status_view(request, case_id):
    case = get_object_or_404(Case, id=case_id, user=request.user)
    return JsonResponse(
        {"status": case.status, "status_display": case.get_status_display()}
    )