# core/tasks.py
from celery import shared_task
from django.conf import settings
from .models import Case
import google.generativeai as genai
import os
import re
import json
from datetime import datetime
import traceback  # For detailed error logging
from google.generativeai import types

# Ensure genai is configured when worker starts
IS_GENAI_CONFIGURED = False
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        IS_GENAI_CONFIGURED = True
        print("Task Module: Generative AI configured successfully.")
    except Exception as e:
        print(f"Task Module: Error configuring Generative AI: {e}")
        traceback.print_exc()
else:
    print("Task Module: GEMINI_API_KEY environment variable not found.")


def get_gemini_response(prompt):
    """Calls the Gemini API and returns the text response."""
    if not IS_GENAI_CONFIGURED:
        print(
            "Error: Cannot call Gemini, API Key not configured or configuration failed."
        )
        return None
    try:
        model_name = "gemini-2.5-pro"
        print(f"DEBUG tasks.py: Using model name: {model_name}")
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        if response.parts:
            full_text = "".join(
                part.text for part in response.parts if hasattr(part, "text")
            )
            return full_text
        elif hasattr(response, "text"):
            return response.text
        else:
            print(f"Warning: Gemini response structure unexpected.")
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                print(f"Prompt Feedback: {response.prompt_feedback}")
            print(f"Full Response Object: {response}")
            return None
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")
        traceback.print_exc()
        return None


def _build_patient_data_json(case_instance):
    """Helper to construct the patient data JSON string for the prompt."""
    past_illnesses_data = [
        {
            "disease": ill.disease or "",
            "approximate_age": ill.approximate_age or "",
            "duration": ill.duration or "",
            "treatment": ill.treatment or "",
            "completely_recovered": ill.completely_recovered or "",
        }
        for ill in case_instance.past_illnesses.all()
    ]

    personal_hist = (
        case_instance.personal_history
        if isinstance(case_instance.personal_history, dict)
        else {}
    )
    menstrual_hist = (
        case_instance.menstrual_history
        if isinstance(case_instance.menstrual_history, dict)
        else {}
    )
    physical_exam = (
        case_instance.physical_examination
        if isinstance(case_instance.physical_examination, dict)
        else {}
    )
    menopause_data = (
        menstrual_hist.get("menopause", {})
        if isinstance(menstrual_hist.get("menopause"), dict)
        else {}
    )

    patient_data = {
        "date": case_instance.date.strftime("%Y-%m-%d") if case_instance.date else "",
        "opd_no": case_instance.opd_no or "",
        "name": case_instance.patient_name or "",
        "age": case_instance.patient_age or "",
        "sex": case_instance.patient_sex or "",
        "occupation": case_instance.patient_occupation or "",
        "address": case_instance.patient_address or "",
        "phone": case_instance.patient_phone or "",
        "presenting_complaints": case_instance.presenting_complaints or "",
        "history_of_present_illness": case_instance.history_of_present_illness or "",
        "past_history": {
            "vaccination": case_instance.past_history_vaccination or "",
            "illnesses": past_illnesses_data,
        },
        "family_history": case_instance.family_history or "",
        "personal_history": {
            "thermal_state": personal_hist.get("thermal_state", ""),
            "perspiration": personal_hist.get("perspiration", ""),
            "appetite": personal_hist.get("appetite", ""),
            "diet": personal_hist.get("diet", ""),
            "desire": personal_hist.get("desire", ""),
            "aversion": personal_hist.get("aversion", ""),
            "thirst": personal_hist.get("thirst", ""),
            "urine": personal_hist.get("urine", ""),
            "bowels": personal_hist.get("bowels", ""),
            "habits_addiction": personal_hist.get("habits_addiction", ""),
            "sleep": personal_hist.get("sleep", ""),
            "dreams": personal_hist.get("dreams", ""),
            "other": personal_hist.get("other", ""),  # <-- INCLUDE OTHER
        },
        "menstrual_history": {
            "age_of_puberty": menstrual_hist.get("age_of_puberty", ""),
            "menses": menstrual_hist.get("menses", ""),
            "menses_complaints": menstrual_hist.get("menses_complaints", ""),
            "age_at_marriage": menstrual_hist.get("age_at_marriage", ""),
            "lmp": menstrual_hist.get("lmp", ""),
            "menses_triggers": menstrual_hist.get("menses_triggers", ""),
            "leucorrhea": menstrual_hist.get("leucorrhea", ""),
            "pregnancy": menstrual_hist.get("pregnancy", ""),
            "menopause": {
                "age": menopause_data.get("age", ""),
                "complaints": menopause_data.get("complaints", ""),
            },
        },
        "patient_as_person": case_instance.patient_as_person or "",
        "physical_examination": {
            "built": physical_exam.get("built", ""),
            "head": physical_exam.get("head", ""),
            "throat": physical_exam.get("throat", ""),
            "hair": physical_exam.get("hair", ""),
            "mouth": physical_exam.get("mouth", ""),
            "ear": physical_exam.get("ear", ""),
            "nails": physical_exam.get("nails", ""),
            "tongue": physical_exam.get("tongue", ""),
            "eyes": physical_exam.get("eyes", ""),
            "extremities": physical_exam.get("extremities", ""),
            "teeth": physical_exam.get("teeth", ""),
            "skin": physical_exam.get("skin", ""),
            "lymph_glands": physical_exam.get("lymph_glands", ""),
            "gums": physical_exam.get("gums", ""),
            "nose": physical_exam.get("nose", ""),
            "bp": physical_exam.get("bp", ""),
            "temperature": physical_exam.get("temperature", ""),
            "pulse": physical_exam.get("pulse", ""),
            "rr": physical_exam.get("rr", ""),
            "spo2": physical_exam.get("spo2", ""),
            "other": physical_exam.get("other", ""),  # <-- INCLUDE OTHER
        },
        "systemic_examination": case_instance.systemic_examination or "",
    }
    return json.dumps(patient_data, indent=4, ensure_ascii=False)


@shared_task
def process_case_analysis(case_id):
    """Celery task to analyze case data, save results to file, and update status."""
    final_status = "ERROR"
    saved_file_rel_path = None
    case_instance = None

    try:
        case_instance = (
            Case.objects.select_related("user")
            .prefetch_related("past_illnesses")
            .get(id=case_id)
        )
        case_instance.status = "PROCESSING"
        case_instance.save(update_fields=["status", "updated_at"])
        print(f"Task started for Case ID: {case_id}. Status set to PROCESSING.")

        patient_json_string = _build_patient_data_json(case_instance)

        # --- Use the UPDATED Prompt ---
        prompt = f"""**ROLE:** Act as an exceptionally skilled and experienced senior homeopathic physician and consultant with decades of deep clinical practice, specializing in classical homeopathy. You possess encyclopedic knowledge of the Organon of Medicine (6th Edition), Kent's Repertory, Boericke's Materia Medica, Allen's Keynotes, Phatak's Materia Medica, Gibson Miller's relationship of remedies, Boger Boenninghausen's Characteristics & Repertory, and other seminal homeopathic texts and repertories. Your analysis is meticulous, holistic, and strictly adheres to homeopathic principles.

        **CONTEXT:** You are analyzing a detailed patient case provided in JSON format for the "HomeoExpertAI" platform. This platform assists qualified homeopathic practitioners by providing structured analysis and remedy suggestions based on the input case data.

        **TASK:** Perform a comprehensive homeopathic analysis of the following patient case data. Your objective is to identify the core disturbance, understand the patient's individual susceptibility and constitution, evaluate the totality of characteristic symptoms, assess the miasmatic background, **perform a detailed repertorization analysis**, determine the most appropriate homeopathic management strategy, and ** suggest relevant allopathic management ,appropriate for concurrent general practice consideration**.

        **METHODOLOGY:**
        1.  **Holistic Evaluation:** Consider the patient as a whole, integrating mental, emotional, physical general, and particular symptoms, including any 'other' notes provided.
        2.  **Symptom Analysis & Hierarchy:** Carefully evaluate *all* provided symptoms. Identify and prioritize characteristic, peculiar, rare, and strange (PQRS) symptoms according to Kent's hierarchy (Mental Generals > Physical Generals > Particulars with strong modalities/concomitants > Common Particulars). Note any strong modalities (aggravations/ameliorations), concomitants, and the patient's constitution/diathesis.
        3.  **Miasmatic Assessment:** Analyze the presenting symptoms, past history, family history, and overall symptom pattern to determine the dominant underlying miasm(s) (Psora, Sycosis, Syphilis, Tubercular) influencing the case.
        4.  **Repertorization Analysis:** Based on the most reliable and characteristic symptoms, perform a detailed repertorization. Clearly list the **key rubrics** selected for repertorization with justification. Present the **top resulting remedies** with their **grades/scores** and the **number of symptoms covered**. Explain the repertorial strategy used (e.g., Kentian, Boenninghausen).
        5.  **Materia Medica Comparison:** Differentiate between the closely competing remedies identified during repertorization by comparing their detailed Materia Medica picture with the patient's unique symptom totality.
        6.  **Diagnosis:** Formulate both a potential clinical diagnosis (based on presenting signs/symptoms) and a homeopathic diagnosis (understanding the disturbed vital force and miasmatic state).
        7.  **Homeopathic Prescription:** Select the *single* most similar remedy (the Simillimum) based on the totality of symptoms and the principles of homeopathy. Determine an appropriate starting potency and posology (repetition schedule) considering the patient's sensitivity, vitality, pathology, miasm, and the nature of the case (acute/chronic). Provide clear justification.
        8.  **Allopathic Suggestion:** If the clinical diagnosis suggests a condition where conventional treatment might be considered or necessary alongside homeopathy (e.g., for severe infections, emergencies, patient preference, co-management), provide a *brief, standard* allopathic prescription suggestion (Drug name, Dose, Route, Frequency, Duration).  Include brief justification or standard indications.

        **INPUT CASE DATA:**

        {patient_json_string}

        **REQUIRED OUTPUT:**
        Generate a response exclusively in the following JSON format. Provide clear, concise, yet sufficiently detailed information for each field, based strictly on your analysis of the provided case data. Ensure the language is professional, clinically precise, and directly addresses the homeopathic principles involved.

        {{
        "analysis_and_evaluation_of_symptoms": "Provide a detailed summary of the most significant symptoms identified from the case data. Explain their relative importance based on homeopathic hierarchy (Mentals, Generals, Peculiars, Modalities, Concomitants). Highlight the keynotes and guiding symptoms that form the core of the case's totality.",
        "miasmatic_assessment": "Identify the dominant miasm(s) (Psora, Sycosis, Syphilis, Tubercular) evident in the case presentation, past history, family history, and symptom patterns. Provide a brief justification based on specific case elements.",
        "case_type(Acute/Chronic)": "Clearly state whether the case primarily represents an Acute condition, a Chronic condition, or an Acute exacerbation of an underlying Chronic state. Justify briefly.",
        "provisional_diagnosis": "State the likely clinical condition(s) based on the presenting symptoms and history, viewed from both a conventional medical perspective (if inferable) and a homeopathic understanding of the disease state.",
        "differential_diagnosis": "List other potential clinical conditions or closely related homeopathic disease states that were considered but deemed less likely. Include brief reasoning for differentiation.",
        "final_diagnosis": "State the most probable clinical diagnosis AND the homeopathic diagnosis (e.g., 'Chronic Psoric Manifestation presenting as Eczema with marked anxiety').",
        "repertorization_analysis": {{
        "strategy": "Briefly state the repertorization approach used (e.g., Kentian focusing on PQRS, Boenninghausen's complete symptom).",
        "selected_rubrics": [
        {{"rubric": "Full Rubric Path (e.g., MIND; FEAR; death, of)", "justification": "Reason for selecting this rubric based on case symptoms.", "intensity": "Optional intensity grading (e.g., 1, 2, 3)"}},
        // ... more rubrics ...
        ],
        "repertorization_chart_summary": [
        {{"remedy": "RemedyName1", "score": "Score/Grade (e.g., 15/5 or ++++)", "symptoms_covered": "Number of key rubrics covered"}},
        {{"remedy": "RemedyName2", "score": "...", "symptoms_covered": "..."}},
        // ... list top 5 remedies from repertorization ...
        ],
        "notes": "Any specific notes regarding the repertorization process or challenges."
        }},
        "group_of_remedies": [
        "RemedyName1 (Briefly mention key differentiating symptoms from Materia Medica relevant to THIS case)",
        "RemedyName2 (Briefly mention key differentiating symptoms from Materia Medica relevant to THIS case)",
        // ... keep top contenders based on repertorization AND MM comparison ...
        ],
        "homeopathic_prescription": {{
        "remedy": "The single Simillimum selected",
        "potency": "Recommended starting potency (e.g., 30C, 200C, LM1)",
        "posology": "Detailed instructions for administration and repetition (e.g., 'Single dose stat, then wait', '6C BD for 7 days')",
        "justification": "Clear rationale linking remedy, potency, and posology choice to the case analysis (totality, miasm, vitality, sensitivity, pathology, acute/chronic nature)."
        }},
        "allopathic_prescription_suggestion": {{ // must include
        "indication": "Clinical condition warranting suggestion (e.g., 'Suspected Bacterial Infection', 'Severe Pain Management')",
        "drug": "Generic or Brand Name",
        "dose": "e.g., '500mg', '10ml'",
        "route": "e.g., 'Oral', 'Topical'",
        "frequency": "e.g., 'TDS', 'BD', 'SOS'",
        "duration": "e.g., 'for 5 days', 'as needed'",
        "justification_or_notes": "Brief reason or standard practice note (e.g., 'Standard first-line antibiotic for suspected strep throat', 'For breakthrough pain relief'). "
        }}
        }}

        **IMPORTANT:** Ensure the entire output is a single, valid JSON object starting with {{ and ending with }}. Do not include any introductory text, explanations, apologies, or concluding remarks outside of the specified JSON structure. Focus solely on providing the requested analysis within the defined format."""

        # --- 3. Call AI ---
        print(f"Calling Gemini for Case ID: {case_id}")
        response_data = get_gemini_response(prompt)

        if not response_data:
            print(
                f"Error: No response text received from Gemini for Case ID {case_id}."
            )
            raise ValueError("No response text received from AI.")

        print(
            f"Received response (length: {len(response_data)}) for Case ID: {case_id}. Stripping markdown..."
        )
        # Try to extract JSON from markdown code blocks
        match = re.search(
            r"```(?:json)?\s*(.*?)\s*```", response_data, re.DOTALL | re.IGNORECASE
        )
        if match:
            json_content = match.group(1).strip()
            print(
                f"Extracted JSON content using markdown fences for Case ID: {case_id}."
            )
        else:
            print(
                f"Warning: JSON markdown fences not found for Case ID {case_id}. Attempting to use raw response."
            )
            json_content = response_data.strip()
            # Basic check if it looks like a JSON object
            if not (json_content.startswith("{") and json_content.endswith("}")):
                print(
                    f"Error: Raw response doesn't look like JSON object for Case ID {case_id}."
                )
                raise ValueError(
                    "Response content does not appear to be a valid JSON object."
                )
            else:
                print(f"Using raw response as JSON content for Case ID: {case_id}.")

        # --- 4. Save Result ---
        opd_base = "case"
        if case_instance.opd_no:
            # Sanitize OPD number for use in filename
            sanitized_opd = re.sub(r'[\\/*?:"<>|\s]+', "_", case_instance.opd_no)
            opd_base = sanitized_opd[:50]  # Limit length

        # Ensure filename uniqueness
        filename_base = f"{opd_base}.json"
        output_path = os.path.join(settings.CASE_RESULTS_DIR, filename_base)
        counter = 1
        while os.path.exists(output_path):
            filename_base = f"{opd_base}_{counter}.json"
            output_path = os.path.join(settings.CASE_RESULTS_DIR, filename_base)
            counter += 1
            if counter > 100:  # Prevent infinite loop
                raise IOError(
                    "Failed to determine unique output filename after multiple attempts."
                )

        print(f"Attempting to save result to: {output_path}")
        os.makedirs(settings.CASE_RESULTS_DIR, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            try:
                # Validate JSON before writing
                json.loads(json_content)
                f.write(json_content)
            except json.JSONDecodeError as json_err:
                print(
                    f"Error: Content validation failed. Invalid JSON for Case ID {case_id}. Error: {json_err}"
                )
                raise ValueError("Generated content is not valid JSON.") from json_err

        print(
            f"Successfully saved result file for Case ID {case_id} at {filename_base}"
        )
        saved_file_rel_path = filename_base  # Store relative path
        final_status = "COMPLETED"

    except Case.DoesNotExist:
        print(f"Error: Case {case_id} not found in task.")
        final_status = "ERROR"
    except ValueError as ve:
        print(f"ValueError during AI task for Case ID {case_id}: {ve}")
        # Optionally log ve traceback if needed: traceback.print_exc()
        final_status = "ERROR"
    except IOError as ioe:
        print(f"IOError during AI task for Case ID {case_id}: {ioe}")
        final_status = "ERROR"
    except Exception as e:
        print(f"Unhandled error during AI task for Case ID {case_id}: {e}")
        traceback.print_exc()  # Log full traceback for unexpected errors
        final_status = "ERROR"

    finally:
        # --- 5. Update Case Status ---
        # Use a try-except block here as well, as updating the DB could fail
        try:
            if (
                case_instance and case_instance.pk
            ):  # Check if we successfully fetched the instance earlier
                # Reload the instance to avoid potential state issues if the task took long
                # or use the existing instance if confident about its state
                # For safety, reload if possible, but handle DoesNotExist
                try:
                    current_case = Case.objects.get(id=case_id)
                    # Check if an update is actually needed
                    if current_case.status != final_status or (
                        final_status == "COMPLETED"
                        and current_case.result_file_path != saved_file_rel_path
                    ):
                        current_case.status = final_status
                        if final_status == "COMPLETED" and saved_file_rel_path:
                            current_case.result_file_path = saved_file_rel_path
                        current_case.save(
                            update_fields=["status", "result_file_path", "updated_at"]
                        )
                        print(
                            f"Final update for Case {case_id}. Status: {final_status}, File: {saved_file_rel_path or 'None'}."
                        )
                    else:
                        print(
                            f"No final status update needed for Case {case_id}. Status already '{current_case.status}'."
                        )
                except Case.DoesNotExist:
                    print(
                        f"Error: Case {case_id} disappeared before final status update."
                    )
                    # Cannot update status if it's gone

            elif (
                case_id
            ):  # If case_instance was None (e.g., initial fetch failed), try to fetch again
                print(
                    f"Attempting final status update for Case ID {case_id} even if instance fetch failed earlier."
                )
                try:
                    case_to_update = Case.objects.get(id=case_id)
                    if (
                        case_to_update.status != final_status
                    ):  # Avoid unnecessary DB write
                        case_to_update.status = final_status
                        # Cannot set result_file_path reliably here if initial steps failed
                        case_to_update.save(update_fields=["status", "updated_at"])
                        print(
                            f"Final status update for Case {case_id} set to {final_status}."
                        )
                    else:
                        print(
                            f"No final status update needed for Case {case_id}. Status already '{case_to_update.status}'."
                        )
                except Case.DoesNotExist:
                    print(
                        f"Error: Case {case_id} not found during final status update."
                    )
                except Exception as final_update_e:
                    print(
                        f"Error during final status update attempt for Case {case_id}: {final_update_e}"
                    )

        except Exception as final_save_e:
            print(
                f"Critical Error during final update block for Case {case_id}: {final_save_e}"
            )
            traceback.print_exc()
