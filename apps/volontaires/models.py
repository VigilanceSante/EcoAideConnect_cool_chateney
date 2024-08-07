from django.db import models

class ContactForm(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    start_date = models.DateField(verbose_name="Heure de début")
    end_date = models.DateField(verbose_name="Heure de fin")
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    monday_all_day = models.BooleanField(default=False)
    monday_morning = models.BooleanField(default=False)
    monday_afternoon = models.BooleanField(default=False)
    monday_evening = models.BooleanField(default=False)
    tuesday_all_day = models.BooleanField(default=False)
    tuesday_morning = models.BooleanField(default=False)
    tuesday_afternoon = models.BooleanField(default=False)
    tuesday_evening = models.BooleanField(default=False)
    wednesday_all_day = models.BooleanField(default=False)
    wednesday_morning = models.BooleanField(default=False)
    wednesday_afternoon = models.BooleanField(default=False)
    wednesday_evening = models.BooleanField(default=False)
    thursday_all_day = models.BooleanField(default=False)
    thursday_morning = models.BooleanField(default=False)
    thursday_afternoon = models.BooleanField(default=False)
    thursday_evening = models.BooleanField(default=False)
    friday_all_day = models.BooleanField(default=False)
    friday_morning = models.BooleanField(default=False)
    friday_afternoon = models.BooleanField(default=False)
    friday_evening = models.BooleanField(default=False)
    saturday_all_day = models.BooleanField(default=False)
    saturday_morning = models.BooleanField(default=False)
    saturday_afternoon = models.BooleanField(default=False)
    saturday_evening = models.BooleanField(default=False)
    sunday_all_day = models.BooleanField(default=False)
    sunday_morning = models.BooleanField(default=False)
    sunday_afternoon = models.BooleanField(default=False)
    sunday_evening = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

