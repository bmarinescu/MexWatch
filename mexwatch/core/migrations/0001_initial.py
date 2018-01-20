# Generated by Django 2.0.1 on 2018-01-20 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('key_pub', models.CharField(max_length=24)),
                ('key_secret', models.CharField(max_length=48)),
            ],
        ),
    ]
