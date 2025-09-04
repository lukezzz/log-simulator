from sqlalchemy.orm import declarative_base
from .settings import cfg
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
import ssl
import os


async def create_pg_engine() -> AsyncEngine:
    # Check if SSL is enabled through environment variables
    if cfg.DB_SSL_ENABLED:
        # Create an SSLContext with proper security defaults
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # Enable hostname verification by default for security
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Load CA certificate if specified
        if cfg.DB_SSL_ROOT_CERT and os.path.exists(cfg.DB_SSL_ROOT_CERT):
            ssl_context.load_verify_locations(cafile=cfg.DB_SSL_ROOT_CERT)
        
        # Configure SSL mode based on DB_SSL_MODE setting
        if cfg.DB_SSL_MODE == "verify-ca":
            # Only verify CA certificate, but keep hostname verification enabled for security
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        elif cfg.DB_SSL_MODE == "verify-full":
            # Verify CA certificate and hostname (already set above)
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        elif cfg.DB_SSL_MODE == "require":
            # Require SSL but with full verification for security
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            # Default to secure settings
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Note: No client certificate loading for CA-only verification
        # Client certificates were used for mutual TLS authentication

        # Caution: use this in development only
        # ssl_context.check_hostname = False
        # ssl_context.verify_mode = ssl.CERT_NONE
        
        engine = create_async_engine(cfg.APP_DB_URI, connect_args={"ssl": ssl_context})
    else:
        # Non-SSL connection
        engine = create_async_engine(cfg.APP_DB_URI)

    return engine


Base = declarative_base()
