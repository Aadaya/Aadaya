# Generated by Django 4.0.4 on 2022-05-17 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AdayaApp', '0003_product_gst15_product_gst18'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='ref_code',
        ),
    ]
