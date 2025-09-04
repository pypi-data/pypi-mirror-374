"""
API endpoints for telemetry and metrics data.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query
from loguru import logger
import time
from datetime import datetime, timedelta

from vrouter_agent.enhanced_stream_processor import get_stream_processor
from vrouter_agent.utils import get_device_serial_number

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/metrics/")
async def get_metrics():
    """
    Get current system metrics from the stream processor.
    
    Returns:
        Current metrics including processing statistics, performance data, and system health
    """
    try:
        processor = await get_stream_processor()
        metrics = processor.get_metrics()
        
        # Enhance metrics with additional computed values
        enhanced_metrics = {
            **metrics,
            "device_serial": get_device_serial_number(),
            "timestamp": time.time(),
            "uptime_seconds": time.time() - metrics.get('start_time', time.time()),
        }
        
        # Calculate success rate
        total_processed = metrics.get('total_processed', 0)
        successful_processed = metrics.get('successful_processed', 0)
        if total_processed > 0:
            enhanced_metrics['success_rate'] = successful_processed / total_processed
        else:
            enhanced_metrics['success_rate'] = 0.0
        
        # Calculate failure rate
        failed_processed = metrics.get('failed_processed', 0)
        if total_processed > 0:
            enhanced_metrics['failure_rate'] = failed_processed / total_processed
        else:
            enhanced_metrics['failure_rate'] = 0.0
        
        logger.info("Retrieved system metrics")
        return enhanced_metrics
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/status/")
async def get_system_status():
    """
    Get current system status and health information.
    
    Returns:
        System status including processor state, worker information, and health indicators
    """
    try:
        processor = await get_stream_processor()
        status = processor.get_status()
        
        # Enhance status with additional information
        enhanced_status = {
            **status,
            "device_serial": get_device_serial_number(),
            "timestamp": time.time(),
            "system_health": "healthy" if status.get("running", False) else "unhealthy",
        }
        
        # Add worker utilization status
        worker_utilization = status.get('worker_utilization', 0.0)
        if worker_utilization > 0.9:
            enhanced_status['worker_status'] = "high_load"
        elif worker_utilization > 0.7:
            enhanced_status['worker_status'] = "moderate_load"
        else:
            enhanced_status['worker_status'] = "normal"
        
        # Add queue status
        queue_size = status.get('queue_size', 0)
        if queue_size > 100:
            enhanced_status['queue_status'] = "high"
        elif queue_size > 50:
            enhanced_status['queue_status'] = "moderate"
        else:
            enhanced_status['queue_status'] = "normal"
        
        logger.info("Retrieved system status")
        return enhanced_status
        
    except Exception as e:
        logger.error(f"Error retrieving system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")


@router.get("/health/")
async def get_health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        Detailed health information including all subsystems
    """
    try:
        processor = await get_stream_processor()
        metrics = processor.get_metrics()
        status = processor.get_status()
        
        current_time = time.time()
        
        # Determine overall health
        is_healthy = True
        health_issues = []
        
        # Check if processor is running
        if not status.get("running", False):
            is_healthy = False
            health_issues.append("Stream processor is not running")
        
        # Check worker utilization
        worker_utilization = status.get('worker_utilization', 0.0)
        if worker_utilization > 0.95:
            health_issues.append("High worker utilization")
        
        # Check queue size
        queue_size = status.get('queue_size', 0)
        if queue_size > 200:
            is_healthy = False
            health_issues.append("Queue size is critically high")
        elif queue_size > 100:
            health_issues.append("Queue size is elevated")
        
        # Check for recent activity
        last_activity = status.get('last_activity')
        if last_activity and (current_time - last_activity) > 300:  # 5 minutes
            health_issues.append("No recent processing activity")
        
        # Check failure rate
        total_processed = metrics.get('total_processed', 0)
        failed_processed = metrics.get('failed_processed', 0)
        if total_processed > 0:
            failure_rate = failed_processed / total_processed
            if failure_rate > 0.1:  # 10% failure rate
                is_healthy = False
                health_issues.append(f"High failure rate: {failure_rate:.2%}")
        
        health_status = {
            "healthy": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "issues": health_issues,
            "checks": {
                "processor_running": status.get("running", False),
                "worker_utilization_ok": worker_utilization < 0.95,
                "queue_size_ok": queue_size < 200,
                "recent_activity": last_activity is not None and (current_time - last_activity) < 300,
                "failure_rate_ok": (failed_processed / max(total_processed, 1)) < 0.1,
            },
            "metrics_summary": {
                "total_processed": total_processed,
                "success_rate": (metrics.get('successful_processed', 0) / max(total_processed, 1)),
                "failure_rate": (failed_processed / max(total_processed, 1)),
                "average_processing_time": metrics.get('average_processing_time', 0),
                "queue_size": queue_size,
                "worker_utilization": worker_utilization,
            },
            "device_serial": get_device_serial_number(),
            "timestamp": current_time,
        }
        
        logger.info(f"Health check completed - Status: {health_status['status']}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform health check")


@router.get("/performance/")
async def get_performance_metrics():
    """
    Get detailed performance metrics.
    
    Returns:
        Performance-focused metrics and statistics
    """
    try:
        processor = await get_stream_processor()
        metrics = processor.get_metrics()
        status = processor.get_status()
        
        current_time = time.time()
        uptime = current_time - metrics.get('start_time', current_time)
        
        performance_metrics = {
            "processing_performance": {
                "total_processed": metrics.get('total_processed', 0),
                "successful_processed": metrics.get('successful_processed', 0),
                "failed_processed": metrics.get('failed_processed', 0),
                "retry_count": metrics.get('retry_count', 0),
                "average_processing_time_ms": metrics.get('average_processing_time', 0),
            },
            "system_performance": {
                "uptime_seconds": uptime,
                "uptime_hours": uptime / 3600,
                "worker_count": status.get('worker_count', 0),
                "worker_utilization": status.get('worker_utilization', 0.0),
                "queue_size": status.get('queue_size', 0),
            },
            "throughput": {
                "transactions_per_second": metrics.get('total_processed', 0) / max(uptime, 1),
                "successful_per_second": metrics.get('successful_processed', 0) / max(uptime, 1),
                "failed_per_second": metrics.get('failed_processed', 0) / max(uptime, 1),
            },
            "device_serial": get_device_serial_number(),
            "timestamp": current_time,
        }
        
        logger.info("Retrieved performance metrics")
        return performance_metrics
        
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")


@router.get("/system-info/")
async def get_system_info():
    """
    Get general system information.
    
    Returns:
        System information including device details and configuration
    """
    try:
        processor = await get_stream_processor()
        metrics = processor.get_metrics()
        
        system_info = {
            "device_serial": get_device_serial_number(),
            "processor_config": {
                "max_workers": getattr(processor, 'max_workers', 'unknown'),
                "batch_size": getattr(processor, 'batch_size', 'unknown'),
            },
            "runtime_info": {
                "start_time": metrics.get('start_time'),
                "start_time_iso": datetime.fromtimestamp(metrics.get('start_time', 0)).isoformat() if metrics.get('start_time') else None,
                "uptime_seconds": time.time() - metrics.get('start_time', time.time()),
                "last_activity": metrics.get('last_activity'),
                "last_activity_iso": datetime.fromtimestamp(metrics.get('last_activity', 0)).isoformat() if metrics.get('last_activity') else None,
            },
            "current_timestamp": time.time(),
            "current_timestamp_iso": datetime.now().isoformat(),
        }
        
        logger.info("Retrieved system information")
        return system_info
        
    except Exception as e:
        logger.error(f"Error retrieving system information: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system information")


@router.get("/alerts/")
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
):
    """
    Get current system alerts and warnings.
    
    Args:
        severity: Optional severity filter
    
    Returns:
        List of current alerts and warnings
    """
    try:
        processor = await get_stream_processor()
        metrics = processor.get_metrics()
        status = processor.get_status()
        
        alerts = []
        current_time = time.time()
        
        # Check for various alert conditions
        
        # Critical alerts
        if not status.get("running", False):
            alerts.append({
                "severity": "critical",
                "message": "Stream processor is not running",
                "timestamp": current_time,
                "component": "stream_processor"
            })
        
        queue_size = status.get('queue_size', 0)
        if queue_size > 200:
            alerts.append({
                "severity": "critical",
                "message": f"Queue size critically high: {queue_size}",
                "timestamp": current_time,
                "component": "queue"
            })
        
        # High severity alerts
        worker_utilization = status.get('worker_utilization', 0.0)
        if worker_utilization > 0.95:
            alerts.append({
                "severity": "high",
                "message": f"Worker utilization very high: {worker_utilization:.1%}",
                "timestamp": current_time,
                "component": "workers"
            })
        
        total_processed = metrics.get('total_processed', 0)
        failed_processed = metrics.get('failed_processed', 0)
        if total_processed > 0:
            failure_rate = failed_processed / total_processed
            if failure_rate > 0.1:
                alerts.append({
                    "severity": "high",
                    "message": f"High failure rate: {failure_rate:.1%}",
                    "timestamp": current_time,
                    "component": "processing"
                })
        
        # Medium severity alerts
        if queue_size > 100:
            alerts.append({
                "severity": "medium",
                "message": f"Queue size elevated: {queue_size}",
                "timestamp": current_time,
                "component": "queue"
            })
        
        if worker_utilization > 0.8:
            alerts.append({
                "severity": "medium",
                "message": f"Worker utilization high: {worker_utilization:.1%}",
                "timestamp": current_time,
                "component": "workers"
            })
        
        # Low severity alerts
        last_activity = status.get('last_activity')
        if last_activity and (current_time - last_activity) > 300:  # 5 minutes
            alerts.append({
                "severity": "low",
                "message": "No recent processing activity",
                "timestamp": current_time,
                "component": "activity"
            })
        
        # Filter by severity if requested
        if severity:
            alerts = [alert for alert in alerts if alert['severity'] == severity.lower()]
        
        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        result = {
            "alerts": alerts,
            "alert_count": len(alerts),
            "critical_count": len([a for a in alerts if a['severity'] == 'critical']),
            "high_count": len([a for a in alerts if a['severity'] == 'high']),
            "medium_count": len([a for a in alerts if a['severity'] == 'medium']),
            "low_count": len([a for a in alerts if a['severity'] == 'low']),
            "device_serial": get_device_serial_number(),
            "timestamp": current_time,
        }
        
        logger.info(f"Retrieved {len(alerts)} alerts")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")
