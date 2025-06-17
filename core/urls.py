from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("start/", views.start_trial_view, name="start_trial"),
    # Case Management URLs
    path(
        "case/new/", views.new_case_view, name="new_case"
    ),  # Separate page for new case form
    path(
        "case/<int:case_id>/wait/", views.wait_for_results_view, name="wait_for_results"
    ),
    path(
        "case/<int:case_id>/", views.case_detail_view, name="case_detail"
    ),  # View details/results
    path("case/<int:case_id>/delete/", views.delete_case_view, name="delete_case"),
    path(
        "case/<int:case_id>/status/",
        views.check_case_status_view,
        name="check_case_status",
    ),  # For JS polling

    # ---- ADD THESE TEMPORARILY FOR WAITING PAGE DEVELOPMENT ----
    # path("dev/test-wait/<int:case_id>/", views.test_wait_page, name="test_wait_page"),
    # path("dev/test-status/<int:case_id>/", views.test_check_status, name="test_check_status"),
    # ---- END TEMPORARY URLS ----
]
