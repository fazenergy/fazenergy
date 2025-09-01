from django.db import migrations

SQL_APPLY = r'''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'last_energy_provider_id'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" DROP COLUMN last_energy_provider_id';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'last_energy_provider_name'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" DROP COLUMN last_energy_provider_name';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'reference_code'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" DROP COLUMN reference_code';
    END IF;
END
$$;
'''

SQL_REVERSE = r'''
DO $$
BEGIN
    -- Apenas recria as colunas com tipos genéricos (se necessário)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'last_energy_provider_id'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" ADD COLUMN last_energy_provider_id integer NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'last_energy_provider_name'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" ADD COLUMN last_energy_provider_name varchar(100) NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'reference_code'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" ADD COLUMN reference_code varchar(100) NULL';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0006_adjust_result_fields'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


