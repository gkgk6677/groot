from django.db import models

# Create your models here.
from django.forms import SelectDateWidget

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    user_pw = models.CharField(max_length=100)
    com_num = models.IntegerField()
    com_name = models.CharField(max_length=100)
    com_head = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_num = models.IntegerField()
    c_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'User'


class Certificate(models.Model):
    cert_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey('Enrollment', models.DO_NOTHING, db_column='enroll_idx')
    term = models.IntegerField()
    end_date = models.DateTimeField()
    cert_tx = models.CharField(max_length=100)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Certificate'


class Contract(models.Model):
    cont_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey('Enrollment', models.DO_NOTHING, db_column='enroll_idx')
    term = models.IntegerField()
    end_date = models.DateTimeField()
    c_date = models.DateTimeField()
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Contract'
        unique_together = (('cont_idx', 'user', 'enroll_idx'),)


class DocVf(models.Model):
    doc_idx = models.AutoField(primary_key=True)
    uuid = models.ForeignKey('File', models.DO_NOTHING, db_column='uuid')
    up_hash = models.CharField(max_length=100)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Doc_vf'
        unique_together = (('doc_idx', 'uuid'),)

class SortMst(models.Model):
    sort_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100 )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'Sort_MST'



class Enrollment(models.Model):
    enroll_idx = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    sort_idx = models.ForeignKey(SortMst, models.DO_NOTHING, db_column='sort_idx')
    title = models.CharField(max_length=100)
    term = models.IntegerField()
    enroll_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    enroll_tx = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Enrollment'
        unique_together = (('enroll_idx', 'user', 'sort_idx'),)


class File(models.Model):
    uuid = models.CharField(primary_key=True, max_length=100)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=100)
    m_date = models.DateTimeField()
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'File'


class ItBoard(models.Model):
    board_idx = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    c_date = models.DateTimeField()
    m_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'It_board'
        unique_together = (('board_idx', 'user'),)


class Notice(models.Model):
    notice_idx = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    c_date = models.DateTimeField()
    m_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Notice'
        unique_together = (('notice_idx', 'user'),)

    #title return
    def __str__(self):
        return self.title

    # detail을 위한 함수
    def get_abolute_url(self):
        return reversed('notice-detail', args=[str(self.id)])

    # update를 위한 함수
    @property
    def update_count(self):
        self.count = self.count +1
        self.save()





