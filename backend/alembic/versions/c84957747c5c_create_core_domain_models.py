"""create core domain models

Revision ID: c84957747c5c
Revises: b73846636b4b
Create Date: 2026-10-09 01:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c84957747c5c'
down_revision: Union[str, Sequence[str], None] = 'b73846636b4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Applicant Profiles
    op.create_table(
        'applicant_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('entity_name', sa.String(length=255), nullable=True),
        sa.Column('udyam_registration_no', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('pincode', sa.String(length=20), nullable=True),
        sa.Column('identity_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('business_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('financials_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applicant_profiles_user_id'), 'applicant_profiles', ['user_id'], unique=True)
    op.create_index(op.f('ix_applicant_profiles_udyam_registration_no'), 'applicant_profiles', ['udyam_registration_no'], unique=False)

    # 2. Loan Requirements
    op.create_table(
        'loan_requirements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('purpose', sa.String(length=255), nullable=False),
        sa.Column('requested_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tenure_months', sa.Integer(), nullable=False),
        sa.Column('preferred_interest_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('collateral_available', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('collateral_type', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loan_requirements_user_id'), 'loan_requirements', ['user_id'], unique=False)

    # 3. Financial Profiles
    op.create_table(
        'financial_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('monthly_income', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('monthly_expenses', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('existing_debt_monthly_obligation', sa.Numeric(precision=15, scale=2), nullable=False, server_default=sa.text('0.00')),
        sa.Column('remaining_cash_flow', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_assets', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_liabilities', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('debt_service_coverage_ratio', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default=sa.text("'SELF_DECLARED'")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_profiles_user_id'), 'financial_profiles', ['user_id'], unique=False)

    # 4. Schemes
    op.create_table(
        'schemes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('purpose', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('min_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('max_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('min_tenure_months', sa.Integer(), nullable=True),
        sa.Column('max_tenure_months', sa.Integer(), nullable=True),
        sa.Column('interest_rate_min', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('interest_rate_max', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('subsidy_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('required_documents', sa.JSON(), nullable=True),
        sa.Column('eligibility_criteria', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schemes_code'), 'schemes', ['code'], unique=True)
    op.create_index(op.f('ix_schemes_name'), 'schemes', ['name'], unique=False)

    # 5. Applications
    op.create_table(
        'applications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_number', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('scheme_id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=True),
        sa.Column('requested_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column('readiness_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['scheme_id'], ['schemes.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_application_number'), 'applications', ['application_number'], unique=True)
    op.create_index(op.f('ix_applications_organization_id'), 'applications', ['organization_id'], unique=False)
    op.create_index(op.f('ix_applications_scheme_id'), 'applications', ['scheme_id'], unique=False)
    op.create_index(op.f('ix_applications_status'), 'applications', ['status'], unique=False)
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)

    # 6. Documents
    op.create_table(
        'documents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'PROCESSING'")),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('review_required', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_application_id'), 'documents', ['application_id'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_application_id'), table_name='documents')
    op.drop_table('documents')

    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_status'), table_name='applications')
    op.drop_index(op.f('ix_applications_scheme_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_organization_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_application_number'), table_name='applications')
    op.drop_table('applications')

    op.drop_index(op.f('ix_schemes_name'), table_name='schemes')
    op.drop_index(op.f('ix_schemes_code'), table_name='schemes')
    op.drop_table('schemes')

    op.drop_index(op.f('ix_financial_profiles_user_id'), table_name='financial_profiles')
    op.drop_table('financial_profiles')

    op.drop_index(op.f('ix_loan_requirements_user_id'), table_name='loan_requirements')
    op.drop_table('loan_requirements')

    op.drop_index(op.f('ix_applicant_profiles_udyam_registration_no'), table_name='applicant_profiles')
    op.drop_index(op.f('ix_applicant_profiles_user_id'), table_name='applicant_profiles')
    op.drop_table('applicant_profiles')
