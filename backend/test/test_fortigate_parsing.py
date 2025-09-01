#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/lukezhang/Project/Dev/log-simulator/backend/app')

from services.parsing_service import parse_log_with_template

def test_fortigate_parsing():
    template = '''date={@timestamp.date} time={@timestamp.time} logid="{event.id}" type="traffic" subtype="forward" level="notice" vd="vdom1" eventtime={event.created} srcip={source.ip} srcport={source.port} srcintf="port12" srcintfrole="undefined" dstip={destination.ip} dstport={destination.port} dstintf="port11" dstintfrole="undefined" srcuuid="{source.user.id}" dstuuid="{destination.user.id}" poluuid="{rule.uuid}" sessionid={network.session_id} proto={network.transport} action="{event.action}" policyid={rule.id} policytype="policy" service={network.service} dstcountry={destination.geo.country_name} srccountry={source.geo.country_name} trandisp="snat" transip={source.nat.ip} transport={source.nat.port} appid={service.id} app="{service.name}" appcat="Web.Client" apprisk="elevated" applist="g-default" duration={event.duration} sentbyte={source.bytes} rcvdbyte={destination.bytes} sentpkt={source.packets} rcvdpkt={destination.packets} utmaction="allow" countapp=1 osname="{host.os.name}" mastersrcmac="{source.mac}" srcmac="{source.mac}" srcserver=0 utmref=65500-742'''
    
    log_message = '''date=2017-11-15 time=11:44:16 logid="0000000013" type="traffic" subtype="forward" level="notice" vd="vdom1" eventtime=1510775056 srcip=10.1.100.155 srcname="pc1" srcport=40772 srcintf="port12" srcintfrole="undefined" dstip=35.197.51.42 dstname="fortiguard.com" dstport=443 dstintf="port11" dstintfrole="undefined" poluuid="707a0d88-c972-51e7-bbc7-4d421660557b" sessionid=8058 proto=6 action="close" policyid=1 policytype="policy" policymode="learn" service="HTTPS" dstcountry="United States" srccountry="Reserved" trandisp="snat" transip=172.16.200.2 transport=40772 appid=40568 app="HTTPS.BROWSER" appcat="Web.Client" apprisk="medium" duration=2 sentbyte=1850 rcvdbyte=39898 sentpkt=25 rcvdpkt=37 utmaction="allow" countapp=1 devtype="Linux PC" osname="Linux" mastersrcmac="a2:e9:00:ec:40:01" srcmac="a2:e9:00:ec:40:01" srcserver=0 utmref=0-220586'''
    
    print("Testing FortiGate log parsing...")
    print(f"Template length: {len(template)} chars")
    print(f"Log message length: {len(log_message)} chars")
    print()
    
    result = parse_log_with_template(template, log_message)
    
    if result.is_match:
        print("✅ Parsing successful!")
        print(f"Parsed {len(result.parsed_ecs)} top-level ECS fields:")
        for key, value in result.parsed_ecs.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.error_message}")
    
    return result.is_match

if __name__ == "__main__":
    success = test_fortigate_parsing()
    if success:
        print("\n🎉 Test passed!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)