from django.urls import path
from .views import ask_question, get_schema_info, run_evaluation

urlpatterns = [
    path('ask/', ask_question, name='ask_question'),
    path('schema/', get_schema_info, name='get_schema'),
    path('evaluate/', run_evaluation, name='run_evaluation'),
]