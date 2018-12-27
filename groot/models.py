from django.db import models

# Create your models here.
from django.forms import SelectDateWidget


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
    user_id = models.ForeignKey('User', models.DO_NOTHING)
    term = models.IntegerField()
    end_date = models.DateTimeField()
    c_date = models.DateTimeField()

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


class Enrollment(models.Model):
    enroll_idx = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('User', models.DO_NOTHING)
    sort_idx = models.ForeignKey('SortMst', models.DO_NOTHING, db_column='sort_idx')
    title = models.CharField(max_length=100)
    term = models.IntegerField()
    enroll_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    enroll_tx = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()

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
    user_id = models.ForeignKey('User', models.DO_NOTHING)
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
    user_id = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    c_date = models.DateTimeField()
    m_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Notice'
        unique_together = (('notice_idx', 'user'),)


class SortMst(models.Model):
    sort_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Sort_MST'