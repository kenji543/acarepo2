from django.db import migrations


def empty_orcid_to_null(apps, schema_editor):
    ResearcherProfile = apps.get_model("portfolio", "ResearcherProfile")
    ResearcherProfile.objects.filter(orcid_id="").update(orcid_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0002_alter_researcherprofile_orcid_id"),
    ]

    operations = [
        migrations.RunPython(empty_orcid_to_null, migrations.RunPython.noop),
    ]
