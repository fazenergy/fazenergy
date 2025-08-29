from django.db import migrations


SQL_APPLY = r'''
-- Adiciona colunas JSONB para guardar payloads
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'request_payload'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" ADD COLUMN request_payload jsonb NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'response_payload'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" ADD COLUMN response_payload jsonb NULL';
    END IF;
END
$$;
'''

SQL_REVERSE = r'''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'request_payload'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" DROP COLUMN request_payload';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'response_payload'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" DROP COLUMN response_payload';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0004_alter_columns_nsu_economy'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


