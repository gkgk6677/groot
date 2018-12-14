# Generated by Django 2.1.2 on 2018-12-14 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id_idx', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=100)),
                ('user_pw', models.CharField(max_length=100)),
                ('com_num', models.IntegerField()),
                ('com_name', models.CharField(max_length=100)),
                ('com_head', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('phone_num', models.IntegerField()),
                ('s_date', models.DateField()),
            ],
            options={
                'db_table': 'User',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='test',
            fields=[
                ('user_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('user_pw', models.CharField(max_length=50)),
                ('user_name', models.CharField(max_length=50)),
                ('c_date', models.DateTimeField()),
            ],
        ),
    ]