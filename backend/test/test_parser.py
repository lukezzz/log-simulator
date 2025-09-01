#!/usr/bin/env python3
"""
Test script for the parsing service functionality.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.parsing_service import parse_log_with_template

def test_parsing():
    """Test the parsing service with various scenarios."""
    
    print("🧪 Testing Log Parser Service")
    print("=" * 50)
    
    # Test 1: Simple case
    print("\n📝 Test 1: Simple IP addresses")
    template1 = "srcip={source.ip} dstip={dest.ip}"
    log1 = "srcip=1.2.3.4 dstip=5.6.7.8"
    result1 = parse_log_with_template(template1, log1)
    print(f"Template: {template1}")
    print(f"Log:      {log1}")
    print(f"Result:   {result1.model_dump()}")
    
    # Test 2: More complex case with ports
    print("\n📝 Test 2: IPs with ports")
    template2 = "src={source.ip}:{source.port} dst={destination.ip}:{destination.port}"
    log2 = "src=10.0.0.1:443 dst=192.168.1.100:80"
    result2 = parse_log_with_template(template2, log2)
    print(f"Template: {template2}")
    print(f"Log:      {log2}")
    print(f"Result:   {result2.model_dump()}")
    
    # Test 3: Non-matching case
    print("\n📝 Test 3: Non-matching log")
    template3 = "srcip={source.ip}"
    log3 = "different format entirely"
    result3 = parse_log_with_template(template3, log3)
    print(f"Template: {template3}")
    print(f"Log:      {log3}")
    print(f"Result:   {result3.model_dump()}")
    
    # Test 4: Complex firewall log
    print("\n📝 Test 4: Complex firewall log")
    template4 = "action={event.action} src={source.ip}:{source.port} dst={destination.ip}:{destination.port} proto={network.protocol}"
    log4 = "action=allow src=192.168.1.10:54321 dst=8.8.8.8:53 proto=udp"
    result4 = parse_log_with_template(template4, log4)
    print(f"Template: {template4}")
    print(f"Log:      {log4}")
    print(f"Result:   {result4.model_dump()}")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    test_parsing()