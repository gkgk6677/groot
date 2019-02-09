# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Certificate(models.Model):
    cert_idx = models.CharField(primary_key=True, max_length=100)
    enroll_idx = models.ForeignKey('Enrollment', models.DO_NOTHING, db_column='enroll_idx')
    cont_idx = models.ForeignKey('Contract', models.DO_NOTHING, db_column='cont_idx', blank=True, null=True)
    term = models.IntegerField()
    end_date = models.DateTimeField()
    c_date = models.DateTimeField(blank=True, null=True)
    cert_status = models.IntegerField()

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
    status = models.IntegerField()
    end_date = models.DateTimeField(blank=True, null=True)
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


class Enrollment(models.Model):
    enroll_idx = models.AutoField(primary_key=True)
    sort_idx = models.ForeignKey('SortMst', models.DO_NOTHING, db_column='sort_idx')
    user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=100)
    term = models.IntegerField()
    enroll_status = models.IntegerField()
    agree_status = models.IntegerField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    refused_reason = models.TextField(blank=True, null=True)
    enroll_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    enroll_tx = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Enrollment'
        unique_together = (('enroll_idx', 'sort_idx'),)


class Expire(models.Model):
    expire_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    status = models.IntegerField()
    reason = models.TextField()
    refused_reason = models.TextField(blank=True, null=True)
    accept_date = models.DateTimeField(blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Expire'


class Extend(models.Model):
    extend_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    term = models.IntegerField()
    status = models.IntegerField()
    reason = models.TextField()
    refused_reason = models.TextField(blank=True, null=True)
    accept_date = models.DateTimeField(blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Extend'


class File(models.Model):
    file_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    folder_path = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64)
    file_name = models.CharField(max_length=100)
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


class Similarity(models.Model):
    similarity_idx = models.IntegerField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    summary_value = models.CharField(max_length=100, blank=True, null=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Similarity'


class SortMst(models.Model):
    sort_idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Sort_MST'


class Update(models.Model):
    update_idx = models.AutoField(primary_key=True)
    enroll_idx = models.ForeignKey(Enrollment, models.DO_NOTHING, db_column='enroll_idx')
    status = models.IntegerField()
    reason = models.TextField()
    accept_date = models.DateTimeField(blank=True, null=True)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Update'


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    user_pw = models.CharField(max_length=100)
    com_num = models.IntegerField()
    com_name = models.CharField(max_length=100)
    com_head = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_num = models.IntegerField()
    homepage = models.CharField(max_length=100)
    c_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'User'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoFtpserverFtpusergroup(models.Model):
    name = models.CharField(unique=True, max_length=30)
    permission = models.CharField(max_length=8)
    home_dir = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_ftpserver_ftpusergroup'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
