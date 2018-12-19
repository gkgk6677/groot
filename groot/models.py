from django.db import models

# Create your models here.

class CertVf(models.Model):
    cert_idx = models.AutoField(primary_key=True)
    pre_hash = models.CharField(max_length=100, blank=True, null=True)
    up_hash = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()
    certificate_issu_idx = models.ForeignKey('Certificate', models.DO_NOTHING, db_column='certificate_issu_idx')

    class Meta:
        managed = False
        db_table = 'Cert_vf'


class Certificate(models.Model):
    issu_idx = models.AutoField(primary_key=True)
    e_date = models.DateTimeField()
    c_date = models.DateTimeField()
    contract_cont_idx = models.ForeignKey('Contract', models.DO_NOTHING, db_column='contract_cont_idx')

    class Meta:
        managed = False
        db_table = 'Certificate'


class Contract(models.Model):
    cont_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    sort = models.CharField(max_length=100)
    e_date = models.DateTimeField()
    c_date = models.DateTimeField()
    user_user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Contract'


class DocVf(models.Model):
    doc_idx = models.AutoField(primary_key=True)
    pre_hash = models.CharField(max_length=100, blank=True, null=True)
    up_hash = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()
    file_file_idx = models.ForeignKey('File', models.DO_NOTHING, db_column='file_file_idx')

    class Meta:
        managed = False
        db_table = 'Doc_vf'


class File(models.Model):
    file_idx = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=100)
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=100)
    s_date = models.DateTimeField()
    c_date = models.DateTimeField()
    contract_cont_idx = models.ForeignKey(Contract, models.DO_NOTHING, db_column='contract_cont_idx')

    class Meta:
        managed = False
        db_table = 'File'


class ItBoard(models.Model):
    board_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    c_date = models.DateTimeField()
    user_user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'It_board'


class Notice(models.Model):
    notice_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    c_date = models.DateTimeField(auto_now_add=True)
    user_user = models.ForeignKey('User', models.DO_NOTHING)



    class Meta:
        managed = False
        db_table = 'Notice'

    # @@2018 12 18 추가@@
    def __str__(self):
        return self.title


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    user_pw = models.CharField(max_length=100)
    com_num = models.IntegerField()
    com_name = models.CharField(max_length=100)
    com_head = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_num = models.IntegerField()
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'User'
