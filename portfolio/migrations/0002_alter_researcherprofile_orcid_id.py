from django.db import migrations, models


def empty_orcid_to_null(apps, schema_editor):
    """Postgres unique constraint treats '' as a value; normalize to NULL."""
    ResearcherProfile = apps.get_model("portfolio", "ResearcherProfile")
    ResearcherProfile.objects.filter(orcid_id="").update(orcid_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(empty_orcid_to_null, migrations.RunPython.noop),
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
