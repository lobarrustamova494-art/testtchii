"""
Performance Benchmarks and Targets
Used for monitoring and testing system performance
"""

# Performance Targets (in seconds)
PERFORMANCE_TARGETS = {
    'image_processing': {
        'target': 1.0,
        'warning': 1.5,
        'critical': 2.0,
        'description': 'Image loading, corner detection, perspective correction, preprocessing'
    },
    'qr_detection': {
        'target': 0.2,
        'warning': 0.3,
        'critical': 0.5,
        'description': 'QR code detection and decoding'
    },
    'coordinate_calculation': {
        'target': 0.1,
        'warning': 0.2,
        'critical': 0.5,
        'description': 'Bubble coordinate calculation'
    },
    'omr_detection': {
        'target': 2.0,
        'warning': 3.0,
        'critical': 5.0,
        'description': 'OMR bubble detection and analysis'
    },
    'ai_verification': {
        'target': 2.0,
        'warning': 3.0,
        'critical': 5.0,
        'description': 'AI verification of uncertain answers'
    },
    'grading': {
        'target': 0.1,
        'warning': 0.2,
        'critical': 0.5,
        'description': 'Answer comparison and score calculation'
    },
    'annotation': {
        'target': 0.5,
        'warning': 0.8,
        'critical': 1.0,
        'description': 'Annotated image generation'
    },
    'total': {
        'target': 4.0,
        'warning': 6.0,
        'critical': 10.0,
        'description': 'Total processing time per sheet'
    }
}

# Memory Targets (in MB)
MEMORY_TARGETS = {
    'image_load': {
        'target': 25,
        'warning': 50,
        'critical': 100,
        'description': 'Memory for loaded image (2480x3508 px)'
    },
    'processing': {
        'target': 50,
        'warning': 100,
        'critical': 200,
        'description': 'Memory during processing'
    },
    'total_per_request': {
        'target': 100,
        'warning': 150,
        'critical': 250,
        'description': 'Total memory per request'
    }
}

# Accuracy Targets (in percentage)
ACCURACY_TARGETS = {
    'omr_detection': {
        'target': 99.0,
        'warning': 95.0,
        'critical': 90.0,
        'description': 'OMR bubble detection accuracy'
    },
    'corner_detection': {
        'target': 95.0,
        'warning': 90.0,
        'critical': 80.0,
        'description': 'Corner marker detection success rate'
    },
    'qr_detection': {
        'target': 98.0,
        'warning': 95.0,
        'critical': 90.0,
        'description': 'QR code detection success rate'
    },
    'with_ai_verification': {
        'target': 99.9,
        'warning': 99.5,
        'critical': 99.0,
        'description': 'Accuracy with AI verification'
    }
}

# Scalability Targets
SCALABILITY_TARGETS = {
    'concurrent_requests': {
        'target': 10,
        'warning': 5,
        'critical': 2,
        'description': 'Number of concurrent requests'
    },
    'throughput': {
        'target': 5,
        'warning': 2,
        'critical': 1,
        'description': 'Sheets processed per second'
    },
    'recommended_throughput': {
        'value': 2,
        'description': 'Recommended sheets per second for stable operation'
    }
}

def check_performance(metric_name: str, value: float) -> dict:
    """
    Check if performance metric meets targets
    
    Args:
        metric_name: Name of metric (e.g., 'image_processing')
        value: Measured value
        
    Returns:
        dict: {
            'status': 'good'|'warning'|'critical',
            'value': measured value,
            'target': target value,
            'message': status message
        }
    """
    if metric_name not in PERFORMANCE_TARGETS:
        return {
            'status': 'unknown',
            'value': value,
            'message': f'Unknown metric: {metric_name}'
        }
    
    targets = PERFORMANCE_TARGETS[metric_name]
    
    if value <= targets['target']:
        status = 'good'
        message = f'✅ {metric_name}: {value:.2f}s (target: {targets["target"]}s)'
    elif value <= targets['warning']:
        status = 'warning'
        message = f'⚠️  {metric_name}: {value:.2f}s (warning threshold: {targets["warning"]}s)'
    else:
        status = 'critical'
        message = f'❌ {metric_name}: {value:.2f}s (critical threshold: {targets["critical"]}s)'
    
    return {
        'status': status,
        'value': value,
        'target': targets['target'],
        'warning': targets['warning'],
        'critical': targets['critical'],
        'message': message
    }

def generate_performance_report(metrics: dict) -> dict:
    """
    Generate performance report from metrics
    
    Args:
        metrics: dict of metric_name: value
        
    Returns:
        dict: Performance report with status for each metric
    """
    report = {
        'metrics': {},
        'overall_status': 'good',
        'summary': {
            'good': 0,
            'warning': 0,
            'critical': 0
        }
    }
    
    for metric_name, value in metrics.items():
        result = check_performance(metric_name, value)
        report['metrics'][metric_name] = result
        
        if result['status'] == 'warning':
            report['summary']['warning'] += 1
            if report['overall_status'] == 'good':
                report['overall_status'] = 'warning'
        elif result['status'] == 'critical':
            report['summary']['critical'] += 1
            report['overall_status'] = 'critical'
        else:
            report['summary']['good'] += 1
    
    return report
