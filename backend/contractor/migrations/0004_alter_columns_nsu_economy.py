from django.db import migrations


SQL_APPLY = r'''
DO $$
BEGIN
    -- Remove nsu da tabela de propostas
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'nsu'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" DROP COLUMN nsu';
    END IF;

    -- Adiciona economy_thirty_years no resultado da proposta
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'economy_thirty_years'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" ADD COLUMN economy_thirty_years numeric(14,2) NULL';
    END IF;
END
$$;
'''

SQL_REVERSE = r'''
DO $$
BEGIN
    -- Recria nsu (rollback)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'nsu'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" ADD COLUMN nsu varchar(100)';
    END IF;

    -- Remove economy_thirty_years (rollback)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'economy_thirty_years'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" DROP COLUMN economy_thirty_years';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0003_drop_contractor_address_cols'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


