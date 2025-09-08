from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0011_add_revo_payload_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "ContractorProposalResult" DROP COLUMN IF EXISTS response_payload_post;',
            reverse_sql='ALTER TABLE "ContractorProposalResult" ADD COLUMN response_payload_post JSONB NULL;'
        ),
    ]


