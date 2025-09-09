from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0010_rename_contract_duration_months_to_contract_duration'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ContractorProposalResult') THEN
                    ALTER TABLE "ContractorProposalResult" 
                    ADD COLUMN IF NOT EXISTS response_payload_post JSONB NULL, 
                    ADD COLUMN IF NOT EXISTS response_payload_put JSONB NULL;
                END IF;
            END $$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ContractorProposalResult') THEN
                    ALTER TABLE "ContractorProposalResult" 
                    DROP COLUMN IF EXISTS response_payload_post, 
                    DROP COLUMN IF EXISTS response_payload_put;
                END IF;
            END $$;
            """
        ),
    ]


