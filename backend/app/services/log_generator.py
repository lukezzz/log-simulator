"""
Log generation service for creating randomized log entries from templates.

This module provides functionality to generate realistic log data by replacing
placeholders in template strings with dynamically generated fake data using
Elastic Common Schema (ECS) format.
"""

import re
import time
import uuid
from datetime import datetime
from typing import Dict, Callable, List
from faker import Faker


class LogGenerator:
    """
    A service class for generating randomized log entries from template strings.
    
    The LogGenerator replaces ECS-formatted placeholders in template strings with realistic
    fake data such as IP addresses, ports, and timestamps.
    """
    
    def __init__(self) -> None:
        """Initialize the LogGenerator with a Faker instance and ECS placeholder generators."""
        self.fake = Faker()
        self._placeholder_generators: Dict[str, Callable[[], str]] = {
            # Network and connection info
            "source.ip": self.fake.ipv4,
            "destination.ip": self.fake.ipv4,
            "source.port": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "destination.port": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "source.nat.ip": self.fake.ipv4,
            "source.nat.port": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "destination.nat.ip": self.fake.ipv4,
            "destination.nat.port": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "source.mac": self.fake.mac_address,
            "destination.mac": self.fake.mac_address,
            "network.transport": lambda: self.fake.random_element(elements=("tcp", "udp", "icmp")),
            "network.service": lambda: self.fake.random_element(elements=("HTTP", "HTTPS", "SSH", "FTP", "DNS")),
            "network.session_id": lambda: str(self.fake.random_int(min=1000000, max=9999999)),
            "network.application": lambda: self.fake.random_element(elements=("web-browsing", "ssl", "ssh", "ftp", "dns")),
            "network.direction": lambda: self.fake.random_element(elements=("inbound", "outbound")),
            "network.bytes": lambda: str(self.fake.random_int(min=64, max=1000000)),
            "network.packets": lambda: str(self.fake.random_int(min=1, max=1000)),
            "network.protocol": lambda: self.fake.random_element(elements=("TCP", "UDP", "ICMP")),
            "network.type": lambda: self.fake.random_element(elements=("ipv4", "ipv6")),
            
            # Event information
            "event.created": lambda: str(int(time.time())),
            "event.id": lambda: str(self.fake.random_int(min=1, max=99999999)).zfill(10),
            "event.action": lambda: self.fake.random_element(elements=("allow", "deny", "close", "accept", "drop")),
            "event.duration": lambda: str(self.fake.random_int(min=1, max=3600)),
            "event.outcome": lambda: self.fake.random_element(elements=("success", "failure", "unknown")),
            "event.sequence": lambda: str(self.fake.random_int(min=1, max=999999)),
            "event.start": lambda: str(int(time.time()) - self.fake.random_int(min=0, max=3600)),
            "event.reason": lambda: self.fake.random_element(elements=("policy-deny", "timeout", "aged-out", "tcp-rst-from-client")),
            
            # Timestamp fields
            "@timestamp.date": lambda: datetime.now().strftime('%Y-%m-%d'),
            "@timestamp.time": lambda: datetime.now().strftime('%H:%M:%S'),
            "@timestamp": lambda: datetime.now().isoformat(),
            "@timestamp.high_res": lambda: str(int(time.time() * 1000000)),
            
            # User and authentication
            "source.user.id": lambda: str(uuid.uuid4()),
            "destination.user.id": lambda: str(uuid.uuid4()),
            "source.user.name": lambda: self.fake.user_name(),
            "destination.user.name": lambda: self.fake.user_name(),
            "user.name": lambda: self.fake.user_name(),
            "user.id": lambda: str(uuid.uuid4()),
            "user.group.name": lambda: self.fake.random_element(elements=("administrators", "users", "guests", "domain_users")),
            
            # Geographic info
            "source.geo.country_name": lambda: self.fake.country(),
            "destination.geo.country_name": lambda: self.fake.country(),
            
            # Service and application
            "service.id": lambda: str(self.fake.random_int(min=1, max=65535)),
            "service.name": lambda: self.fake.random_element(elements=("HTTP.BROWSER_Firefox", "HTTP.BROWSER_Chrome", "SSH.CLIENT", "FTP.CLIENT")),
            "service.type": lambda: self.fake.random_element(elements=("web", "database", "messaging", "file_transfer")),
            
            # Host information
            "host.os.name": lambda: self.fake.random_element(elements=("Ubuntu", "Windows 10", "CentOS", "macOS", "Debian")),
            "host.os.family": lambda: self.fake.random_element(elements=("linux", "windows", "macos", "unix")),
            "host.os.version": lambda: self.fake.random_element(elements=("20.04", "10.0.19041", "7.9", "11.6", "10")),
            "host.id": lambda: str(uuid.uuid4()),
            "host.name": lambda: self.fake.hostname(),
            "host.hostname": lambda: self.fake.hostname(),
            
            # Traffic metrics
            "source.bytes": lambda: str(self.fake.random_int(min=64, max=1000000)),
            "destination.bytes": lambda: str(self.fake.random_int(min=64, max=1000000)),
            "source.packets": lambda: str(self.fake.random_int(min=1, max=1000)),
            "destination.packets": lambda: str(self.fake.random_int(min=1, max=1000)),
            
            # Rules and policies
            "rule.id": lambda: str(self.fake.random_int(min=1, max=999)),
            "rule.uuid": lambda: str(uuid.uuid4()),
            "rule.name": lambda: self.fake.random_element(elements=("allow-web", "deny-malware", "block-untrusted", "permit-ssh")),
            
            # DNS specific fields
            "dns.id": lambda: str(self.fake.random_int(min=1, max=65535)),
            "dns.question.name": lambda: self.fake.domain_name(),
            "dns.question.type": lambda: self.fake.random_element(elements=("A", "AAAA", "CNAME", "MX", "TXT", "PTR")),
            "dns.resolved_ip": self.fake.ipv4,
            
            # URL and web related fields
            "url.domain": lambda: self.fake.domain_name(),
            "url.path": lambda: self.fake.uri_path(),
            "url.original": lambda: self.fake.url(),
            "url.category": lambda: self.fake.random_element(elements=("business-and-economy", "computer-and-internet-info", "web-advertisements")),
            "destination.domain": lambda: self.fake.domain_name(),
            
            # File related fields
            "file.name": lambda: self.fake.file_name(),
            "file.hash.sha256": lambda: self.fake.sha256(),
            
            # Threat related fields
            "threat.technique.name": lambda: self.fake.random_element(elements=("SQL Injection", "Cross-Site Scripting", "Buffer Overflow", "Command Injection")),
            "threat.technique.id": lambda: str(self.fake.random_int(min=1000, max=9999)),
            "threat.software.name": lambda: self.fake.random_element(elements=("Trojan.Generic", "W32.Malware", "Adware.Generic", "Virus.Boot")),
            "threat.software.id": lambda: str(self.fake.random_int(min=1000, max=9999)),
            "threat.indicator.confidence": lambda: str(self.fake.random_int(min=1, max=100)),
            
            # Observer related fields
            "observer.name": lambda: self.fake.hostname(),
            "observer.ingress.interface.name": lambda: self.fake.random_element(elements=("eth0", "port1", "ge-0/0/0", "TenGigE0/0/0")),
            "observer.egress.interface.name": lambda: self.fake.random_element(elements=("eth1", "port2", "ge-0/0/1", "TenGigE0/0/1")),
            
            # Log related fields
            "log.logger": lambda: self.fake.random_element(elements=("traffic", "threat", "url", "data")),
            
            # Organization and AS fields
            "organization.name": lambda: self.fake.company(),
            "source.as.organization.name": lambda: self.fake.company(),
            "destination.as.organization.name": lambda: self.fake.company(),
            
            # Client and User Agent fields
            "client.ip": self.fake.ipv4,
            "user_agent.original": lambda: self.fake.user_agent(),
            
            # Container and Kubernetes fields
            "container.id": lambda: str(uuid.uuid4()),
            "orchestrator.namespace": lambda: self.fake.random_element(elements=("default", "kube-system", "production", "staging")),
            "orchestrator.cluster.name": lambda: self.fake.random_element(elements=("prod-cluster", "dev-cluster", "test-cluster")),
            "kubernetes.pod.name": lambda: f"pod-{self.fake.random_string(length=8)}",
            
            # Legacy placeholders for backward compatibility
            "srcip": self.fake.ipv4,
            "dstip": self.fake.ipv4,
            "srcport": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "dstport": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "eventtime": lambda: str(int(time.time())),
            "date": lambda: datetime.now().strftime('%Y-%m-%d'),
            "time": lambda: datetime.now().strftime('%H:%M:%S'),
            "sessionid": lambda: str(self.fake.random_int(min=1000000, max=9999999)),
            "proto": lambda: self.fake.random_element(elements=("tcp", "udp", "icmp")),
            "action": lambda: self.fake.random_element(elements=("allow", "deny", "close")),
            "policyid": lambda: str(self.fake.random_int(min=1, max=999)),
            "transip": self.fake.ipv4,
            "transport": lambda: str(self.fake.random_int(min=1024, max=65535)),
            "appid": lambda: str(self.fake.random_int(min=1, max=65535)),
            "duration": lambda: str(self.fake.random_int(min=1, max=3600)),
            "sentbyte": lambda: str(self.fake.random_int(min=64, max=1000000)),
            "rcvdbyte": lambda: str(self.fake.random_int(min=64, max=1000000)),
            "sentpkt": lambda: str(self.fake.random_int(min=1, max=1000)),
            "rcvdpkt": lambda: str(self.fake.random_int(min=1, max=1000)),
        }
    
    def generate_log(self, template_string: str) -> str:
        """
        Generate a randomized log entry from a template string.
        
        Replaces ECS-formatted placeholders in the template with dynamically generated fake data.
        Supports both new ECS format ({placeholder}) and legacy format (<placeholder>) for 
        backward compatibility.
        
        Args:
            template_string: The template string containing placeholders to replace
            
        Returns:
            A log string with all placeholders replaced with generated data
            
        Example:
            >>> generator = LogGenerator()
            >>> template = "Connection from {source.ip}:{source.port} to {destination.ip}:{destination.port} at {event.created}"
            >>> log = generator.generate_log(template)
            >>> print(log)
            "Connection from 192.168.1.100:8080 to 10.0.0.50:443 at 1692900000"
        """
        def replace_placeholder(match):
            placeholder = match.group(1)
            if placeholder in self._placeholder_generators:
                return self._placeholder_generators[placeholder]()
            # If placeholder not found, return the original match
            return match.group(0)
        
        # Replace ECS format placeholders {placeholder}
        result = re.sub(r'\{([^}]+)\}', replace_placeholder, template_string)
        
        # For backward compatibility, also replace legacy format <placeholder>
        def replace_legacy_placeholder(match):
            placeholder = match.group(1)
            if placeholder in self._placeholder_generators:
                return self._placeholder_generators[placeholder]()
            return match.group(0)
        
        result = re.sub(r'<([^>]+)>', replace_legacy_placeholder, result)
        
        return result
    
    def add_placeholder(self, placeholder: str, generator_func: Callable[[], str]) -> None:
        """
        Add a custom placeholder generator.
        
        Args:
            placeholder: The placeholder string (e.g., "<custom_field>")
            generator_func: A callable that returns a string value for the placeholder
        """
        self._placeholder_generators[placeholder] = generator_func
    
    def get_available_placeholders(self) -> List[str]:
        """
        Get a list of all available placeholders that can be used in templates.
        
        Returns:
            A list of placeholder strings
        """
        return list(self._placeholder_generators.keys())