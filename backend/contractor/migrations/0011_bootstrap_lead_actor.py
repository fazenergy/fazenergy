from django.db import migrations


SQL_APPLY = r'''
DO $$
BEGIN
    -- Cria tabela ContractorProposalLeadActor, se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema='public' AND table_name='ContractorProposalLeadActor'
    ) THEN
        EXECUTE '
            CREATE TABLE "ContractorProposalLeadActor" (
                id bigserial PRIMARY KEY,
                proposal_id bigint NOT NULL,
                actor varchar(20) NOT NULL,
                legal_name varchar(255) NULL,
                name varchar(255) NULL,
                cpf_cnpj varchar(20) NULL,
                cellphone varchar(20) NULL,
                email varchar(254) NULL,
                zip_code varchar(10) NULL,
                address varchar(255) NULL,
                number varchar(20) NULL,
                complement varchar(255) NULL,
                neighborhood varchar(255) NULL,
                city varchar(255) NULL,
                st varchar(2) NULL
            )';
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name='leadactor_proposal_fk'
        ) THEN
            EXECUTE 'ALTER TABLE "ContractorProposalLeadActor" ADD CONSTRAINT leadactor_proposal_fk FOREIGN KEY (proposal_id) REFERENCES "ContractorProposal" (id) DEFERRABLE INITIALLY DEFERRED';
        END IF;
    END IF;
END
$$;
'''

SQL_REVERSE = r'''-- no-op'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0010_bootstrap_legacy_tables'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


