# Generated by Django 5.1.2 on 2024-11-10 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_end_date_task_importance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='importance',
            field=models.CharField(choices=[('Low', 'Low Priority (Complete within a month)'), ('Medium', 'Moderate Priority (Complete within two weeks)'), ('Urgent', 'High Priority (Complete within a few days)')], default='low', max_length=10),
        ),
    ]
