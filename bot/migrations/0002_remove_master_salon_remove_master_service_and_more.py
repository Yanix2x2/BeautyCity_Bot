# Generated by Django 5.2.3 on 2025-06-25 11:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="master",
            name="salon",
        ),
        migrations.RemoveField(
            model_name="master",
            name="service",
        ),
        migrations.AddField(
            model_name="master",
            name="salon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bot.salon",
                verbose_name="Салон",
            ),
        ),
        migrations.AddField(
            model_name="master",
            name="service",
            field=models.CharField(
                choices=[
                    ("Hair", "Стилист"),
                    ("Nail", "Ноготочки"),
                    ("Makeup", "Макияж"),
                ],
                default="Неизвестно",
                max_length=10,
                verbose_name="Услуга",
            ),
            preserve_default=False,
        ),
    ]
