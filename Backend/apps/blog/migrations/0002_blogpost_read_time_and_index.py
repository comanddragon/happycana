# Generated to match apps/blog/models.py changes: adds the stored
# `read_time` field (computed once in BlogPost.save() instead of per
# request) and a composite index on (is_published, -published_at), which
# is what every list query filters and sorts by. Written by hand since
# this sandbox has no live DB/Django install to run makemigrations
# against — verify with `python manage.py makemigrations --check` before
# merging.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='read_time',
            field=models.CharField(blank=True, default='', db_default='', max_length=20),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['is_published', '-published_at'], name='blog_published_idx'),
        ),
    ]
