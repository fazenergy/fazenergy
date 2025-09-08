from django.db import migrations


SQL_APPLY = r'''
DO $$
BEGIN
    -- Cria tabela Contractor, se não existir (estrutura mínima atual)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'Contractor'
    ) THEN
        EXECUTE '
            CREATE TABLE "Contractor" (
                id bigserial PRIMARY KEY,
                licensed_id bigint NOT NULL,
                lead_name varchar(255) NOT NULL,
                email varchar(254) NOT NULL,
                cellphone varchar(20) NOT NULL,
                person_type varchar(2) NOT NULL DEFAULT ''PF'',
                fiscal_number varchar(20) NULL,
                legal_name varchar(255) NULL,
                status varchar(100) NOT NULL DEFAULT ''Novo'',
                usr_record varchar(50) NOT NULL,
                dtt_record timestamp with time zone NOT NULL DEFAULT now(),
                usr_update varchar(50) NULL,
                dtt_update timestamp with time zone NOT NULL DEFAULT now()
            )';
        -- FK para Licensed (sem cascade)
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = 'contractor_licensed_fk'
        ) THEN
            EXECUTE 'ALTER TABLE "Contractor" ADD CONSTRAINT contractor_licensed_fk FOREIGN KEY (licensed_id) REFERENCES "Licensed" (id) DEFERRABLE INITIALLY DEFERRED';
        END IF;
    END IF;

    -- Cria tabela ContractorProposal, se não existir (estrutura mínima atual)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'ContractorProposal'
    ) THEN
        EXECUTE '
            CREATE TABLE "ContractorProposal" (
                id bigserial PRIMARY KEY,
                contractor_id bigint NOT NULL,
                product_id bigint NULL,
                reference_code varchar(50) NOT NULL,
                zip_code varchar(10) NOT NULL,
                address varchar(255) NOT NULL,
                number varchar(20) NULL,
                complement varchar(255) NULL,
                neighborhood varchar(255) NULL,
                city varchar(255) NOT NULL,
                state varchar(2) NOT NULL,
                contract_person varchar(100) NOT NULL,
                property_type varchar(50) NULL,
                owner varchar(100) NOT NULL,
                is_owner_self boolean NOT NULL DEFAULT true,
                seller_email varchar(254) NULL,
                cpf_cnpj varchar(20) NULL,
                legal_name varchar(255) NULL,
                email varchar(254) NULL,
                electric_bill_amount numeric(12,2) NULL,
                consumer_unit varchar(100) NULL,
                consumer_group varchar(100) NULL,
                monthly_consumption jsonb NULL,
                energy_provider_id integer NULL,
                energy_provider_name varchar(100) NULL,
                request_payload jsonb NULL,
                visit_1 timestamp with time zone NULL,
                visit_2 timestamp with time zone NULL,
                status varchar(100) NOT NULL DEFAULT ''Aguardando'',
                usr_record varchar(50) NOT NULL,
                dtt_record timestamp with time zone NOT NULL DEFAULT now(),
                dtt_expired timestamp with time zone NULL,
                usr_update varchar(50) NULL,
                dtt_update timestamp with time zone NOT NULL DEFAULT now()
            )';
        -- FKs
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = 'contractorproposal_contractor_fk'
        ) THEN
            EXECUTE 'ALTER TABLE "ContractorProposal" ADD CONSTRAINT contractorproposal_contractor_fk FOREIGN KEY (contractor_id) REFERENCES "Contractor" (id) DEFERRABLE INITIALLY DEFERRED';
        END IF;
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = 'contractorproposal_product_fk'
        ) THEN
            EXECUTE 'ALTER TABLE "ContractorProposal" ADD CONSTRAINT contractorproposal_product_fk FOREIGN KEY (product_id) REFERENCES "Product" (id) DEFERRABLE INITIALLY DEFERRED';
        END IF;
    END IF;

    -- Cria tabela ContractorProposalResult, se não existir (estrutura mínima atual)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'ContractorProposalResult'
    ) THEN
        EXECUTE '
            CREATE TABLE "ContractorProposalResult" (
                id bigserial PRIMARY KEY,
                proposal_id bigint NOT NULL,
                contract_type varchar(100) NOT NULL,
                contract_duration_months integer NULL,
                discount_percentage numeric(6,2) NULL,
                discount_amount numeric(12,2) NULL,
                economy_thirty_years numeric(14,2) NULL,
                installment_amount numeric(12,2) NOT NULL,
                total_installments integer NOT NULL,
                total_amount numeric(12,2) NOT NULL,
                kwp numeric(6,2) NULL,
                kwh_annual numeric(10,2) NULL,
                required_area numeric(12,2) NULL,
                qty_modules integer NULL,
                energy_provider_id integer NULL,
                energy_provider_name varchar(255) NULL,
                provider_costs numeric(12,2) NULL,
                revo_costs numeric(12,2) NULL,
                electric_bill_value numeric(12,2) NULL,
                consumer_unit varchar(50) NULL,
                consumer_group varchar(100) NULL,
                proposal_expiration_at timestamp with time zone NOT NULL,
                status varchar(50) NOT NULL DEFAULT ''Ativo'',
                usr_record varchar(50) NOT NULL,
                dtt_record timestamp with time zone NOT NULL DEFAULT now(),
                response_payload jsonb NULL
            )';
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = 'contractorproposalresult_proposal_fk'
        ) THEN
            EXECUTE 'ALTER TABLE "ContractorProposalResult" ADD CONSTRAINT contractorproposalresult_proposal_fk FOREIGN KEY (proposal_id) REFERENCES "ContractorProposal" (id) DEFERRABLE INITIALLY DEFERRED';
        END IF;
    END IF;
END
$$;
'''

SQL_REVERSE = r'''-- no-op'''


class Migration(migrations.Migration):

    dependencies = [
        ('contractor', '0009_drop_contractor_pref_and_bill'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_APPLY, reverse_sql=SQL_REVERSE),
    ]


