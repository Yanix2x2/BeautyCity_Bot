# Generated by Django 5.2.3 on 2025-06-29 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0009_remove_master_salon"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="is_paid",
            field=models.BooleanField(
                default=False, verbose_name="Оплачено через бота"
            ),
        ),
    ]
