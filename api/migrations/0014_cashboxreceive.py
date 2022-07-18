# Generated by Django 3.1.4 on 2022-03-13 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20220310_1121'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashboxReceive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sum', models.PositiveBigIntegerField()),
                ('currency', models.CharField(choices=[("so'm", "so'm"), ('dollar', 'dollar')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('filial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.filial')),
            ],
        ),
    ]