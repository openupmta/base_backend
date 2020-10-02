import os
import urllib

from sqlalchemy import create_engine

os_env = os.environ


class Config(object):
    SECRET_KEY = '3nF3Rn0'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))


class ProdConfig(Config):
    """Production configuration."""
    # app config
    ENV = 'production'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    HOST = '0.0.0.0'
    TEMPLATES_AUTO_RELOAD = False
    # SQL Alchemy config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+r'model\quitt.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    """Development configuration."""
    # app config
    ENV = 'development'
    DEBUG = True
    DEBUG_TB_ENABLED = True  # Disable Debug toolbar
    HOST = '0.0.0.0'
    TEMPLATES_AUTO_RELOAD = True
    # SQL Alchemy config

    # JWT Config
    JWT_SECRET_KEY = '1234567a@'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # USERNAME = 'sa'
    # PASSWORD = '1'
    # SERVER = '192.168.1.17\MSSQLSERVER15'
    # DATABASE = 'QUITT'
    # DRIVER = 'SQL Server Native Client 11.0'
    # SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}?trusted_connection=yes'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+r'model\quitt.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Test configuration."""
    # app config
    ENV = 'test'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    HOST = '0.0.0.0'
    TEMPLATES_AUTO_RELOAD = False
    # JWT Config
    # JWT_SECRET_KEY = '1234567a@'
    # JWT_BLACKLIST_ENABLED = True
    # JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    # SQL Alchemy config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+r'model\quitt.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False