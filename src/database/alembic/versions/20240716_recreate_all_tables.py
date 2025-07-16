"""recreate all tables for new transparent business logic

Revision ID: 20240716_recreate_all_tables
Revises: ee48eb4ce95e
Create Date: 2024-07-16
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
import datetime

revision = '20240716_recreate_all_tables'
down_revision = 'ee48eb4ce95e'
branch_labels = None
depends_on = None

def upgrade():
    # Удаляем старые таблицы (если существуют)
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    op.execute('DROP TABLE IF EXISTS products CASCADE')
    op.execute('DROP TABLE IF EXISTS categories CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    op.execute('DROP TABLE IF EXISTS sessions CASCADE')

    # Создаём новые таблицы
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('telegram_id', sa.String, unique=True, nullable=False, index=True),
        sa.Column('username', sa.String),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column('email', sa.String),
        sa.Column('phone', sa.String),
        sa.Column('extra_data', pg.JSONB),
    )
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, unique=True, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.utcnow),
    )
    op.create_table(
        'products',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, index=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id', ondelete='CASCADE'), index=True),
        sa.Column('description', sa.Text),
        sa.Column('price', sa.Integer, index=True),
        sa.Column('image_url', sa.String),
        sa.Column('specs', pg.JSONB),  # Характеристики устройства (как JSON)
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.utcnow),
    )
    op.create_index('ix_product_name', 'products', ['name'])
    op.create_index('ix_product_price', 'products', ['price'])
    op.create_index('ix_product_category_id', 'products', ['category_id'])
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('role', sa.String),  # 'user' или 'assistant'
        sa.Column('message', sa.Text),
        sa.Column('timestamp', sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column('session_id', sa.String),
    )
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('started_at', sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column('ended_at', sa.DateTime),
        sa.Column('extra_data', pg.JSONB),
    )

def downgrade():
    op.drop_table('sessions')
    op.drop_table('messages')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('users') 