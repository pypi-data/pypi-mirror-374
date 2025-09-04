#!/usr/bin/env python3
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
TRAEFIK_API_PORT = 8087
CONFIG_FILE = os.path.join(Path.home(), ".consulcli_config.json")

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_config(key, value):
    config = load_config()
    config[key] = value
    config["saved_on"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {CONFIG_FILE}.")

def get_consul_ip(public_ip_or_alias):
    """
    public_ip_or_alias: key used in your aliases mapping. Returns the mapped internal IP.
    """
    config = load_config()
    aliases = config.get("aliases", {})
    internal_ip = aliases.get(public_ip_or_alias)
    if not internal_ip:
        print(f"No alias found for '{public_ip_or_alias}'. Use `tf alias add {public_ip_or_alias} <ip>` to define one.")
        sys.exit(1)
    return internal_ip

# ------------------------------------------------------------------------------
# Consul / Traefik Operations
# ------------------------------------------------------------------------------
def register_service(public_ip, service_id, service_name, address, port, domains,
                     middlewares=None, https_insecure=False, custom_rule=None, disable_tls=False):
    """
    Register a service into the local Consul agent (by alias) with Traefik tags.
    Optionally:
      - https_insecure: talk to upstream over HTTPS but skip verification via serversTransport
      - disable_tls: disable TLS termination at Traefik (use web entryPoint instead of websecure)
      - middlewares: list of Traefik middleware refs "id@provider"
      - custom_rule: full Traefik rule string; if provided, 'domains' are ignored.
    """
    internal_ip = get_consul_ip(public_ip)

    if custom_rule:
        domain_rules = custom_rule
    else:
        if not domains:
            print("Error: You must specify at least one domain or provide --custom-rule support (not exposed via CLI).")
            sys.exit(2)
        domain_rules = " || ".join([f"Host(`{d}`)" for d in domains])

    tags = ["traefik.enable=true"]

    if disable_tls:
        # Use HTTP only (e.g., for ejabberd ACME support)
        tags.append(f"traefik.http.routers.{service_id}.rule={domain_rules}")
        tags.append(f"traefik.http.routers.{service_id}.entrypoints=web")
        tags.append(f"traefik.http.routers.{service_id}.service={service_id}")
    else:
        # Standard HTTPS config
        tags.append(f"traefik.http.routers.{service_id}.rule={domain_rules}")
        tags.append(f"traefik.http.routers.{service_id}.entrypoints=websecure")
        tags.append(f"traefik.http.routers.{service_id}.tls=true")
        tags.append(f"traefik.http.routers.{service_id}.tls.certresolver=myresolver")

    tags.append(f"traefik.http.services.{service_id}.loadbalancer.server.port={int(port)}")

    if https_insecure:
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.server.scheme=https")
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.serverstransport=insecure-transport@file")

    if middlewares:
        tags.append(f"traefik.http.routers.{service_id}.middlewares=" + ",".join(middlewares))

    # Create serversTransport in Consul "config" if requested
    if https_insecure:
        servers_transport_payload = {
            "Name": f"insecure-transport",
            "TLS": {
                "InsecureSkipVerify": True
            }
        }
        transport_url = f"http://{internal_ip}:8500/v1/agent/config/traefik/transport/insecure-transport"
        try:
            requests.put(transport_url, json=servers_transport_payload, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not register serversTransport for {service_id}: {e}")

    payload = {
        "ID": service_id,
        "Name": service_name,
        "Address": address,
        "Port": int(port),
        "Tags": tags
    }

    url = f"http://{internal_ip}:8500/v1/agent/service/register"
    try:
        resp = requests.put(url, json=payload, timeout=10)
        if resp.status_code == 200:
            mw_info = f" with middlewares: {', '.join(middlewares)}" if middlewares else ""
            tls_info = " (TLS disabled)" if disable_tls else ""
            print(f"Service '{service_name}' (ID: {service_id}) registered in Consul{mw_info}{tls_info}.")
        else:
            print(f"Failed to register service. HTTP {resp.status_code}: {resp.text}")
            sys.exit(3)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def deregister_service(public_ip, service_id):
    """
    Deregister a service from the local Consul agent identified by alias `public_ip`.
    Also tries to remove the Traefik serversTransport created during --https-insecure.
    """
    internal_ip = get_consul_ip(public_ip)

    # Try to remove Traefik serversTransport (ignore 404s)
    transport_url = f"http://{internal_ip}:8500/v1/agent/config/traefik/transport/{service_id}-transport"
    try:
        resp_t = requests.delete(transport_url, timeout=10)
        if resp_t.status_code in (200, 204):
            print(f"Removed serversTransport '{service_id}-transport' from Consul config.")
        elif resp_t.status_code == 404:
            pass  # nothing to remove; fine
        else:
            print(f"Warning: serversTransport delete returned HTTP {resp_t.status_code}: {resp_t.text}")
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not delete serversTransport for {service_id}: {e}")

    # Deregister the Consul service
    url = f"http://{internal_ip}:8500/v1/agent/service/deregister/{service_id}"
    try:
        resp = requests.put(url, timeout=10)
        if resp.status_code == 200:
            print(f"Service ID '{service_id}' deregistered from Consul at {internal_ip}.")
        else:
            print(f"Failed to deregister service. HTTP {resp.status_code}: {resp.text}")
            sys.exit(4)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def list_services(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:8500/v1/agent/services"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            services = resp.json()
            if not services:
                print(f"No services found on Consul at {internal_ip}.")
                return
            print(f"Services on Consul at {internal_ip}:")
            print("-------------------------------------------------------------------")
            for srv_id, srv_data in services.items():
                name = srv_data.get("Service", "")
                addr = srv_data.get("Address", "")
                port = srv_data.get("Port", "")
                tags = srv_data.get("Tags", [])
                print(f"ID: {srv_id}")
                print(f"  Name: {name}")
                print(f"  Address: {addr}")
                print(f"  Port: {port}")
                print(f"  Tags: {', '.join(tags)}")
                print("-------------------------------------------------------------------")
        else:
            print(f"Failed to list services. HTTP {resp.status_code}: {resp.text}")
            sys.exit(5)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def list_traefik(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:{TRAEFIK_API_PORT}/api/http/routers"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            routers = resp.json()
            if not routers:
                print(f"No routers found in Traefik at {internal_ip}.")
                return
            print(f"Routers in Traefik at {internal_ip}:")
            print("-------------------------------------------------------------------")
            router_items = routers.items() if isinstance(routers, dict) else [
                (r.get("name", "unknown"), r) for r in routers
            ]
            for router_name, router_data in router_items:
                print(f"Router: {router_name}")
                print(f"  Rule: {router_data.get('rule', '')}")
                print(f"  Service: {router_data.get('service', '')}")
                middlewares = router_data.get("middlewares", [])
                if middlewares:
                    print(f"  Middlewares: {', '.join(middlewares)}")
                print("-------------------------------------------------------------------")
        else:
            print(f"Failed to list Traefik routers. HTTP {resp.status_code}: {resp.text}")
            sys.exit(6)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Traefik at {internal_ip}: {e}")
        sys.exit(1)

def list_middlewares(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:{TRAEFIK_API_PORT}/api/http/middlewares"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            middlewares = resp.json()
            if not middlewares:
                print(f"No middlewares found in Traefik at {internal_ip}.")
                return
            print(f"Middlewares in Traefik at {internal_ip}:")
            print("-------------------------------------------------------------------")
            # Traefik returns a list of dicts; print them verbosely
            for mw in middlewares:
                for key, value in mw.items():
                    print(f"{key}: {json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value}")
                print("-------------------------------------------------------------------")
        else:
            print(f"Failed to list Traefik middlewares. HTTP {resp.status_code}: {resp.text}")
            sys.exit(7)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Traefik at {internal_ip}: {e}")
        sys.exit(1)

# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------
def main():
    epilog_text = """
Examples:
  tf alias list
  tf alias add jim 192.168.19.7

  tf register jim mysvc MyService 192.168.19.4 3000 my.example.com
  tf register jim mysvc MyService 192.168.19.4 3000 my.example.com --middlewares auth@file
  tf register jim proxmox Proxmox 192.168.19.10 8006 prox.example.com --https-insecure  # Traefik->upstream over TLS, skip verify
  tf register jim proxmox Proxmox 192.168.19.10 8006 prox.example.com --disable-tls     # Disable TLS termination on Traefik
  tf deregister jim mysvc

  tf list jim
  tf list-traefik jim
  tf list-middlewares jim
"""
    parser = argparse.ArgumentParser(
        description="Consul-Traefik Management CLI.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    # register
    reg_parser = subparsers.add_parser("register", help="Register a service")
    reg_parser.add_argument("public_ip", help="Alias name that maps to an internal Consul IP")
    reg_parser.add_argument("service_id", help="Unique service ID in Consul")
    reg_parser.add_argument("service_name", help="Human-readable service name")
    reg_parser.add_argument("address", help="Upstream service address (IP or DNS)")
    reg_parser.add_argument("port", help="Upstream service port")
    reg_parser.add_argument("domains", nargs="*", help="One or more domain names for Traefik Host() rule")
    reg_parser.add_argument("--middlewares", nargs="*", help="Traefik middleware refs, e.g. auth@file,ratelimit@file")
    reg_parser.add_argument("--https-insecure", action="store_true",
                            help="Use HTTPS upstream with InsecureSkipVerify via serversTransport")
    reg_parser.add_argument("--disable-tls", action="store_true",
                            help="Disable TLS termination in Traefik (use entrypoint 'web')")

    # deregister
    dereg_parser = subparsers.add_parser("deregister", help="Deregister a service")
    dereg_parser.add_argument("public_ip", help="Alias name that maps to an internal Consul IP")
    dereg_parser.add_argument("service_id", help="Service ID to deregister")

    # list services
    list_parser = subparsers.add_parser("list", help="List services")
    list_parser.add_argument("public_ip", help="Alias name that maps to an internal Consul IP")

    # list traefik routers
    list_traefik_parser = subparsers.add_parser("list-traefik", help="List Traefik routers")
    list_traefik_parser.add_argument("public_ip", help="Alias name that maps to an internal Consul IP")

    # list middlewares
    list_middlewares_parser = subparsers.add_parser("list-middlewares", help="List Traefik middlewares")
    list_middlewares_parser.add_argument("public_ip", help="Alias name that maps to an internal Consul IP")

    # alias management
    alias_parser = subparsers.add_parser("alias", help="Manage IP aliases")
    alias_subparsers = alias_parser.add_subparsers(dest="alias_command")

    alias_add = alias_subparsers.add_parser("add", help="Add an alias")
    alias_add.add_argument("name", help="Alias name, e.g., 'jim'")
    alias_add.add_argument("ip", help="Internal Consul IP for that alias")

    alias_remove = alias_subparsers.add_parser("remove", help="Remove an alias")
    alias_remove.add_argument("name", help="Alias name to remove")

    alias_subparsers.add_parser("list", help="List aliases")

    # version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "alias":
        config = load_config()
        aliases = config.get("aliases", {})

        if args.alias_command == "add":
            aliases[args.name] = args.ip
            config["aliases"] = aliases
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Alias '{args.name}' set to {args.ip}")

        elif args.alias_command == "remove":
            if args.name in aliases:
                del aliases[args.name]
                config["aliases"] = aliases
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=4)
                print(f"Alias '{args.name}' removed.")
            else:
                print(f"No such alias: {args.name}")
                sys.exit(1)

        elif args.alias_command == "list":
            if aliases:
                print("Configured aliases:")
                for name, ip in aliases.items():
                    print(f"  {name}: {ip}")
            else:
                print("No aliases configured.")
        else:
            print("Invalid alias subcommand.")
            sys.exit(1)

    elif args.command == "version":
        print("version: 0.1.16")
        sys.exit(0)

    elif args.command == "register":
        if not args.domains:
            print("Error: you must provide at least one domain for the router rule (e.g., example.com).")
            sys.exit(2)
        register_service(
            args.public_ip,
            args.service_id,
            args.service_name,
            args.address,
            args.port,
            args.domains,
            middlewares=args.middlewares,
            https_insecure=args.https_insecure,
            disable_tls=args.disable_tls
        )

    elif args.command == "deregister":
        deregister_service(args.public_ip, args.service_id)

    elif args.command == "list":
        list_services(args.public_ip)

    elif args.command == "list-traefik":
        list_traefik(args.public_ip)

    elif args.command == "list-middlewares":
        list_middlewares(args.public_ip)

if __name__ == "__main__":
    main()
