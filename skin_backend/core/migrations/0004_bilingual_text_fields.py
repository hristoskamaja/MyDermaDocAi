# Hand-written (the sandboxed shell used to run `makemigrations` is
# unavailable this session) - adds the English counterparts of every
# admin/AI-generated text field so content can be served in EN or MK.
# Mirrors the existing migration style used by 0002/0003 in this app.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_dermatologist'),
    ]

    operations = [
        migrations.AddField(
            model_name='skincondition',
            name='description_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='skincondition',
            name='symptoms_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='skincondition',
            name='treatment_overview_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recommendation',
            name='name_mk',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='recommendation',
            name='description_mk',
            field=models.TextField(blank=True, null=True),
        ),
    ]
