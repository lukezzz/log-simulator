#!/usr/bin/env python3
"""
Test script to verify the YAML template can be loaded correctly.
"""

import yaml
import os


def test_yaml_template_loading():
    """Test that the YAML template can be loaded and parsed correctly."""
    yaml_file = "./predefined_templates/fortigate_forward_traffic.yml"
    
    if not os.path.exists(yaml_file):
        print(f"❌ YAML file not found: {yaml_file}")
        return False
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f)
        
        # Verify required fields are present
        required_fields = ['name', 'device_type', 'description', 'content_format']
        for field in required_fields:
            if field not in template_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ YAML Template Loading Test:")
        print(f"Name: {template_data['name']}")
        print(f"Device Type: {template_data['device_type']}")
        print(f"Description: {template_data['description']}")
        print(f"Content Format (first 100 chars): {template_data['content_format'][:100]}...")
        print()
        
        # Check for ECS placeholders in the content
        content = template_data['content_format']
        ecs_placeholders = ['{source.ip}', '{destination.ip}', '{event.action}', '{@timestamp.date}']
        found_placeholders = []
        
        for placeholder in ecs_placeholders:
            if placeholder in content:
                found_placeholders.append(placeholder)
        
        print(f"✅ Found ECS placeholders: {found_placeholders}")
        print("✅ YAML template loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading YAML template: {e}")
        return False


if __name__ == "__main__":
    test_yaml_template_loading()