# Generated by Django 4.0.4 on 2022-05-18 05:09

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AdayaApp', '0005_termsandconditions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='termsandconditions',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
