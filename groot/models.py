from django.db import models

# Create your models here.
from django.forms import SelectDateWidget

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    user_pw = models.CharField(max_length=100)
    com_num = models.CharField(max_length=20)
    com_name = models.CharField(max_length=100)
    com_head = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=20)
    homepage = models.CharField(max_length=100)
    c_date = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'User'


class Certificate(models.Model):
    cert_idx = models.CharField(primary_key=True, max_length=100)
    enroll_idx = models.ForeignKey('Enrollment', models.DO_NOTHING, db_column='enroll_idx')
    cont_idx = models.ForeignKey('Contract', models.DO_NOTHING, db_column='cont_idx', blank=True, null=True)
    term = models.IntegerField()
    end_date = models.DateTimeField()
    c_date = models.DateTimeField(blank=True, null=True)
    cert_status = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'Certificate'


class Contract(models.Model):
    cont_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey('Enrollment', models.DO_NOTHING, db_column='enroll_idx')
    user = models.ForeignKey('User', models.DO_NOTHING)
    term = models.IntegerField()
    reason = models.TextField()
    refused_reason = models.TextField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()
    accept_date = models.DateTimeField(blank=True, null=True)
    contract_tx = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Contract'


class DocVf(models.Model):
    doc_idx = models.AutoField(primary_key=True)
    file_idx = models.ForeignKey('File', models.DO_NOTHING, db_column='file_idx')
    up_hash = models.CharField(max_length=100)
    result = models.IntegerField()
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Doc_vf'

class SortMst(models.Model):
    sort_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100 )

    def __str__(self):
        return '(' + str(self.sort_idx) + ')' + self.title

    class Meta:
        managed = False
        db_table = 'Sort_MST'



class Enrollment(models.Model):
    enroll_idx = models.AutoField(primary_key=True)
    sort_idx = models.ForeignKey('SortMst', models.DO_NOTHING, db_column='sort_idx')
    user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=100)
    term = models.PositiveIntegerField(default=1)
    summary = models.TextField(blank=True, null=True)
    refused_reason = models.TextField(blank=True, null=True)
    agree_status = models.IntegerField(blank=True, null=True)
    enroll_status = models.IntegerField(null=True)
    extend_status = models.CharField(max_length=50,blank=True, null=True)
    expire_status = models.CharField(max_length=50,blank=True, null=True)
    enroll_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    enroll_tx = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField(auto_now_add=True)


    class Meta:
        managed = False
        db_table = 'Enrollment'
        unique_together = (('enroll_idx', 'sort_idx'),)

class Update(models.Model):
    update_idx = models.IntegerField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    status = models.IntegerField()
    reason = models.TextField()
    accept_date = models.DateTimeField(blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Update'

class Extend(models.Model):
    extend_idx = models.IntegerField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    term = models.PositiveIntegerField(default=1)
    status = models.IntegerField()
    reason = models.TextField()
    refused_reason = models.TextField(blank=True, null=True)
    extend_tx = models.CharField(max_length=100,blank=True, null=True)
    accept_date = models.DateTimeField(blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Extend'

class Expire(models.Model):
    expire_idx = models.IntegerField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    status = models.IntegerField()
    reason = models.TextField()
    refused_reason = models.TextField(blank=True, null=True)
    accept_date = models.DateTimeField(blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Expire'


class Similarity(models.Model):
    similarity_idx = models.IntegerField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    summary_value = models.CharField(max_length=100, blank=True, null=True)
    keyword_value = models.CharField(max_length=100, blank=True, null=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Similarity'


class File(models.Model):
    file_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    folder_path = models.CharField(max_length=300)
    file_hash= models.CharField(max_length=100)
    file_name = models.CharField(max_length=100, null=True)
    c_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'File'

class Attribute(models.Model):
    attribute_idx = models.IntegerField(primary_key=True)
    amount = models.IntegerField()
    s_date = models.DateTimeField()
    m_date = models.DateTimeField()
    inode = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=100)
    file_idx = models.ForeignKey('File', models.DO_NOTHING, db_column='file_idx')

    class Meta:
        managed = False
        db_table = 'Attribute'

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





