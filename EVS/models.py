from django.db import models

# Create your models here.
class tickets(models.Model):
    ticket_id = models.IntegerField()
    uniform_violation = models.BooleanField()
    dress_code_violation = models.BooleanField()
    id_violation = models.BooleanField()
    id_not_claimed_violation = models.BooleanField()
    osa_id = models.IntegerField()
    submitted_by = models.CharField(max_length = 200)
    id_status = models.BooleanField()
    ticket_status = models.BooleanField()
    remarks = models.CharField(max_length = 200)
    reasons = models.CharField(max_length = 200)
    photo_path = models.CharField(max_length = 200)
    date_created = models.DateTimeField()
    date_validated = models.DateTimeField()

class role(models.Model):
    role_id = models.AutoField(primary_key = True)
    role_desc = models.CharField(max_length = 200)

class student(models.Model):
    student_id = models.IntegerField(primary_key = True)
    FName = models.CharField(max_length = 200)
    LName = models.CharField(max_length = 200)
    MName = models.CharField(max_length = 200)

class academic_year(models.Model):
    acad_year_id = models.AutoField(primary_key = True)
    academic_year_start = models.DateField()
    academic_year_end = models.DateField()
    semester = models.IntegerField()
    date_created = models.DateField(auto_now = True)
    osa_id = models.IntegerField()

class violation(models.Model):
    violation_id = models.AutoField(primary_key = True)
    violation_desc = models.CharField(max_length = 200)

class student_violation(models.Model):
    student_id = models.ForeignKey(student, on_delete = models.CASCADE)
    violation_id = models.ForeignKey(violation, on_delete = models.CASCADE)
    count = models.IntegerField()
    comm_serv = models.BooleanField()
    comm_serv_status = models.SmallIntegerField()
    apology_letter = models.BooleanField()
    apology_letter_status = models.SmallIntegerField()
