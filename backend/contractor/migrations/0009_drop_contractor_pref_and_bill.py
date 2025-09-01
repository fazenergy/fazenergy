from django.db import migrations

SQL_APPLY = r'''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'preferred_property_type'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" DROP COLUMN preferred_property_type';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'last_electric_bill'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" DROP COLUMN last_electric_bill';
    END IF;
END
$$;
'''

SQL_REVERSE = r'''
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'preferred_property_type'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" ADD COLUMN preferred_property_type varchar(50) NULL';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Contractor' AND column_name = 'last_electric_bill'
    ) THEN
        EXECUTE 'ALTER TABLE "Contractor" ADD COLUMN last_electric_bill numeric(10,2) NULL';
    END IF;
END
$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0008_add_visits_to_proposal'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


