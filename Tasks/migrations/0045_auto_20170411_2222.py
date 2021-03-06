# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 02:22
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Tasks', '0044_auto_20170315_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkCharts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AnnualFileLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedAnnual.csv')),
                ('QuarterFileLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\BBG_CombinedQuarterly.csv')),
                ('TickersFileLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\TickerList.xlsx')),
                ('BaseSaveLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\PeerGroups\\BenchmarkCharts')),
                ('HistoricalChartBaseSaveLoc', models.TextField(default='C:\\Users\\gcole\\Documents\\BloombergData\\PeerGroups\\CompanyData\\')),
                ('IncludeLTMData', models.BooleanField(default=True)),
                ('ChartColumns', models.TextField(default="'SalesGrowth', 'EBITDAGrowth', 'ROTA', 'UnleveragedFCFROTA', 'ROA', 'UnleveragedFCFROA', 'TangibleAsset_Coverage', 'Adj_EBITDA_Margin', 'Gross_Margin', 'TotalLeverageAdj', 'NetLeverageAdj', 'EBITDA_to_Interest', 'CapEx_to_AdjEBITDA'")),
                ('BaseCompany', models.TextField(default='XOM US')),
                ('CompanyList', models.TextField(default="'CVX US', 'OXY US'")),
                ('IncludeBaseCompanyInPeers', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='createnewdatapullfile',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 302097, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_chargeoffs',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 305600, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_cleancombinedapplications',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 306100, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_combine_lc_app_files',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 305099, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='lendingclub_initial_new_origination_data_cleaning',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 305099, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='mergenewcompanydata',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 302597, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='updatingcompanydatastepone',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 301097, tzinfo=utc), verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='updatingcompanydatasteptwo',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 12, 2, 22, 3, 301597, tzinfo=utc), verbose_name='date published'),
        ),
    ]
