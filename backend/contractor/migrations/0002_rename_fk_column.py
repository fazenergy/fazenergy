from django.db import migrations


RENAME_TO_CONTRACTOR_ID = r'''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'prospect_id'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" RENAME COLUMN prospect_id TO contractor_id';
    END IF;
END
$$;
'''

RENAME_TO_PROSPECT_ID = r'''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ContractorProposal' AND column_name = 'contractor_id'
    ) THEN
        EXECUTE 'ALTER TABLE "ContractorProposal" RENAME COLUMN contractor_id TO prospect_id';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql=RENAME_TO_CONTRACTOR_ID, reverse_sql=RENAME_TO_PROSPECT_ID),
    ]


