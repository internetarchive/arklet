from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ark", "0002_allow_blank_ark_model_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE ark_ark ALTER COLUMN commitment SET DEFAULT ''"
        ),
        migrations.RunSQL(
            sql="ALTER TABLE ark_ark ALTER COLUMN metadata SET DEFAULT ''"
        ),
        migrations.RunSQL(sql="ALTER TABLE ark_ark ALTER COLUMN url SET DEFAULT ''"),
    ]
