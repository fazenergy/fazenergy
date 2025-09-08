from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0010_rename_contract_duration_months_to_contract_duration'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "ContractorProposalResult" '
                'ADD COLUMN IF NOT EXISTS response_payload_post JSONB NULL, '
                'ADD COLUMN IF NOT EXISTS response_payload_put JSONB NULL;'
            ),
            reverse_sql=(
                'ALTER TABLE "ContractorProposalResult" '
                'DROP COLUMN IF EXISTS response_payload_post, '
                'DROP COLUMN IF EXISTS response_payload_put;'
            )
        ),
    ]


