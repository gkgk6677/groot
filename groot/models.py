from django.db import models

# Create your models here.
class test(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True)
    user_pw = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    c_date = models.DateTimeField()

class User(models.Model):
    id_idx = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    user_pw = models.CharField(max_length=100)
    com_num = models.IntegerField()
    com_name = models.CharField(max_length=100)
    com_head = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_num = models.IntegerField()
    s_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'User'