from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="researcherprofile",
            name="orcid_id",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="ORCID identifier",
                max_length=50,
                null=True,
                unique=True,
            ),
        ),
    ]
