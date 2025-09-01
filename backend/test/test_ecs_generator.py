#!/usr/bin/env python3
"""
Test script to verify the new ECS-compliant log generator works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.log_generator import LogGenerator


def test_ecs_placeholder_generation():
    """Test that the new ECS placeholders are properly replaced."""
    generator = LogGenerator()
    
    # Test with ECS format
    ecs_template = "Connection from {source.ip}:{source.port} to {destination.ip}:{destination.port} at {event.created}"
    ecs_result = generator.generate_log(ecs_template)
    print("ECS Format Test:")
    print(f"Template: {ecs_template}")
    print(f"Generated: {ecs_result}")
    print()
    
    # Test with legacy format (for backward compatibility)
    legacy_template = "Connection from <srcip>:<srcport> to <dstip>:<dstport> at <eventtime>"
    legacy_result = generator.generate_log(legacy_template)
    print("Legacy Format Test:")
    print(f"Template: {legacy_template}")
    print(f"Generated: {legacy_result}")
    print()
    
    # Test with the actual FortiGate template format
    fortigate_template = 'date={@timestamp.date} time={@timestamp.time} logid="{event.id}" srcip={source.ip} srcport={source.port} dstip={destination.ip} dstport={destination.port} action="{event.action}"'
    fortigate_result = generator.generate_log(fortigate_template)
    print("FortiGate ECS Template Test:")
    print(f"Template: {fortigate_template}")
    print(f"Generated: {fortigate_result}")
    print()
    
    # Verify that placeholders were actually replaced
    assert "{source.ip}" not in ecs_result, "ECS placeholder was not replaced"
    assert "<srcip>" not in legacy_result, "Legacy placeholder was not replaced"
    assert "{@timestamp.date}" not in fortigate_result, "FortiGate timestamp placeholder was not replaced"
    
    print("✅ All tests passed! The ECS log generator is working correctly.")


if __name__ == "__main__":
    test_ecs_placeholder_generation()