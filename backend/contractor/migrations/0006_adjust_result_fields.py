from django.db import migrations

SQL_APPLY = r'''
DO $$
BEGIN
    -- Remover colunas antigas, se existirem
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'annual_economy'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" DROP COLUMN annual_economy';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'economy_in_three_years'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" DROP COLUMN economy_in_three_years';
    END IF;

    -- Ajustar tipo de required_area para numeric(12,2)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'required_area'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" ALTER COLUMN required_area TYPE numeric(12,2) USING required_area::numeric';
    ELSE
        -- Caso a coluna não exista, cria já com o tipo correto
        EXECUTE 'ALTER TABLE "ContractorProposalResult" ADD COLUMN required_area numeric(12,2) NULL';
    END IF;
END
$$;
'''

SQL_REVERSE = r'''
DO $$
BEGIN
    -- Não recriamos as colunas removidas automaticamente; apenas revertendo o tipo de required_area para integer
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposalResult' AND column_name = 'required_area'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposalResult" ALTER COLUMN required_area TYPE integer USING round(required_area)::integer';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0005_add_payload_jsonb'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]
