from .api import routes
import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .config import settings
from .utils.logging import setup_logger, PROCESS, SUCCESS
from .utils.ascii_art import startup_animation
from .discovery.resource_tracker import ResourceTracker
from .discovery.advertiser import ResourceAdvertiser
from .discovery.golem_base_advertiser import GolemBaseAdvertiser
from .vm.multipass import MultipassProvider
from .vm.port_manager import PortManager
from .security.faucet import FaucetClient

logger = setup_logger(__name__)

app = FastAPI(title="VM on Golem Provider")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


async def setup_provider() -> None:
    """Setup and initialize the provider components."""
    try:
        # Create resource tracker first
        logger.process("🔄 Initializing resource tracker...")
        resource_tracker = ResourceTracker()
        app.state.resource_tracker = resource_tracker

        # Create provider with resource tracker and temporary port manager
        logger.process("🔄 Initializing VM provider...")
        provider = MultipassProvider(
            resource_tracker, port_manager=None)  # Will be set later

        try:
            # Initialize provider (without port operations)
            await asyncio.wait_for(provider.initialize(), timeout=30)

            # Store provider reference
            app.state.provider = provider
            app.state.proxy_manager = provider.proxy_manager

            # Initialize port manager first to verify all ports
            logger.process("🔄 Initializing port manager...")
            port_manager = PortManager(
                start_port=settings.PORT_RANGE_START,
                end_port=settings.PORT_RANGE_END,
                discovery_port=settings.PORT,
                skip_verification=settings.SKIP_PORT_VERIFICATION
            )

            if not await port_manager.initialize():
                raise RuntimeError("Port verification failed")

            # Store port manager references
            app.state.port_manager = port_manager
            provider.port_manager = port_manager
            app.state.proxy_manager.port_manager = port_manager

            # Now restore proxy configurations using only verified ports
            logger.process("🔄 Restoring proxy configurations...")
            await app.state.proxy_manager._load_state()

        except asyncio.TimeoutError:
            logger.error("Provider initialization timed out")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize provider: {e}")
            raise

        # Create advertiser
        logger.process("🔄 Initializing resource advertiser...")
        if settings.DISCOVERY_DRIVER == "golem-base":
            advertiser = GolemBaseAdvertiser(
                resource_tracker=resource_tracker
            )
            await advertiser.initialize()
        else:
            advertiser = ResourceAdvertiser(
                resource_tracker=resource_tracker,
                discovery_url=settings.DISCOVERY_URL,
                provider_id=settings.PROVIDER_ID
            )
        app.state.advertiser = advertiser

        logger.success(
            "✨ Provider setup complete and ready to accept requests")
    except Exception as e:
        logger.error(f"Failed to setup provider: {e}")
        # Attempt cleanup of any initialized components
        await cleanup_provider()
        raise


async def cleanup_provider() -> None:
    """Cleanup provider components."""
    cleanup_errors = []

    # Stop advertiser
    if hasattr(app.state, "advertiser"):
        try:
            await app.state.advertiser.stop()
            if hasattr(app.state, "advertiser_task"):
                app.state.advertiser_task.cancel()
                try:
                    await app.state.advertiser_task
                except asyncio.CancelledError:
                    pass
        except Exception as e:
            cleanup_errors.append(f"Failed to stop advertiser: {e}")

    # Cleanup proxy manager first to stop all proxy servers
    if hasattr(app.state, "proxy_manager"):
        try:
            await asyncio.wait_for(app.state.proxy_manager.cleanup(), timeout=30)
        except asyncio.TimeoutError:
            cleanup_errors.append("Proxy manager cleanup timed out")
        except Exception as e:
            cleanup_errors.append(f"Failed to cleanup proxy manager: {e}")

    # Cleanup provider
    if hasattr(app.state, "provider"):
        try:
            await asyncio.wait_for(app.state.provider.cleanup(), timeout=30)
        except asyncio.TimeoutError:
            cleanup_errors.append("Provider cleanup timed out")
        except Exception as e:
            cleanup_errors.append(f"Failed to cleanup provider: {e}")

    if cleanup_errors:
        error_msg = "\n".join(cleanup_errors)
        logger.error(f"Errors during cleanup:\n{error_msg}")
    else:
        logger.success("✨ Provider cleanup complete")


@app.on_event("startup")
async def startup_event():
    """Handle application startup."""
    try:
        # Display startup animation
        await startup_animation()
 
        # Initialize provider
        await setup_provider()

        # Check wallet balance and request funds if needed
        faucet_client = FaucetClient(
            faucet_url=settings.FAUCET_URL,
            captcha_url=settings.CAPTCHA_URL,
            captcha_api_key=settings.CAPTCHA_API_KEY,
        )
        await faucet_client.get_funds(settings.PROVIDER_ID)

        # Post initial advertisement and start advertising loop
        if isinstance(app.state.advertiser, GolemBaseAdvertiser):
            await app.state.advertiser.post_advertisement()
            app.state.advertiser_task = asyncio.create_task(app.state.advertiser.start_loop())

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Ensure proper cleanup
        await cleanup_provider()
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown."""
    await cleanup_provider()

# Import routes after app creation to avoid circular imports
app.include_router(routes.router, prefix="/api/v1")

# Export app for uvicorn
__all__ = ["app", "start"]


def check_requirements():
    """Check if all requirements are met."""
    try:
        # Import settings to trigger validation
        from .config import settings
        return True
    except Exception as e:
        logger.error(f"Requirements check failed: {e}")
        return False


async def verify_provider_port(port: int) -> bool:
    """Verify that the provider port is available for binding.

    Args:
        port: The port to verify

    Returns:
        bool: True if the port is available, False otherwise
    """
    try:
        # Try to create a temporary listener
        server = await asyncio.start_server(
            lambda r, w: None,  # Empty callback
            '0.0.0.0',
            port
        )
        server.close()
        await server.wait_closed()
        logger.info(f"✅ Provider port {port} is available")
        return True
    except Exception as e:
        logger.error(f"❌ Provider port {port} is not available: {e}")
        logger.error("Please ensure:")
        logger.error(f"1. Port {port} is not in use by another application")
        logger.error("2. You have permission to bind to this port")
        logger.error("3. Your firewall allows binding to this port")
        return False


import typer

cli = typer.Typer()

@cli.command()
def start(no_verify_port: bool = typer.Option(False, "--no-verify-port", help="Skip provider port verification.")):
    """Start the provider server."""
    import sys
    from pathlib import Path
    from dotenv import load_dotenv
    import uvicorn
    from .utils.logging import setup_logger
    from .config import settings

    # Configure logging with debug mode
    logger = setup_logger(__name__, debug=True)

    try:
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        # Log environment variables
        logger.info("Environment variables:")
        for key, value in os.environ.items():
            if key.startswith('GOLEM_PROVIDER_'):
                logger.info(f"{key}={value}")

        # Check requirements
        if not check_requirements():
            logger.error("Requirements check failed")
            sys.exit(1)

        # Verify provider port is available
        if not no_verify_port and not asyncio.run(verify_provider_port(settings.PORT)):
            logger.error(f"Provider port {settings.PORT} is not available")
            sys.exit(1)

        # Configure uvicorn logging
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Run server
        logger.process(
            f"🚀 Starting provider server on {settings.HOST}:{settings.PORT}")
        uvicorn.run(
            "provider:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if not settings.DEBUG else "debug",
            log_config=log_config,
            timeout_keep_alive=60,  # Increase keep-alive timeout
            limit_concurrency=100,  # Limit concurrent connections
        )
    except Exception as e:
        logger.error(f"Failed to start provider server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
