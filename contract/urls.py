
from django.urls import path
from .views import *

urlpatterns = [
    path('recent/list/', recent_contracts_list, name='recent-contracts'),
    path('details/<str:notice_id>/', contracts_details, name='contract-details'),

    path('requirements-analysis/', requirements_analysis, name='requirements-analysis'),
    path('generate-proposal/', generate_proposal, name='generate-proposal'),

    path('draft-proposals/save/', save_draft_proposal, name='save_draft_proposal'),
    path('draft-proposals/delete/<int:proposal_id>/', delete_draft_proposal, name='delete_draft_proposal'),
    path('draft-proposals/list/', draf_proposal_list, name='draft-proposals'),
    path('submitted-proposals/', submit_proposal_list, name='submitted-proposals'),
    path('proposal/<int:proposal_id>/', get_proposal_by_id, name='proposal'),  # get and update proposal by id
    path('proposal/', update_proposal_by_id, name='update_proposal_by_id'),  # get and update proposal by id
    # path('download-pdf/', download_pdf, name='download-pdf'),
    path('send-pdf-email/', send_pdf_email_link, name='send_pdf_email_link'),
    path('proposal_pdf/<int:proposal_id>/', proposal_pdf, name='proposal_pdf'),
]

