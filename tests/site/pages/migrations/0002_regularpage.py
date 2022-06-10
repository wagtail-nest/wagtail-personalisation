# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION>=(3,0):
    import wagtail.fields as wagtail_fields
else:
    import wagtail.core.fields as wagtail_fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0001_initial'),
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegularPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),  # noqa: E501
                ('subtitle', models.CharField(blank=True, default='', max_length=255)),
                ('body', wagtail_fields.RichTextField(blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
