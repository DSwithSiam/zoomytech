from django.db import models
from accounts.models import CustomUser



class Testimonial(models.Model):
    image = models.ImageField(upload_to='testimonial', null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title or "Untitled Testimonial"

class ContractDetails(models.Model):
    notice_id = models.CharField(max_length = 300)
    contract = models.JSONField(null = True, blank = True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)



class ContractProposal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposal')
    notice_id = models.CharField(max_length = 300)
    solicitation_number = models.CharField(max_length = 300)
    opportunity_type = models.CharField(max_length = 50)
    inactive_date = models.DateField(null=True, blank = True)
    draft = models.BooleanField(default=False)
    submit = models.BooleanField(default=False) 
    proposal = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __init__(self):
        return f"{self.notice_id}"
