# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def seed_ignorelist(apps, schema_editor):
    Ignorelist = apps.get_model("n4f2", "Ignorelist")
    sites = [
        "Henry Schein POC",
        "LUSA - NYX Cosmetics - DEV",
        "test_APAC",
        "Riachuelo DEV",
        "BBBY Test",
        "Stage Stores Testing",
        "IKEA NL Demo",
        "Ocean Demo",
        "Dental Cremer - DEV",
        "LUSA - Giorgio Armani Beauty - DEV",
        "LUSA - LOreal Paris USA - DEV",
        "Michael Kors CA - DEV",
        "Michael Kors US - DEV",
        "Ocean Develop",
        "Cognizant Experience Zone",
        "Accenture - demandware2"
    ]
    for site in sites:
        verify = Ignorelist.objects.filter(site_name=site)
        if verify.exists():
            print(verify[0].site_name + " already exists. Skipping")
        else:
            s = Ignorelist(site_name = site)
            s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('n4f2', '0002_ignorelist'),
    ]

    operations = [
        migrations.RunPython(seed_ignorelist)
    ]
