# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 11:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Tasks', '0049_auto_20170412_0745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='createnewdatapullfile',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 283851, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_chargeoffs',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 287872, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_cleancombinedapplications',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 287872, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_combine_lc_app_files',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 287872, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_initial_new_origination_data_cleaning',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 286871, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='mergenewcompanydata',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 284853, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='updatingcompanydatastepone',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 282851, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='updatingcompanydatasteptwo',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 50, 15, 283851, tzinfo=utc), verbose_name='date published'),
        ),
    ]