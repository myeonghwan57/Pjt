from django.db import models

# Create your models here.

# 여기는 crawling
# 비워두는 걸로 해요
# 성공하면 채워 나가는 걸로
# 솔직히 진짜 해보고 싶어요 ㅋㅋㅋ
# ㄹㅇㅋㅋ
class JobData(models.Model):
    job_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    pseudo_position = models.CharField(max_length=100)
    company_job = models.TextField()
