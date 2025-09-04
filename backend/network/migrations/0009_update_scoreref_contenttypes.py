from django.db import migrations


def migrate_contenttypes_app_label(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ScoreReference = apps.get_model('network', 'ScoreReference')

    try:
        ct_prospect = ContentType.objects.get(app_label='prospect', model='proposal')
    except ContentType.DoesNotExist:
        ct_prospect = None

    try:
        ct_contractor = ContentType.objects.get(app_label='contractor', model='proposal')
    except ContentType.DoesNotExist:
        ct_contractor = None

    if ct_prospect and ct_contractor:
        ScoreReference.objects.filter(content_type=ct_prospect).update(content_type=ct_contractor)


def reverse_noop(apps, schema_editor):
    # Sem reversão automática
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_rename_network_sc_status_idx_scorerefere_status_a311bd_idx'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(migrate_contenttypes_app_label, reverse_noop),
    ]


