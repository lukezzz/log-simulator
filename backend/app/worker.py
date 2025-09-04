"""
Background worker for processing log sending jobs.

This module provides a separate process that listens to Redis pub/sub commands
and manages long-running log sending jobs.
"""

import asyncio
import socket
import logging
from typing import Dict, Optional
import redis.asyncio as redis

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from core.settings import cfg
from models.job import Job, JobStatusEnum, ProtocolEnum
from models.log_template import LogTemplate
from services.log_generator import LogGenerator


# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global dictionary to store active job tasks
active_jobs: Dict[str, asyncio.Task] = {}

# Redis client
redis_client: Optional[redis.Redis] = None

# Log generator instance
log_generator = LogGenerator()

# db
engine = create_async_engine(cfg.APP_DB_URI, echo=True)

async def send_log_loop(job_id: str) -> None:
    """
    Main loop for sending logs for a specific job with advanced scheduling.
    
    This function handles start_time, end_time, send_count, and send_interval_ms
    according to the job configuration.
    
    Args:
        job_id: The UUID of the job to process
    """
    logger.info(f"Starting log sending loop for job {job_id}")
    async with AsyncSession(engine) as session:
        try:
            # Get job details from database and extract all needed data
            job_config = None
            template_content = None
            
            try:
                logger.debug(f"Fetching job {job_id} from database")
                stmt = select(Job).where(Job.id == job_id)
                job_res = await session.execute(stmt)
                job = job_res.scalar_one_or_none()
                if not job:
                    logger.error(f"Job {job_id} not found in database")
                    return
                
                # Get the template
                logger.debug(f"Fetching template {job.template_id} for job {job_id}")
                stmt = select(LogTemplate).where(LogTemplate.id == job.template_id)
                template_res = await session.execute(stmt)
                template = template_res.scalar_one_or_none()
                if not template:
                    logger.error(f"Template {job.template_id} not found for job {job_id}")
                    await _update_job_status(job_id, JobStatusEnum.ERROR)
                    return
                
                # Extract all data we need before closing the session
                job_config = {
                    'destination_host': job.destination_host,
                    'destination_port': job.destination_port,
                    'protocol': job.protocol,
                    'start_time': job.start_time,
                    'end_time': job.end_time,
                    'send_count': job.send_count,
                    'send_interval_ms': job.send_interval_ms or 1000
                }
                template_content = template.content_format
                
                # Update job status to RUNNING
                job.status = JobStatusEnum.RUNNING
                await session.commit()
                
                logger.info(f"Job {job_id} configured: {job_config['protocol']} to {job_config['destination_host']}:{job_config['destination_port']}")
                logger.info(f"Scheduling config - start_time: {job_config['start_time']}, end_time: {job_config['end_time']}, send_count: {job_config['send_count']}, interval: {job_config['send_interval_ms']}ms")
                
            except Exception as e:
                logger.error(f"Database error while setting up job {job_id}: {e}")
                await _update_job_status(job_id, JobStatusEnum.ERROR)
                return

            # Validate we have all required data
            if not job_config or not template_content:
                logger.error(f"Failed to extract job configuration for {job_id}")
                await _update_job_status(job_id, JobStatusEnum.ERROR)
                return
            
            # Import datetime for time comparisons
            from datetime import datetime, timezone
            
            # Helper function to ensure timezone-aware datetime
            def ensure_timezone_aware(dt):
                if dt is None:
                    return None
                if dt.tzinfo is None:
                    # Assume naive datetime is in UTC
                    return dt.replace(tzinfo=timezone.utc)
                return dt
            
            # Ensure start_time and end_time are timezone-aware
            job_config['start_time'] = ensure_timezone_aware(job_config['start_time'])
            job_config['end_time'] = ensure_timezone_aware(job_config['end_time'])
            
            # Wait for start_time if set and in the future
            if job_config['start_time']:
                now = datetime.now(timezone.utc)
                if job_config['start_time'] > now:
                    wait_seconds = (job_config['start_time'] - now).total_seconds()
                    logger.info(f"Job {job_id} waiting {wait_seconds:.1f}s until start time {job_config['start_time']}")
                    await asyncio.sleep(wait_seconds)
            
            # Initialize counters
            logs_sent = 0
            interval_seconds = job_config['send_interval_ms'] / 1000.0
            
            # Main sending loop
            while True:
                try:
                    # Check if we should stop due to end_time
                    if job_config['end_time']:
                        now = datetime.now(timezone.utc)
                        if now >= job_config['end_time']:
                            logger.info(f"Job {job_id} reached end_time {job_config['end_time']}, stopping")
                            break
                    
                    # Check if we should stop due to send_count limit
                    if job_config['send_count'] and logs_sent >= job_config['send_count']:
                        logger.info(f"Job {job_id} reached send_count limit of {job_config['send_count']}, stopping")
                        break
                    
                    # Generate log content from template
                    log_content = log_generator.generate_log(template_content)
                    
                    # Send the log
                    await _send_log_message(
                        log_content,
                        job_config['destination_host'],
                        job_config['destination_port'],
                        job_config['protocol']
                    )
                    
                    logs_sent += 1
                    logger.debug(f"Sent log {logs_sent} for job {job_id}: {log_content[:100]}...")
                    
                    # Sleep for the configured interval
                    await asyncio.sleep(interval_seconds)
                    
                except asyncio.CancelledError:
                    logger.info(f"Job {job_id} was cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in job {job_id} loop: {e}")
                    logger.debug(f"Full exception details: {type(e).__name__}: {str(e)}")
                    await _update_job_status(job_id, JobStatusEnum.ERROR)
                    break
            
            # Job completed naturally (reached end_time or send_count)
            logger.info(f"Job {job_id} completed naturally after sending {logs_sent} logs")
            await _update_job_status(job_id, JobStatusEnum.STOPPED)
                    
        except Exception as e:
            logger.error(f"Fatal error in job {job_id}: {e}")
            await _update_job_status(job_id, JobStatusEnum.ERROR)
        finally:
            # Clean up the job from active jobs
            if job_id in active_jobs:
                del active_jobs[job_id]
            logger.info(f"Log sending loop ended for job {job_id}")


async def _send_log_message(message: str, host: str, port: int, protocol: ProtocolEnum) -> None:
    """
    Send a log message to the specified destination.
    
    Args:
        message: The log message to send
        host: Destination host
        port: Destination port  
        protocol: Protocol to use (TCP or UDP)
    """
    try:
        logger.debug(f"Sending message via {protocol} to {host}:{port} - {message[:50]}...")
        if protocol == ProtocolEnum.UDP:
            await _send_udp_message(message, host, port)
        elif protocol == ProtocolEnum.TCP:
            await _send_tcp_message(message, host, port)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
        logger.debug(f"Successfully sent message via {protocol} to {host}:{port}")
    except Exception as e:
        logger.error(f"Failed to send message to {host}:{port} via {protocol}: {type(e).__name__}: {e}")
        raise


async def _send_udp_message(message: str, host: str, port: int) -> None:
    """Send a message via UDP."""
    loop = asyncio.get_event_loop()
    
    def send_udp():
        logger.debug(f"Creating UDP socket for {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            message_bytes = message.encode('utf-8')
            logger.debug(f"Sending {len(message_bytes)} bytes via UDP to {host}:{port}")
            sock.sendto(message_bytes, (host, port))
            logger.debug(f"UDP message sent successfully to {host}:{port}")
        except Exception as e:
            logger.error(f"UDP socket error: {type(e).__name__}: {e}")
            raise
        finally:
            sock.close()
    
    await loop.run_in_executor(None, send_udp)


async def _send_tcp_message(message: str, host: str, port: int) -> None:
    """Send a message via TCP."""
    try:
        logger.debug(f"Opening TCP connection to {host}:{port}")
        reader, writer = await asyncio.open_connection(host, port)
        
        # Prepare message with newline
        message_bytes = message.encode('utf-8') + b'\n'
        logger.debug(f"Sending {len(message_bytes)} bytes via TCP")
        
        writer.write(message_bytes)
        await writer.drain()
        
        logger.debug(f"TCP message sent, closing connection to {host}:{port}")
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        logger.error(f"TCP connection error to {host}:{port}: {type(e).__name__}: {e}")
        raise


async def _update_job_status(job_id: str, status: JobStatusEnum) -> None:
    """
    Update job status in the database.
    
    Args:
        job_id: Job UUID as string
        status: New status to set
    """
    logger.debug(f"Updating job {job_id} status to {status}")
    async with AsyncSession(engine) as session:
        try:
            stmt = select(Job).where(Job.id == job_id)
            job_res = await session.execute(stmt)
            job = job_res.scalar_one_or_none()
            logger.debug(f"Found job {job}, {job.__repr__() if job else 'None'}")   
            if job:
                job.status = status
                await session.commit()
                logger.info(f"Updated job {job_id} status to {status}")
            else:
                logger.warning(f"Job {job_id} not found when trying to update status to {status}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {type(e).__name__}: {e}")
            await session.rollback()
            raise


async def handle_job_command(message: str) -> None:
    """
    Handle incoming job commands from Redis pub/sub.
    
    Args:
        message: Command message in format "START:job_id" or "STOP:job_id"
    """
    try:
        logger.debug(f"Processing command: {message}")
        command, job_id = message.split(":", 1)
        
        if command == "START":
            logger.info(f"Received START command for job {job_id}")
            await _start_job(job_id)
        elif command == "STOP":
            logger.info(f"Received STOP command for job {job_id}")
            await _stop_job(job_id)
        else:
            logger.warning(f"Unknown command: {command}")
            
    except ValueError as e:
        logger.error(f"Invalid command format: {message} - {e}")
    except Exception as e:
        logger.error(f"Error handling command {message}: {type(e).__name__}: {e}")
        logger.debug(f"Full exception details: {str(e)}")


async def _start_job(job_id: str) -> None:
    """
    Start a job by creating a new task.
    
    Args:
        job_id: Job UUID as string
    """
    if job_id in active_jobs:
        logger.warning(f"Job {job_id} is already running")
        return
    
    logger.info(f"Starting job {job_id}")
    
    # Update job status to STARTING
    await _update_job_status(job_id, JobStatusEnum.RUNNING)
    
    # Create and store the task
    task = asyncio.create_task(send_log_loop(job_id))
    active_jobs[job_id] = task


async def _stop_job(job_id: str) -> None:
    """
    Stop a job by cancelling its task.
    
    Args:
        job_id: Job UUID as string
    """
    if job_id not in active_jobs:
        logger.warning(f"Job {job_id} is not running")
        return
    
    logger.info(f"Stopping job {job_id}")
    
    # Cancel the task
    task = active_jobs[job_id]
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Update job status
    await _update_job_status(job_id, JobStatusEnum.STOPPED)
    
    # Remove from active jobs
    del active_jobs[job_id]


async def main():
    """
    Main worker process that listens for Redis pub/sub commands.
    """
    global redis_client
    
    logger.info("Starting log simulator worker...")
    
    # Connect to Redis
    redis_client = redis.from_url(cfg.REDIS_URI, decode_responses=True)
    
    try:
        # Test Redis connection
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
        
        # Create pub/sub connection
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("job_commands")
        
        logger.info("Subscribed to job_commands channel, waiting for commands...")
        
        # Listen for messages
        async for message in pubsub.listen():
            if message["type"] == "message":
                command_data = message["data"]
                logger.info(f"Received command: {command_data}")
                await handle_job_command(command_data)
                
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        # Clean up active jobs
        logger.info("Stopping all active jobs...")
        for job_id, task in active_jobs.items():
            logger.info(f"Cancelling job {job_id}")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Close Redis connection
        if redis_client:
            await redis_client.aclose()
        
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())