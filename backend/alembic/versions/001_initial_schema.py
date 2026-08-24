"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Contents
    op.create_table(
        'contents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('text_hash', sa.String(64), index=True, nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('clean_text', sa.Text(), nullable=False),
        sa.Column('source_label', sa.String(50), nullable=True),
        sa.Column('domain', sa.String(50), default='general'),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('word_count', sa.Integer(), default=0),
        sa.Column('char_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Detection Results
    op.create_table(
        'detection_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('contents.id'), nullable=False, index=True),
        sa.Column('classification', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('ai_probability', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('gltr_stats', sa.JSON(), nullable=True),
        sa.Column('watermark_status', sa.String(30), default='NOT_SUPPORTED'),
        sa.Column('watermark_details', sa.JSON(), nullable=True),
        sa.Column('statistical_features', sa.JSON(), nullable=True),
        sa.Column('indicators', sa.JSON(), nullable=True),
        sa.Column('is_heuristic_fallback', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Platforms
    op.create_table(
        'platforms',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('platform_type', sa.String(50), default='microblogging'),
        sa.Column('risk_weight', sa.Float(), default=1.0),
        sa.Column('description', sa.String(255), default=''),
        sa.Column('icon_name', sa.String(50), default='share'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Synthetic Accounts
    op.create_table(
        'synthetic_accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('platform_id', sa.String(36), sa.ForeignKey('platforms.id'), nullable=False),
        sa.Column('pseudonym_handle', sa.String(100), nullable=False, index=True),
        sa.Column('account_age_days', sa.Integer(), default=30),
        sa.Column('bot_probability', sa.Float(), default=0.0),
        sa.Column('follower_count', sa.Integer(), default=100),
        sa.Column('following_count', sa.Integer(), default=100),
        sa.Column('is_coordinated_actor', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Campaigns
    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('objective', sa.String(255), default=''),
        sa.Column('target_narrative', sa.Text(), default=''),
        sa.Column('status', sa.String(20), default='ACTIVE'),
        sa.Column('risk_score', sa.Float(), default=0.0),
        sa.Column('gnn_risk_score', sa.Float(), default=0.0),
        sa.Column('explainability_reasons', sa.JSON(), nullable=True),
        sa.Column('total_events', sa.Integer(), default=0),
        sa.Column('total_reach', sa.Integer(), default=0),
        sa.Column('total_platforms', sa.Integer(), default=1),
        sa.Column('velocity_events_per_hour', sa.Float(), default=0.0),
        sa.Column('branching_factor', sa.Float(), default=1.0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Posts
    op.create_table(
        'posts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('platform_id', sa.String(36), sa.ForeignKey('platforms.id'), nullable=False),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('synthetic_accounts.id'), nullable=False),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('contents.id'), nullable=False),
        sa.Column('parent_post_id', sa.String(36), sa.ForeignKey('posts.id'), nullable=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('post_type', sa.String(30), default='ORIGINAL'),
        sa.Column('likes', sa.Integer(), default=0),
        sa.Column('reshares', sa.Integer(), default=0),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Simulation Runs
    op.create_table(
        'simulation_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('status', sa.String(20), default='STOPPED'),
        sa.Column('event_rate_per_sec', sa.Float(), default=1.0),
        sa.Column('total_events_emitted', sa.Integer(), default=0),
        sa.Column('duration_seconds', sa.Integer(), default=120),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('paused_at', sa.DateTime(), nullable=True),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Propagation Events
    op.create_table(
        'propagation_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('simulation_id', sa.String(36), sa.ForeignKey('simulation_runs.id'), nullable=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('event_type', sa.String(30), nullable=False),
        sa.Column('source_post_id', sa.String(36), nullable=True),
        sa.Column('target_post_id', sa.String(36), nullable=True),
        sa.Column('account_id', sa.String(36), nullable=False),
        sa.Column('platform_id', sa.String(36), nullable=False),
        sa.Column('content_id', sa.String(36), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
    )

    # Model Metadata
    op.create_table(
        'model_metadata',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('operational_status', sa.String(30), default='TRAINED'),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('limitations', sa.Text(), default=''),
        sa.Column('dataset_info', sa.Text(), default=''),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('model_metadata')
    op.drop_table('propagation_events')
    op.drop_table('simulation_runs')
    op.drop_table('posts')
    op.drop_table('campaigns')
    op.drop_table('synthetic_accounts')
    op.drop_table('platforms')
    op.drop_table('detection_results')
    op.drop_table('contents')
