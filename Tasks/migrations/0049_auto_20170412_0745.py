# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 11:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Tasks', '0048_auto_20170411_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinDataLoadFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AnnualFileLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv')),
                ('QuarterFileLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv')),
                ('TickersFileLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\TickerList.xlsx')),
            ],
        ),
        migrations.AlterField(
            model_name='createnewdatapullfile',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 299554, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_chargeoffs',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 303557, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_cleancombinedapplications',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 303557, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_combine_lc_app_files',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 302556, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_initial_new_origination_data_cleaning',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 302556, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='mergenewcompanydata',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 299554, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='updatingcompanydatastepone',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 298535, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='updatingcompanydatasteptwo',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 11, 45, 43, 298535, tzinfo=utc), verbose_name='date published'),
        ),
    ]
