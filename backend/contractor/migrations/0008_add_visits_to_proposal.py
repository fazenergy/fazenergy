from django.db import migrations

SQL_APPLY = r'''
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'visit_1'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" ADD COLUMN visit_1 timestamp with time zone NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'visit_2'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" ADD COLUMN visit_2 timestamp with time zone NULL';
    END IF;
END
$$;
'''

SQL_REVERSE = r'''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'visit_1'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" DROP COLUMN visit_1';
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'visit_2'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" DROP COLUMN visit_2';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0007_drop_contractor_energy_fields'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


