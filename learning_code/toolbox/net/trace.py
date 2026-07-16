"""
Using pipeline to display ip location and isp
Example:
    traceroute claude.ai | python trace.py
"""


import csv
import ipaddress
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


HOP_PATTERN = re.compile(r"^\s*(\d+)\s+(.*)$")
PAREN_IP_PATTERN = re.compile(r"\(([0-9a-fA-F:.]+)\)")
RTT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*ms")


def _find_ip(text):
    match = PAREN_IP_PATTERN.search(text)
    if match:
        return match.group(1)

    for token in text.split():
        candidate = token.strip("(),")
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            continue
    return None


def _records(hop, probes):
    if hop is None:
        return
    for ip, times in probes.items():
        yield hop, ip, times


def parse_traceroute(lines):
    current_hop = None
    probes = {}

    for raw_line in lines:
        match = HOP_PATTERN.match(raw_line)
        if match:
            yield from _records(current_hop, probes)
            current_hop = int(match.group(1))
            probes = {}
            body = match.group(2)
        elif current_hop is not None and raw_line[:1].isspace():
            body = raw_line.strip()
        else:
            continue

        ip = _find_ip(body)
        if ip is None:
            continue
        times = [f"{value} ms" for value in RTT_PATTERN.findall(body)]
        probes.setdefault(ip, []).extend(times)

    yield from _records(current_hop, probes)


def lookup_ip(ip):
    if not ipaddress.ip_address(ip).is_global:
        return "", ""

    try:
        query = urlencode({"fields": "status,message,city,isp"})
        with urlopen(f"http://ip-api.com/json/{ip}?{query}", timeout=10) as response:
            data = json.load(response)
        if data.get("status") == "success":
            return data.get("city", ""), data.get("isp", "")
        print(f"IP query failed for {ip}: {data.get('message', 'unknown error')}", file=sys.stderr)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"IP query failed for {ip}: {error}", file=sys.stderr)
    return "", ""


def write_results(records, lookup=lookup_ip, output=None):
    output = output or sys.stdout
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["hop", "ip", "城市", "isp", "time"])
    locations = {}

    for hop, ip, times in records:
        if ip not in locations:
            locations[ip] = lookup(ip)
        city, isp = locations[ip]
        writer.writerow([hop, ip, city, isp, " | ".join(times)])
        output.flush()


if __name__ == "__main__":
    write_results(parse_traceroute(sys.stdin))
