# Generated by Django 3.0.6 on 2020-05-24 16:59

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op_params', django.contrib.postgres.fields.jsonb.JSONField()),
                ('slug_name', models.SlugField(max_length=100)),
                ('is_initial', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('function', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_taskflow.Workflow')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('state', django.contrib.postgres.fields.jsonb.JSONField()),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_taskflow.Element')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_taskflow.Ticket')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug_name', models.SlugField(max_length=100)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dtflow_link_source', to='django_taskflow.Element')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dtflow_link_target', to='django_taskflow.Element')),
            ],
        ),
        migrations.AddField(
            model_name='element',
            name='operation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_taskflow.Operation'),
        ),
        migrations.AddField(
            model_name='element',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_taskflow.Workflow'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.UniqueConstraint(fields=('ticket', 'creation'), name='workflow_task_uniqueness'),
        ),
        migrations.AddConstraint(
            model_name='element',
            constraint=models.UniqueConstraint(fields=('workflow', 'slug_name'), name='uniqueness_workflow_slug'),
        ),
        migrations.AddConstraint(
            model_name='element',
            constraint=models.UniqueConstraint(condition=models.Q(is_initial=True), fields=('workflow',), name='unique_initial_element'),
        ),
    ]
