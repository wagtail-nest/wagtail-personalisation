# Generated by Django 2.0.5 on 2018-05-26 14:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtail_personalisation", "0018_segment_excluded_users"),
    ]

    operations = [
        migrations.AlterField(
            model_name="personalisablepagemetadata",
            name="segment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="page_metadata",
                to="wagtail_personalisation.Segment",
            ),
        ),
    ]
