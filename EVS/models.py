from django.db import models

class AcademicYear(models.Model):
    acad_year_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)
    year_start = models.DateField()
    year_end = models.DateField()
    semester = models.IntegerField()
    date_created = models.DateField(auto_now_add=True)
    osa_id = models.IntegerField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year_start}-{self.year_end} Sem {self.semester}"

class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    semester = models.CharField(max_length = 200)

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
    
class Violation(models.Model):
    violation_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description  

class Reason(models.Model):
    reason_id = models.AutoField(primary_key=True)
    reason_type = models.CharField(max_length=200)
    description = models.CharField(max_length=200) 

    def __str__(self):
        return self.description 

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    uniform_violation = models.BooleanField(default=0)
    dress_code_violation = models.BooleanField(default=0)
    id_violation = models.BooleanField(default=0)
    id_not_claimed_violation = models.BooleanField(default=0)
    osa_id = models.IntegerField()
    submitted_by = models.CharField(max_length=200)
    id_status = models.IntegerField(default=0)
    ticket_status = models.IntegerField(default=0)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    photo_path = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_validated = models.DateTimeField(null=True, blank=True)
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='tickets_by_semester')
    acad_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='tickets_by_academic_year')
    
    def __str__(self):
        return f"Ticket {self.ticket_id} - Submitted by {self.submitted_by}"
    
class TicketReason(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    reason = models.ForeignKey(Reason, on_delete=models.CASCADE)

class StudentViolation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    community_service = models.BooleanField(default=0)
    community_service_status = models.SmallIntegerField(default=0, null=True)
    apology_letter = models.BooleanField(default=0)
    apology_letter_status = models.SmallIntegerField(default=0, null=True)
    acad_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} - {self.violation} (x{self.count})"