from django.db import migrations, models

import extra_settings.fields


class Migration(migrations.Migration):
    dependencies = [
        ("extra_settings", "0002_auto_20200826_1714"),
    ]

    operations = [
        migrations.AlterField(
            model_name="setting",
            name="value_file",
            field=models.FileField(
                blank=True,
                upload_to=extra_settings.fields.upload_to_files,
                verbose_name="Value",
            ),
        ),
        migrations.AlterField(
            model_name="setting",
            name="value_image",
            field=models.FileField(
                blank=True,
                upload_to=extra_settings.fields.upload_to_images,
                verbose_name="Value",
            ),
        ),
    ]
