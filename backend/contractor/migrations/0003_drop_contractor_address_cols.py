from django.db import migrations


SQL_DROP_COLS = r'''
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS zip_code;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_zip_code;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_address;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_number;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_complement;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_neighborhood;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_city;
ALTER TABLE "Contractor" DROP COLUMN IF EXISTS contractor_st;
'''

SQL_RESTORE_COLS = r'''
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS zip_code varchar(10);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_zip_code varchar(10);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_address varchar(255);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_number varchar(20);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_complement varchar(255);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_neighborhood varchar(255);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_city varchar(255);
ALTER TABLE "Contractor" ADD COLUMN IF NOT EXISTS contractor_st varchar(2);
'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0002_rename_fk_column'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_DROP_COLS, reverse_sql=SQL_RESTORE_COLS),
    ]


