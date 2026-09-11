# Hand-written (the sandboxed shell used to run `makemigrations` is
# unavailable this session) - adds latitude/longitude to Dermatologist so
# "find a dermatologist" results can be sorted by proximity. Mirrors the
# existing migration style used by 0002/0003/0004 in this app.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_bilingual_text_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='dermatologist',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dermatologist',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
