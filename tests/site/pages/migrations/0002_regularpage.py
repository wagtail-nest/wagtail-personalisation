# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models
from wagtail import fields


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0001_initial"),
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegularPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),  # noqa: E501
                ("subtitle", models.CharField(blank=True, default="", max_length=255)),
                ("body", fields.RichTextField(blank=True, default="")),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
