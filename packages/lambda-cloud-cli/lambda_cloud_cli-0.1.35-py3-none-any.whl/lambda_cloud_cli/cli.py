# ─────────────────────────────────────────────
# 📚 Standard Library Imports
# ─────────────────────────────────────────────
import os
import sys
import time
import subprocess
import random
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional,List
from datetime import datetime

# ─────────────────────────────────────────────
# 🌐 Third-party Libraries
# ─────────────────────────────────────────────
import requests
import typer

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # For Python < 3.8

# ─────────────────────────────────────────────
# 📦 Internal Modules
# ─────────────────────────────────────────────
from lambda_cloud_cli.lambda_api_client import LambdaAPIClient
from lambda_cloud_cli.config import load_api_key, save_api_key, delete_api_key, CONFIG_PATH

# ─────────────────────────────────────────────
# 🚀 CLI Entry & Client Initialization
# ─────────────────────────────────────────────

app = typer.Typer()
client=None

# ─────────────────────────────────────────────
# 🔧 Utility Functions
# ─────────────────────────────────────────────

# Client & Authentication Utilities

def get_client():
    global client
    if client is None:
        API_KEY = os.environ.get("API_KEY") or load_api_key()
        if not API_KEY:
            typer.echo("❌ No API key set. Run: lambda-cli login")
            raise typer.Exit(code=1)
        client = LambdaAPIClient(api_key=API_KEY)
    return client

# SSH Key Utilities

def prompt_ssh_key_selection():
    keys = get_client().list_ssh_keys().get("data", [])
    if not keys:
        typer.secho("❌ No SSH keys available in your account.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo("🔐 Select an SSH key to use:\n")

    for idx, key in enumerate(keys, start=1):
        preview = key["public_key"][:30] + "..."
        typer.echo(f"{idx}. {key['name']:<20} {preview}")

    choice = typer.prompt("Enter the number of your choice", type=int, default=1)

    if not (1 <= choice <= len(keys)):
        typer.secho("❌ Invalid selection.", fg=typer.colors.RED)
        raise typer.Exit()

    selected = keys[choice - 1]["name"]
    typer.echo(f"✅ Selected SSH key: {selected}")
    return selected

# File System Utilities

def prompt_file_system_selection(region_name: str):
    fs_list = get_client().list_file_systems().get("data", [])
    matching = [fs for fs in fs_list if fs["region"] == region_name]

    if not matching:
        typer.echo("ℹ️  No file systems available in this region.")
        return None, None, None

    typer.echo(f"\nAvailable file systems in {region_name}:\n")
    for idx, fs in enumerate(matching, 1):
        typer.echo(f"{idx}. {fs['name']}")

    choice = typer.prompt("Enter the number of the file system to mount", type=int, default=1)
    selected_fs = matching[choice - 1]
    default_mount = f"/lambda/nfs/{selected_fs['name']}"
    mount_point = typer.prompt("Enter mount point", default=default_mount)

    return selected_fs["id"], selected_fs["name"], mount_point

# Filter Utilities

def get_region_name(region_field):
    if isinstance(region_field, str):
        return region_field
    if isinstance(region_field, dict):
        return region_field.get("name")
    return None

# Billing Utilities

def format_price_estimate(price_cents: int) -> str:
    hourly = price_cents / 100
    daily = hourly * 24
    monthly = daily * 30
    return (
        f"${hourly:,.2f}/hr  |  "
        f"${daily:,.2f}/day  |  "
        f"${monthly:,.2f}/month"
    )

# Jupyter Integration

def wait_for_jupyter(inst_id: str, open_browser: bool):
    typer.echo("⏳ Monitoring in the background: your instance will launch and Jupyter will open when ready.")

    for _ in range(180):  # ~15 minutes
        time.sleep(5)
        current = get_client().get_instance(inst_id).get("data", {})
        if current.get("status") == "active":
            url = current.get("jupyter_url")
            if url:
                typer.secho("📓 Jupyter is ready!", fg=typer.colors.GREEN)
                typer.echo(f"🔗 {url}")
                if open_browser:
                    import webbrowser
                    webbrowser.open(url)
            else:
                typer.secho("⚠️ Jupyter URL not available yet.", fg=typer.colors.YELLOW)
            break
    else:
        typer.secho("❌ Timed out waiting for Jupyter to become available.", fg=typer.colors.RED)

# ─────────────────────────────────────────────
# 🔐 Authentication Commands // login, logout, whoami
# ─────────────────────────────────────────────

@app.command(name="login", help="Authenticate with your Lambda Cloud API key")
def login(force: bool = typer.Option(False, "--force", help="Overwrite existing stored key")):
    """Set your Lambda Cloud API key"""
    existing_key = load_api_key()
    if existing_key and not force:
        typer.secho("🔒 You are already logged in with an API key.", fg=typer.colors.YELLOW)
        typer.echo("👉 Run 'lambda-cli logout' or use '--force' to overwrite it.")
        raise typer.Exit()

    api_key = typer.prompt("🔐 Enter your Lambda Cloud API key", hide_input=True)
    save_api_key(api_key)
    typer.echo("✅ API key saved.")
    
@app.command(name="logout",help="Remove your stored API key")
def logout():
    """Remove your stored API key"""
    if delete_api_key():
        typer.echo("✅ API key removed. You are now logged out.")
    else:
        typer.echo("ℹ️  No API key was stored.")

@app.command(name="whoami", help="Show the current authentication status and account info")
def whoami():
    """Show currently authenticated Lambda Cloud identity"""
    api_key = load_api_key()

    if not api_key:
        typer.secho("🚫 Not logged in.", fg=typer.colors.RED)
        typer.echo("👉 Run `lambda-cli login` to authenticate.")
        raise typer.Exit()

    if len(api_key) > 10:
        masked = api_key[:6] + "*" * (len(api_key) - 10) + api_key[-4:]
    else:
        masked = "*" * len(api_key)

    typer.secho("🔐 Authenticated", fg=typer.colors.GREEN)
    typer.echo(f"🔑 API Key: {masked}")

    try:
        keys = get_client().list_ssh_keys().get("data", [])
        typer.echo(f"🔐 SSH keys: {len(keys)} found")
        for key in keys:
            typer.echo(f"• {key['name']}")
    except Exception:
        typer.echo("⚠️ Could not fetch SSH keys")

# ─────────────────────────────────────────────
# 🚀 Instance Lifecycle Commands // launch-instance, clone-instance, interactive-launch, interactive-clone 
# ─────────────────────────────────────────────

@app.command(name="launch-instance",help="Launch a new instance in your Lambda Cloud account")
def launch_instance(
    region_name: str = typer.Option(..., "--region-name", help="Lambda region (e.g. us-west-1)"),
    instance_type: str = typer.Option(..., "--instance-type", help="Instance type (e.g. gpu_1x_a10)"),
    ssh_key_name: str = typer.Option(..., "--ssh-key-name", help="Your SSH key name"),
    name: Optional[str] = typer.Option(None, "--name", help="Name for your instance"),
    auto_name: bool = typer.Option(False, "--auto-name", help="Auto-generate a name if --name is not provided"),
    image_id: Optional[str] = typer.Option(None, "--image-id", help="Optional image ID"),
    file_system_name: Optional[str] = typer.Option(None, "--file-system-name", help="Attach an existing file system"),
    mount_point: Optional[str] = typer.Option("/mnt/fs", "--mount-point", help="Mount point for the file system"),
    auto_open_jupyter: bool = typer.Option(False, "--auto-open-jupyter", help="Open Jupyter URL in your browser if available"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before launch"),
):

    # 🧠 1. Ensure either --name or --auto-name is provided
    if not name and not auto_name:
        typer.secho("❌ You must provide --name or use --auto-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # ⚠️ 2. Generate name if --auto-name is used
    if auto_name and not name:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"lambda-cli-{timestamp}"
        typer.echo(f"🆕 Auto-generated name: {name}")

    # 🔍 3. Validate uniqueness of the instance name
    existing = get_client().list_instances().get("data", [])
    if any(inst["name"] == name for inst in existing):
        typer.secho(f"❌ An instance with the name '{name}' already exists.", fg=typer.colors.RED)
        typer.echo("💡 Choose a different name or use --auto-name")
        raise typer.Exit(code=1)

    payload = {
        "region_name": region_name,
        "instance_type_name": instance_type,
        "ssh_key_names": [ssh_key_name],
        "name": name
    }

    if image_id:
        payload["image"] = {"id": image_id}

    if file_system_name:
        typer.echo()  # Blank line for spacing

        # 🔍 Resolve file system ID from name in the selected region
        all_fs = get_client().list_file_systems().get("data", [])
        available_fs = [fs for fs in all_fs if fs["region"]["name"] == region_name]

        match = next((fs for fs in available_fs if fs["name"] == file_system_name), None)

        if not match:
            # 🐞 Diagnostic output
            typer.secho(f"ℹ️  Available file systems in region '{region_name}':", fg=typer.colors.YELLOW)
            for fs in available_fs:
                typer.echo(f"• {fs['name']} ({fs['region']['name']})")
            typer.secho(f"❌ File system '{file_system_name}' not found in region '{region_name}'", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        fs_id = match["id"]

        payload["file_system_names"] = [file_system_name]
        payload["file_system_mounts"] = [{
            "file_system_id": fs_id,
            "mount_point": mount_point
        }]

        typer.echo(f"✅ File system '{file_system_name}' will be mounted at '{mount_point}'")
        typer.echo()  # Extra space after confirmation

    # 👁️ Preview before launch
    if not yes:
        typer.echo("\n🧾 Instance Launch Preview:\n")
        typer.echo(f"• Name:              {name}")
        typer.echo(f"• Region:            {region_name}")
        typer.echo(f"• Instance type:     {instance_type}")
        typer.echo(f"• SSH key:           {ssh_key_name}")
        
        if file_system_name and mount_point:
            typer.echo(f"• File system:       {file_system_name}")
            typer.echo(f"   ↳ Mount point ➜   {mount_point}")
        if payload.get("firewall_rulesets"):
            ids = [r["id"] for r in payload["firewall_rulesets"]]
            typer.echo(f"• Firewall rulesets: {', '.join(ids)}")
            
        typer.echo()
        
        confirm = typer.confirm("🚀 Proceed with launching this instance?")
        if not confirm:
            typer.echo("🚫 Launch cancelled.")
            raise typer.Exit()

    typer.echo()

    instance_types = get_client().list_instance_types().get("data", {})
    match = next((t for t in instance_types.values() if t["instance_type"]["name"] == instance_type), None)
    if match:
        cents = match.get("instance_type", {}).get("price_cents_per_hour", 0)
        typer.secho("💵 Estimated Billing:", fg=typer.colors.CYAN)
        typer.echo(f"  {format_price_estimate(cents)}")
        typer.echo()

    result = get_client().launch_instance(payload)
    typer.echo("🚀 Launch request sent!")

    if 'error' in result:
        typer.secho(f"❌ {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get('suggestion')
        if suggestion:
            typer.echo(f"💡 {suggestion}")
    else:
        typer.secho("✅ Instance launched successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

        # 📓 Jupyter launching logic (always attempt to check for Jupyter)
        data = result.get("data", {})
        inst_id = data.get("id") or (data.get("instance_ids") or [None])[0]
        
        if not inst_id:
            typer.secho("❌ Could not determine instance ID from the response.", fg=typer.colors.RED)
            return

            try:
                thread = threading.Thread(target=wait_for_jupyter, args=(inst_id, auto_open_jupyter), daemon=True)
                thread.start()
            except Exception as e:
                typer.secho("⚠️ Could not start Jupyter watcher thread.", fg=typer.colors.YELLOW)
                typer.echo(str(e))

@app.command(name="clone-instance", help="Clone an existing instance in your Lambda Cloud account")
def clone_instance(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="ID of the instance to clone"),
    instance_name: Optional[str] = typer.Option(None, "--instance-name", help="Name of the instance to clone"),
    new_name: Optional[str] = typer.Option(None, "--new-name", help="Name for the new cloned instance"),
    auto_name: bool = typer.Option(False, "--auto-name", help="Auto-generate a name if --new-name is not provided"),
    ssh_key_name: Optional[str] = typer.Option(None, "--ssh-key-name", help="Optional SSH key name to override the original"),
    include_filesystem: bool = typer.Option(False, "--include-filesystem", help="Include the original file system and mounts"),
    auto_open_jupyter: bool = typer.Option(False, "--auto-open-jupyter", help="Open Jupyter URL in your browser if available"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before launching"),
):
    """Clone a Lambda Cloud instance using the same specs but a new name (and optionally a new SSH key)."""
    if not instance_id and not instance_name:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if not new_name and not auto_name:
        typer.secho("❌ Provide --new-name or use --auto-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 🔎 Find source instance
    all_instances = get_client().list_instances().get("data", [])
    if instance_name:
        source = next((i for i in all_instances if i["name"] == instance_name), None)
    elif instance_id:
        source = next((i for i in all_instances if i["id"] == instance_id), None)
    else:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit()

    if not source:
        label = instance_name or instance_id
        typer.secho(f"❌ No instance found with: {label}", fg=typer.colors.RED)
        raise typer.Exit()

    # 🧠 Auto-name if requested
    if auto_name:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        new_name = f"lambda-clone-{timestamp}"
        typer.echo(f"🆕 Auto-generated name: {new_name}")

    # 🚫 Prevent name collision
    if any(i.get("name") == new_name for i in all_instances):
        typer.secho(f"❌ An instance named '{new_name}' already exists", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 🔐 SSH key: use provided or prompt
    key_name = ssh_key_name or prompt_ssh_key_selection()

    # 🧱 Build payload
    payload = {
        "region_name": source["region"]["name"],
        "instance_type_name": source["instance_type"]["name"],
        "ssh_key_names": [key_name],
        "name": new_name,
        "hostname": source.get("hostname", ""),
        "user_data": source.get("user_data", ""),
        "tags": source.get("tags", []),
        "firewall_rulesets": source.get("firewall_rulesets", [])
    }

    if include_filesystem:
        payload["file_system_names"] = source.get("file_system_names", [])
        payload["file_system_mounts"] = source.get("file_system_mounts", [])

    # 👀 Preview before confirmation
    if not yes:
        typer.echo("\n🧾 Clone Instance Preview:\n")
        typer.echo(f"• New name:          {new_name}")
        typer.echo(f"• Region:            {payload['region_name']}")
        typer.echo(f"• Instance type:     {payload['instance_type_name']}")
        typer.echo(f"• SSH key:           {key_name}")

        # ✅ File system & mount preview (only if included)
        if include_filesystem and payload.get("file_system_names"):
            typer.echo(f"• File systems:      {', '.join(payload['file_system_names'])}")
            for mount in payload.get("file_system_mounts", []):
                fs_id = mount.get("file_system_id", "unknown")
                mount_point = mount.get("mount_point", "unknown")
                typer.echo(f"   ↳ Mount {fs_id} ➜ {mount_point}")

        if payload.get("firewall_rulesets"):
            ruleset_ids = [r.get('id') for r in payload["firewall_rulesets"]]
            typer.echo(f"• Firewall rulesets: {', '.join(ruleset_ids)}")

        typer.echo()

        confirm = typer.confirm("🚀 Launch this cloned instance?")
        if not confirm:
            typer.echo("🚫 Launch cancelled.")
            raise typer.Exit()

    # 💵 Estimated billing 
    price = source.get("instance_type", {}).get("price_cents_per_hour")
    if price:
        typer.echo()
        typer.secho("💵 Estimated Billing:", fg=typer.colors.CYAN)
        typer.echo(f"  {format_price_estimate(price)}")
        typer.echo()
    
    # 🚀 Launch
    typer.echo("🚀 Launching cloned instance...")
    result = get_client().launch_instance(payload)

    if result.get("error"):
        typer.secho(f"❌ Error: {result['error']['message']}", fg=typer.colors.RED)
        if result["error"].get("suggestion"):
            typer.echo(f"💡 {result['error']['suggestion']}")
    else:
        typer.secho("✅ Instance cloned successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

        # 📓 Jupyter launching logic (always attempt to check for Jupyter)
        inst_id = result["data"].get("id") or result["data"]["instance_ids"][0]
        thread = threading.Thread(target=wait_for_jupyter, args=(inst_id, auto_open_jupyter), daemon=True)
        thread.start()

# ─────────────────────────────────────────────
# 🧠 Interactive Tool Commands // interactive-launch, interactive-clone 
# ─────────────────────────────────────────────

@app.command(name="interactive-launch", help="Launch a new instance via interactive prompts")
def interactive_launch():
    """Step-by-step interactive wizard to launch a new Lambda instance"""

    typer.secho("🧙 Interactive Instance Wizard", fg=typer.colors.MAGENTA, bold=True)

    client = get_client()

    typer.echo()
    # 1️⃣ Region Selection
    regions = [
        {"name": "us-west-1", "label": "California, USA"},
        {"name": "us-midwest-1", "label": "Illinois, USA"},
        {"name": "eu-central-1", "label": "Frankfurt, Germany"},
    ]

    typer.echo("🌍 Select a region:")
    for idx, r in enumerate(regions, start=1):
        typer.echo(f"{idx}. {r['name']} ({r['label']})")

    region_choice = typer.prompt("Enter the number of your choice",type=int)
    region_name = regions[region_choice - 1]["name"]

    # 2️⃣ Instance Type Selection
    types_dict = client.list_instance_types().get("data", {})
    sorted_types = sorted(types_dict.values(), key=lambda t: t["instance_type"]["specs"].get("gpus", 0))

    typer.echo("\n🧠 Select an instance type:")
    for i, t in enumerate(sorted_types, start=1):
        inst = t["instance_type"]
        name = inst["name"]
        gpus = inst["specs"].get("gpus", "?")
        price = inst["price_cents_per_hour"] / 100
        typer.echo(f"{i}. {name:<25} ({gpus} GPUs, ${price:.2f}/hr)")

    type_choice = typer.prompt("Enter the number of your choice", type=int)
    instance_type = sorted_types[type_choice - 1]["instance_type"]["name"]
    instance_price = sorted_types[type_choice - 1]["instance_type"]["price_cents_per_hour"] / 100

    price_cents = sorted_types[type_choice - 1]["instance_type"].get("price_cents_per_hour")
    if price_cents is None:
        typer.secho("❌ Selected instance type is missing pricing information.", fg=typer.colors.RED)
        raise typer.Exit()
    instance_price = price_cents / 100


    # 3️⃣ SSH Key
    ssh_keys = client.list_ssh_keys().get("data", [])

    if not ssh_keys:
        typer.secho("❌ No SSH keys found. Please add one using `lambda-cli add-ssh-key`.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo("\n🔐 Select an SSH key:")
    for idx, key in enumerate(ssh_keys, start=1):
        preview = key["public_key"][:30] + "..."
        typer.echo(f"{idx}. {key['name']} (ID: {key['id']}) - {preview}")

    ssh_choice = typer.prompt("Enter the number of your choice", type=int, default=1)
    ssh_key_name = ssh_keys[ssh_choice - 1]["name"]
    typer.echo()

    # 4️⃣ Name Prompt
    typed_name = input("🆕 Enter a name for the instance (press Enter to auto-generate): ").strip()
    if not typed_name:
        name = f"lambda-cli-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        typer.echo(f"🧠 Auto-generated name: {name}")
    else:
        name = typed_name

    # 🚫 Prevent name collision
    all_instances = get_client().list_instances().get("data", [])
    if any(i.get("name") == name for i in all_instances):
        typer.secho(f"❌ An instance named '{new_name}' already exists.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo()

        # Launch
    payload = {
        "region_name": region_name,
        "instance_type_name": instance_type,
        "ssh_key_names": [ssh_key_name],
        "name": name
    }
    
    # 5️⃣ File system (optional)
    file_system_id, file_system_name, mount_point = None, None, None

    fs_prompt = typer.confirm("🧱 Would you like to attach a file system to this instance?", default=False)

    if fs_prompt:

        all_fs = client.list_file_systems().get("data", [])
        fs_choices = [fs for fs in all_fs if fs["region"]["name"] == region_name]
        
        if not fs_choices:
            typer.echo("ℹ️  No file systems available in this region.")
        else:
            typer.echo()
            typer.echo(f"📂 Available file systems in {region_name}:")
            for idx, fs in enumerate(fs_choices, start=1):
                typer.echo(f"{idx}. {fs['name']}")

            fs_choice = typer.prompt("Enter the number of the file system to mount", type=int, default=1)

            if not (1 <= fs_choice <= len(fs_choices)):
                typer.secho("❌ Invalid selection.", fg=typer.colors.RED)
                raise typer.Exit()

            selected_fs = fs_choices[fs_choice - 1]
            file_system_id = selected_fs["id"]
            file_system_name = selected_fs["name"]
            default_mount = f"/lambda/nfs/{file_system_name}"
    
            typer.echo()
            typer.echo(f"Default mount point: {default_mount}")
            mount_point = typer.prompt("Enter mount point", default=default_mount)

            payload["file_system_names"] = [file_system_name]
            payload["file_system_mounts"] = [{
                "file_system_id": file_system_id,
                "mount_point": mount_point
            }]

    # Confirmation + Preview
    typer.echo("\n🧾 Instance Launch Preview:\n")
    typer.echo(f"• Name:              {name}")
    typer.echo(f"• Region:            {region_name}")
    typer.echo(f"• Instance type:     {instance_type}")
    typer.echo(f"• SSH key:           {ssh_key_name}")

    if file_system_name and mount_point:
        typer.echo(f"• File system:       {file_system_name}")
        typer.echo(f"   ↳ Mount point:    {mount_point}")

    typer.echo()
    hourly = instance_price
    daily = hourly * 24
    monthly = daily * 30
    typer.echo(f"💵 Estimated Billing: ${hourly:.2f}/hr, ${daily:.2f}/day, ${monthly:.2f}/month")
    typer.echo()

    confirm = typer.confirm("🚀 Launch this instance?",default=True)
    if not confirm:
        typer.echo("🚫 Launch cancelled.")
        raise typer.Exit()

    typer.echo("🚀 Launching...")
    result = client.launch_instance(payload)

    if "error" in result:
        typer.secho(f"❌ {result['error']['message']}", fg=typer.colors.RED)
        suggestion = result["error"].get("suggestion")
        if suggestion:
            typer.echo(f"💡 {suggestion}")
    else:
        typer.secho("✅ Instance launched successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

    # 📓 Jupyter launching logic (always attempt to check for Jupyter)
        inst_id = result["data"].get("id") or result["data"]["instance_ids"][0]
        if not inst_id:
            typer.secho("❌ Could not determine instance ID from the response.", fg=typer.colors.RED)
            return

        thread = threading.Thread(target=wait_for_jupyter, args=(inst_id, True), daemon=True)
        thread.start()

@app.command(name="interactive-clone", help="Clone an existing instance via interactive prompts")
def interactive_clone():
    """Step-by-step interactive wizard to clone an existing Lambda instance"""
    client = get_client()
    all_instances = client.list_instances().get("data", [])

    if not all_instances:
        typer.secho("❌ No instances available to clone.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.secho("🧙 Interactive Instance Wizard", fg=typer.colors.CYAN)
    typer.echo("\n📦 Available instances:")

    for i, inst in enumerate(all_instances, start=1):
        typer.echo(f"{i}. {inst['name']}  ({inst['id']})")
    choice = typer.prompt("Select the instance to clone", type=int, default=1)
    source = all_instances[choice - 1]

    typer.echo()
    typed_name = input("🆕 Enter a name for cloned instance (press Enter to auto-generate): ").strip()
    if not typed_name:
        new_name = f"lambda-clone-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        typer.echo(f"🧠 Auto-generated name: {new_name}")
    else:
        new_name = typed_name

    # 🔐 SSH Key Selection
    typer.echo()
    ssh_keys = get_client().list_ssh_keys().get("data", [])
    if not ssh_keys:
        typer.secho("❌ No SSH keys found. Please add one using `lambda-cli add-ssh-key`.", fg=typer.colors.RED)
        raise typer.Exit()

    default_key = source.get("ssh_key_names", [None])[0]

    if default_key: 
        key_obj = next((k for k in ssh_keys if k["name"] == default_key), None)
        if key_obj:
            typer.echo(f"🔐 The original instance used SSH key: {default_key} (ID: {key_obj['id']})")
        else:
            typer.echo(f"🔐 The original instance used SSH key: {default_key}")

        use_same = typer.confirm("Would you like to use the same SSH key?", default=True)
        if use_same:
            key_name = default_key
        else:
            typer.echo("\n🔐 Select an SSH key:")
            for idx, key in enumerate(ssh_keys, start=1):
                preview = key["public_key"][:30] + "..."
                typer.echo(f"{idx}. {key['name']} (ID: {key['id']}) - {preview}")
            ssh_choice = typer.prompt("Enter the number of your choice", type=int, default=1)
            key_name = ssh_keys[ssh_choice - 1]["name"]
    else:
        typer.echo("🔐 The original instance did not have an SSH key assigned.")
        typer.echo("You must now choose an SSH key.")
        typer.echo("\n🔐 Select an SSH key:")
        for idx, key in enumerate(ssh_keys, start=1):
            preview = key["public_key"][:30] + "..."
            typer.echo(f"{idx}. {key['name']} (ID: {key['id']}) - {preview}")
        ssh_choice = typer.prompt("Enter the number of your choice", type=int)
        key_name = ssh_keys[ssh_choice - 1]["name"]

    typer.echo()

        # Filesystem
    include_fs = typer.confirm("🧱 Clone and reattach the original file system from source?", default=True)

    # Prepare payload
    payload = {
        "region_name": source["region"]["name"],
        "instance_type_name": source["instance_type"]["name"],
        "ssh_key_names": [key_name],
        "hostname": source.get("hostname", ""),
        "user_data": source.get("user_data", ""),
        "tags": source.get("tags", []),
        "firewall_rulesets": source.get("firewall_rulesets", [])
    }

    if include_fs:
        payload["file_system_names"] = source.get("file_system_names", [])
        payload["file_system_mounts"] = source.get("file_system_mounts", [])

    # 💵 Billing
    price_cents = source["instance_type"].get("price_cents_per_hour", 0)
    instance_price = price_cents / 100

    # Preview
    typer.echo("\n🧾 Clone Preview:\n")
    typer.echo(f"• New name:          {new_name}")
    typer.echo(f"• Region:            {payload['region_name']}")
    typer.echo(f"• Instance type:     {payload['instance_type_name']}")
    typer.echo(f"• SSH key:           {key_name}")

    if include_fs and payload.get("file_system_names"):
        typer.echo(f"• File systems:      {', '.join(payload['file_system_names'])}")
        for mount in payload.get("file_system_mounts", []):
            fs_id = mount.get("file_system_id", "unknown")
            mount_point = mount.get("mount_point", "unknown")
            typer.echo(f"   ↳ Mount {fs_id} ➜ {mount_point}")

    typer.echo()
    hourly = instance_price
    daily = hourly * 24
    monthly = daily * 30
    typer.echo(f"💵 Estimated Billing: ${hourly:.2f}/hr, ${daily:.2f}/day, ${monthly:.2f}/month")
    typer.echo()

    confirm = typer.confirm("🚀 Launch this cloned instance?",default=True)
    if not confirm:
        typer.echo("❌ Cancelled.")
        raise typer.Exit()

    payload["name"] = new_name
    result = client.launch_instance(payload)

    if result.get("error"):
        typer.secho(f"❌ Error: {result['error']['message']}", fg=typer.colors.RED)
        if result["error"].get("suggestion"):
            typer.echo(f"💡 {result['error']['suggestion']}")
    else:
        typer.secho("✅ Instance cloned successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

        # 📓 Jupyter launching logic (always attempt to check for Jupyter)
        inst_id = result["data"].get("id") or result["data"]["instance_ids"][0]
        if not inst_id:
            typer.secho("❌ Could not determine instance ID from the response.", fg=typer.colors.RED)
            return

        thread = threading.Thread(target=wait_for_jupyter, args=(inst_id, True), daemon=True)
        thread.start()

# ─────────────────────────────────────────────
# 🧹 Instance Management Commands // update_instance_name, terminate_instance, open_jupyter
# ─────────────────────────────────────────────

@app.command(name="update-instance-name", help="Rename an existing instance in your Lambda Cloud account")
def update_instance_name(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Instance ID to rename"),
    instance_name: Optional[str] = typer.Option(None, "--instance-name", help="Instance name to rename"),
    new_name: str = typer.Option(..., "--new-name", help="New name for the instance")
):
    """Renames an instance using either its ID or name"""
    
    if not instance_id and not instance_name:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if instance_name:
        all_instances = get_client().list_instances().get("data", [])
        match = next((i for i in all_instances if i["name"] == instance_name), None)
        if not match:
            typer.secho(f"❌ No instance found with name: {instance_name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        instance_id = match["id"]

    # 🔍 Check for name conflict
    existing_instances = get_client().list_instances().get("data", [])
    if any(inst["name"] == new_name for inst in existing_instances):
        typer.secho(f"❌ An instance named '{new_name}' already exists.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    result = get_client().update_instance_name(instance_id, new_name)

    if isinstance(result, dict) and result.get("error"):
        typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        return

    updated_name = result.get("data", {}).get("name", new_name)
    typer.secho("✅ Instance renamed successfully!", fg=typer.colors.GREEN)
    typer.echo(f"🆔 {instance_id}")
    typer.echo(f"🔤 New name: {updated_name}")

@app.command(name="terminate-instance", help="Terminate one or more Lambda Cloud instances by ID or name")
def terminate_instance(
    instance_ids: List[str] = typer.Option(None, "--instance-id", help="Instance ID to terminate (use multiple times)"),
    instance_names: List[str] = typer.Option(None, "--instance-name", help="Instance name to terminate (use multiple times)"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before termination")
):
    """Terminate Lambda Cloud instances by their IDs or names."""

    all_instances = get_client().list_instances().get("data", [])
    id_to_instance = {i["id"]: i for i in all_instances}
    name_to_id = {i["name"]: i["id"] for i in all_instances}

    resolved_ids = set(instance_ids or [])
    preview_names = []

    # 🔍 Resolve names to IDs
    for name in instance_names or []:
        if name not in name_to_id:
            typer.secho(f"❌ No instance found with name: {name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        inst_id = name_to_id[name]
        resolved_ids.add(name_to_id[name])
        preview_names.append((name, name_to_id[name]))

    if not resolved_ids:
        typer.secho("❌ No instances specified for termination.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo(f"🗑 Preparing to terminate {len(resolved_ids)} instance(s)...")

    # 📋 Preview selected instances
    if not yes:
        typer.echo("\n🗒 Instances selected for termination:\n")
        for inst_id in resolved_ids:
            inst = id_to_instance.get(inst_id)
            label = f"{inst['name']} (ID: {inst_id})" if inst else inst_id
            typer.echo(f"• {label}")
        typer.echo()

        confirm = typer.confirm(f"⚠️  Are you sure you want to terminate these {len(resolved_ids)} instance(s)?")
        if not confirm:
            typer.echo("🚫 Termination cancelled.")
            raise typer.Exit()

    else:
        typer.echo(f"✅ --yes flag detected, skipping preview. Terminating {len(resolved_ids)} instance(s)...")

    # 🚀 Terminate all selected instance IDs
    result = get_client().terminate_instances(list(resolved_ids))

    if isinstance(result, dict) and result.get("error"):
        typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        return

    terminated = result.get("data", {}).get("terminated_instances", [])
    if not terminated:
        typer.secho("⚠️  Termination request completed but returned no terminated instances.", fg=typer.colors.YELLOW)
        return

    typer.echo(f"\n🗑 Terminated {len(terminated)} instance(s):\n")

    for inst in terminated:
        typer.echo(f"  IP: {inst.get('ip', 'N/A')}")
        typer.echo(f"  Status: {inst.get('status', 'unknown')}")
        typer.echo(f"  IP: {inst.get('ip', 'N/A')}")
        typer.echo(f"  Type: {inst.get('instance_type', {}).get('name', 'N/A')}")
        typer.echo(f"  Region: {inst.get('region', {}).get('name', 'N/A')}\n")
        
@app.command(name="open-jupyter", help="Open the Jupyter URL for an active instance")
def open_jupyter(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Instance ID"),
    instance_name: Optional[str] = typer.Option(None, "--instance-name", help="Instance name")
):
    """Open the Jupyter notebook URL in a browser for a running instance"""
    
    if not instance_id and not instance_name:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    #Fetch Instances
    instances = get_client().list_instances().get("data", [])
    match = None

    #Match by Name or ID
    if instance_name:
        match = next((i for i in instances if i["name"] == instance_name), None)
    elif instance_id:
        match = next((i for i in instances if i["id"] == instance_id), None)

    if not match:
        typer.secho("❌ No matching instance found.", fg=typer.colors.RED)
        raise typer.Exit()

    #Status Check
    status = match.get("status")
    if status != "active":
        typer.secho(f"⚠️ Instance is not active (current status: {status})", fg=typer.colors.YELLOW)
        raise typer.Exit()

    #Check Jupyter URL
    url = match.get("jupyter_url")
    if not url:
        typer.secho("❌ No Jupyter URL found for this instance.", fg=typer.colors.RED)
        raise typer.Exit()

    #Attempt to open
    typer.echo(f"🔗 Opening Jupyter in your browser: {url}")
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception as e:
        typer.secho("❌ Failed to open browser.", fg=typer.colors.RED)
        typer.echo(str(e))

# ─────────────────────────────────────────────
# 📊 Monitoring & Metadata Commands // list_instances, billing
# ─────────────────────────────────────────────

@app.command(name="get-instance", help="Show details for a specific instance by ID or name")
def get_instance_cmd(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Instance ID"),
    instance_name: Optional[str] = typer.Option(None, "--instance-name", help="Instance name"),
    json_output: bool = typer.Option(False, "--json", help="Print raw API JSON"),
):
    """Describe an instance by ID or name."""
    if bool(instance_id) == bool(instance_name):
        typer.secho("❌ Provide exactly one of --instance-id or --instance-name.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    client = get_client()

    # Resolve by name → ID (search all instances, any status)
    if instance_name:
        all_instances = client.list_instances().get("data", []) or []
        match = next((i for i in all_instances if i.get("name") == instance_name), None)
        if not match:
            typer.secho(f"❌ No instance found with name: {instance_name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        instance_id = match["id"]

    # Fetch details
    result = client.get_instance(instance_id)
    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)

    if json_output:
        import json as _json
        typer.echo(_json.dumps(result, indent=2))
        return

    data = result.get("data", {}) if isinstance(result, dict) else result
    region_field = data.get("region", {}) or {}
    region_name = get_region_name(region_field) or "unknown"
    region_label = region_field.get("label") if isinstance(region_field, dict) else None
    rdisp = f"{region_name} ({region_label})" if region_label else region_name

    typer.echo(f"ID:         {data.get('id')}")
    typer.echo(f"Name:       {data.get('name')}")
    typer.echo(f"Status:     {data.get('status')}")
    typer.echo(f"Region:     {rdisp}")
    typer.echo(f"Type:       {data.get('instance_type',{}).get('name')}")
    typer.echo(f"Public IP:  {data.get('ip') or '-'}")
    typer.echo(f"Jupyter:    {data.get('jupyter_url') or '-'}")
    if data.get("tags"):
        typer.echo(f"Tags:       {', '.join(data.get('tags'))}")

@app.command(name="list-instances", help="List all instances in your Lambda Cloud account")
def list_instances(
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region (e.g. us-west-1)")
):
    """List all active or booting instances, optionally filtered by region"""
    instances = get_client().list_instances().get("data", [])
    instances = [i for i in instances if i.get("status") in ["active", "booting"]]

    if region:
        instances = [i for i in instances if i.get("region", {}).get("name") == region]

    if not instances:
        typer.secho("ℹ️  No matching instances found.", fg=typer.colors.YELLOW)
        return

    # Column widths
    id_width = 36
    name_width = 28
    type_width = 30
    status_width = 12
    region_width = 20

    # Header
    header = (
        f"{'ID':<{id_width}}  "
        f"{'Name':<{name_width}}  "
        f"{'Type':<{type_width}}  "
        f"{'Status':<{status_width}}  "
        f"{'Region':<{region_width}}"
    )
    typer.echo(header)
    typer.echo("-" * (len(header)-5))

    # Rows
    for inst in instances:
        inst_id = inst.get("id", "")
        name = inst.get("name", "")
        inst_type = inst.get("instance_type", {}).get("name", "N/A")
        status = inst.get("status", "unknown")
        region_name = inst.get("region", {}).get("name", "unknown")

        # 🎨 Colorize status only
        status_color = (
            typer.colors.GREEN if status == "active"
            else typer.colors.YELLOW if status == "booting"
            else typer.colors.RED
        )
        
        raw_status = status.ljust(status_width)
        status_str = typer.style(raw_status, fg=status_color)

        # Output the row with only status colored
        typer.echo(
            f"{inst_id:<{id_width}}  "
            f"{name:<{name_width}}  "
            f"{inst_type:<{type_width}}  "
            f"{status_str:<{status_width}}  "
            f"{region_name:<{region_width}}"
        )

    typer.echo()
    typer.secho(f"🧾 Total: {len(instances)} instance(s) listed.", fg=typer.colors.CYAN)

@app.command(name="billing", help="Estimate hourly, daily, and monthly costs for active instances")
def billing(
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region (e.g. us-west-1)"),
    name_contains: Optional[str] = typer.Option(None, "--name-contains", help="Filter by substring in instance names")
):
    """Show estimated billing costs for your currently running Lambda Cloud instances."""
    
    instances = get_client().list_instances().get("data", [])
    if not instances:
        typer.secho("ℹ️  No instances found in your account.", fg=typer.colors.YELLOW)
        return

    total_cents_per_hr = 0
    matched = []

    for inst in instances:
        if inst.get("status") not in ["active", "booting"]:
            continue
        if region and inst.get("region", {}).get("name") != region:
            continue
        if name_contains and name_contains not in inst.get("name", ""):
            continue
        matched.append(inst)

    if not matched:
        typer.secho("ℹ️  No matching active instances found.", fg=typer.colors.YELLOW)
        return

    typer.echo("🧾 Current Billing Estimate\n")

    for inst in matched:
        name = inst.get("name", "(no name)")
        instance_type = inst.get("instance_type", {}).get("name", "unknown")
        cents_per_hour = inst.get("instance_type", {}).get("price_cents_per_hour", 0)
        total_cents_per_hr += cents_per_hour

        typer.echo(f"• {name} ({instance_type})")
        typer.echo(f"  {format_price_estimate(cents_per_hour)}\n")  # Using your utility function

    total_hr = total_cents_per_hr / 100
    total_day = total_hr * 24
    total_month = total_day * 30

    typer.echo("────────────────────────────────────────────")
    typer.secho(
        f"💰 Total: ${total_hr:.2f}/hr | ${total_day:.2f}/day | ${total_month:.2f}/month",
        fg=typer.colors.CYAN
    )

# ─────────────────────────────────────────────
# 📊 Infrastructure Reference Commands // list_instance_types, list_ssh_keys, list_file_systems
# ─────────────────────────────────────────────

@app.command(name="list-instance-types", help="Show all available Lambda Cloud instance types with GPU count and specs")
def list_instance_types():
    types_dict = get_client().list_instance_types().get("data", {})
    if not types_dict:
        typer.secho("ℹ️  No instance types found.", fg=typer.colors.YELLOW)
        return

    header = f"{'Name':<30} {'GPUs':<5} {'vCPUs':<6} {'Mem (GiB)':<10} {'$/hr':<6}"
    typer.echo(header)
    typer.echo("-" * len(header))

    for type_data in types_dict.values():
        inst = type_data.get("instance_type", {})
        name = inst.get("name", "unknown")
        gpus = inst.get("specs", {}).get("gpus", "?")
        vcpus = inst.get("specs", {}).get("vcpus", "?")
        mem = inst.get("specs", {}).get("memory_gib", "?")
        price = inst.get("price_cents_per_hour", 0) / 100

        typer.echo(f"{name:<30} {gpus:<5} {vcpus:<6} {mem:<10} ${price:.2f}")
        
@app.command(name="list-ssh-keys", help="List all SSH keys registered in your Lambda Cloud account")
def list_ssh_keys():
    keys = get_client().list_ssh_keys().get("data", [])
    if not keys:
        typer.secho("ℹ️  No SSH keys found in your account.", fg=typer.colors.YELLOW)
        return

    # Column widths
    id_width = 36
    name_width = 20
    preview_width = 50

    # Header
    header = (
        f"{'ID':<{id_width}}  "
        f"{'Name':<{name_width}}  "
        f"{'Public Key Preview':<{preview_width}}"
    )
    typer.echo(header)
    typer.echo("-" * (id_width + name_width + preview_width + 4))

    # Rows
    for key in keys:
        key_id = key.get("id", "")[:id_width]
        name = key.get("name", "")[:name_width]
        pubkey = key.get("public_key", "")
        preview = (pubkey[:preview_width - 3] + "...") if len(pubkey) > preview_width else pubkey

        typer.echo(
            f"{key_id:<{id_width}}  "
            f"{name:<{name_width}}  "
            f"{preview:<{preview_width}}"
        )

    typer.echo()
    typer.secho(f"🔑 Total: {len(keys)} SSH key(s) listed.", fg=typer.colors.CYAN)
    
@app.command(name="list-file-systems", help="List all file systems in your Lambda Cloud account")
def list_file_systems(
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region (e.g. us-west-1)")
):
    """Lists file systems, optionally filtered by region"""
    filesystems = get_client().list_file_systems().get("data", [])
    if not filesystems:
        typer.secho("ℹ️  No file systems found.", fg=typer.colors.YELLOW)
        return

    if region:
        filesystems = [fs for fs in filesystems if get_region_name(fs.get("region")) == region]
        if not filesystems:
            typer.secho(f"ℹ️  No file systems found in region: {region}", fg=typer.colors.YELLOW)
            return

    filesystems.sort(key=lambda fs: fs.get("name", ""))

    # Set fixed column widths
    id_width = 36
    name_width = 20
    region_width = 30

    # Header
    header = (
        f"{'ID':<{id_width}}  "
        f"{'Name':<{name_width}}  "
        f"{'Region':<{region_width}}"
    )
    typer.echo(header)
    typer.echo("-" * (id_width + name_width + region_width + 4))

    # Rows
    for fs in filesystems:
        fs_id = fs.get("id", "")[:id_width]
        name = fs.get("name", "unnamed")[:name_width]

        region_field = fs.get("region", {})
        region_name = get_region_name(region_field)
        region_label = region_field.get("label") if isinstance(region_field, dict) else None
        label_display = f"{region_name} ({region_label})" if region_label else region_name

        typer.echo(
            f"{fs_id:<{id_width}}  "
            f"{name:<{name_width}}  "
            f"{label_display:<{region_width}}"
        )

    typer.echo()
    typer.secho(f"📂 Total: {len(filesystems)} file system(s) listed.", fg=typer.colors.CYAN)

# ─────────────────────────────────────────────
# 🔐 SSH Key Management Commands // add_ssh_key, delete_ssh_key
# ─────────────────────────────────────────────

@app.command(name="add-ssh-key", help="Register a new SSH public key with your Lambda Cloud account")
def add_ssh_key(
    name: str = typer.Option(..., "--name", help="A name to label this SSH key"),
    public_key: str = typer.Option(..., "--public-key", help="The public SSH key string (e.g. starts with ssh-rsa or ssh-ed25519)")
):
    """Register a new SSH key with a name and public key contents"""

    # Duplicate name check
    existing_keys = get_client().list_ssh_keys().get("data", [])
    if any(k.get("name") == name for k in existing_keys):
        typer.secho(f"❌ A key with the name '{name}' already exists.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Key format check
    if not public_key.startswith(("ssh-rsa", "ssh-ed25519")):
        typer.secho("❌ Public key must start with 'ssh-rsa' or 'ssh-ed25519'", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"🔐 Adding SSH key: {name}...")
    typer.echo()

    result = get_client().add_ssh_key(name, public_key)

    if isinstance(result, dict) and result.get("error"):
        typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
    else:
        typer.secho("✅ SSH key added successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

@app.command(name="delete-ssh-key", help="Delete one or more SSH keys from your Lambda Cloud account by ID or name")
def delete_ssh_key(
    key_ids: List[str] = typer.Option(None, "--key-id", help="SSH key ID to delete (use multiple times for multiple keys)"),
    key_names: List[str] = typer.Option(None, "--key-name", help="SSH key name to delete (use multiple times)"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before deleting")
):
    """Delete one or more SSH keys from your Lambda account by ID or name."""
    all_keys = get_client().list_ssh_keys().get("data", [])
    id_map = {k["name"]: k["id"] for k in all_keys}

    # 🔍 Resolve key names to IDs
    resolved_ids = set(key_ids or [])
    preview_names = []

    for name in key_names or []:
        if name not in id_map:
            typer.secho(f"❌ No SSH key found with name: {name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        resolved_ids.add(id_map[name])
        preview_names.append((name, id_map[name]))

    if not resolved_ids:
        typer.secho("❌ No keys specified for deletion.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo(f"🗑 Preparing to delete {len(resolved_ids)} SSH key(s)...")

    # 📋 Preview
    if not yes and preview_names:
        name_width = max(len(name) for name, _ in preview_names)
        typer.echo("\n🗒 Keys selected for deletion:\n")
        for name, key_id in preview_names:
            typer.echo(f"• {name:<{name_width}}  (ID: {key_id})")
        typer.echo()

    # ⚠️ Warn if deleting all
    if len(resolved_ids) == len(all_keys):
        typer.secho("⚠️ You are about to delete ALL SSH keys from your account!", fg=typer.colors.YELLOW)
        if not typer.confirm("Are you absolutely sure?", default=False):
            typer.echo("🚫 Deletion cancelled.")
            raise typer.Exit()

    # Confirm
    if not yes:
        confirm = typer.confirm(f"⚠️  Are you sure you want to delete {len(resolved_ids)} SSH key(s)?")
        if not confirm:
            typer.echo("🚫 Deletion cancelled.")
            raise typer.Exit()

    # 🚀 Perform deletion
    for key_id in resolved_ids:
        typer.echo(f"⏳ Deleting SSH key: {key_id}...")
        result = get_client().delete_ssh_key(key_id)

        if result.get("error"):
            typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = result["error"].get("suggestion")
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
        else:
            typer.secho(f"✅ Deleted SSH key {key_id}", fg=typer.colors.GREEN)

# ─────────────────────────────────────────────
# 🧱 File System Management Commands // create-file-system, delete-file-system, list-images
# ─────────────────────────────────────────────

@app.command(name="create-file-system", help="Create a new file system in your Lambda Cloud account")
def create_file_system(
    fs_name: str = typer.Option(..., "--fs-name", help="Name for the new file system"),
    region: str = typer.Option(..., "--region", help="Region for the file system (e.g. us-west-1)"),
):
    """
    Create a file system with a given name in the specified region.
    Mirrors the UX patterns of add-ssh-key: duplicate check, clear messages, and error handling.
    """
    client = get_client()

    # 🔂 Duplicate name check (scoped to region, like your pattern for keys)
    existing = client.list_file_systems().get("data", []) or []
    in_region = [fs for fs in existing if get_region_name(fs.get("region")) == region]
    if any(fs.get("name") == fs_name for fs in in_region):
        typer.secho(f"❌ A file system named '{fs_name}' already exists in region '{region}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # (Optional) warn if same name exists elsewhere to avoid confusion
    elsewhere = [fs for fs in existing if get_region_name(fs.get("region")) != region and fs.get("name") == fs_name]
    if elsewhere:
        typer.secho(f"⚠️ A file system named '{fs_name}' exists in another region. Proceeding in '{region}'.", fg=typer.colors.YELLOW)

    # 🚀 Create
    typer.echo(f"🧱 Creating file system '{fs_name}' in region '{region}'...")
    typer.echo()

    result = client.create_file_system(fs_name, region)

    # ❗ Surface structured errors (same shape you use for SSH key commands)
    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        message = err.get("message", "Unknown error")
        typer.secho(f"❌ Error: {message}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)

    # ✅ Success output (print nice details if present)
    data = result.get("data") if isinstance(result, dict) and "data" in result else result
    fs_id = (data or {}).get("id") if isinstance(data, dict) else None
    region_field = (data or {}).get("region") if isinstance(data, dict) else None
    region_name = get_region_name(region_field) if region_field else region

    typer.secho("✅ File system created successfully!", fg=typer.colors.GREEN)
    if fs_id:
        typer.echo(f"ID: {fs_id}")
    typer.echo(f"Name: {fs_name}")
    typer.echo(f"Region: {region_name}")

@app.command(name="delete-file-system", help="Delete one or more file systems from your Lambda Cloud account by ID or name")
def delete_file_system(
    fs_ids: List[str] = typer.Option(None, "--fs-id", help="File system ID to delete (use multiple times for multiple FS)"),
    fs_names: List[str] = typer.Option(None, "--fs-name", help="File system name to delete (use multiple times)"),
    region: Optional[str] = typer.Option(None, "--region", help="If deleting by name, optionally filter / resolve within this region (e.g. us-west-1)"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before deleting"),
):
    """
    Delete one or more file systems by ID or name.
    Mirrors UX patterns used in delete-ssh-key: multiple flags, preview, and confirmations.
    """
    client = get_client()
    all_fs = client.list_file_systems().get("data", []) or []

    # Optional region scoping (helps disambiguate duplicate names)
    scoped_fs = [f for f in all_fs if not region or get_region_name(f.get("region")) == region]

    if not scoped_fs:
        if region:
            typer.secho(f"ℹ️  No file systems found in region: {region}", fg=typer.colors.YELLOW)
        else:
            typer.secho("ℹ️  No file systems found.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    # Build name -> [records] map for resolution like SSH key delete
    name_map = {}
    for f in scoped_fs:
        nm = f.get("name")
        if nm:
            name_map.setdefault(nm, []).append(f)

    # 1) Start with any explicit IDs provided
    resolved_ids = set(fs_ids or [])
    preview_rows = []  # (display_name, fs_id, region_display)

    # 2) Resolve names → IDs (error if ambiguous within scope)
    for nm in fs_names or []:
        matches = name_map.get(nm, [])
        if len(matches) == 0:
            msg = f"❌ No file system found with name: {nm}"
            if region:
                msg += f" in region '{region}'"
            typer.secho(msg, fg=typer.colors.RED)
            raise typer.Exit(code=1)
        if len(matches) > 1:
            typer.secho(f"❌ Multiple file systems named '{nm}' found.", fg=typer.colors.RED)
            # Show collisions like your list-file-systems table
            id_width, name_width, region_width = 36, 20, 30
            header = f"{'ID':<{id_width}}  {'Name':<{name_width}}  {'Region':<{region_width}}"
            typer.echo(header)
            typer.echo("-" * (id_width + name_width + region_width + 4))
            for f in matches:
                rid = f.get("id", "")[:id_width]
                rfield = f.get("region", {}) or {}
                rname = get_region_name(rfield)
                rlabel = rfield.get("label") if isinstance(rfield, dict) else None
                rdisp = f"{rname} ({rlabel})" if rlabel else rname
                typer.echo(f"{rid:<{id_width}}  {nm:<{name_width}}  {rdisp:<{region_width}}")
            typer.echo("\nTip: Re-run with --fs-id <ID> or add --region to narrow the search.")
            raise typer.Exit(code=1)

        # Exactly one match → resolve
        target = matches[0]
        resolved_ids.add(target["id"])

    if not resolved_ids:
        typer.secho("❌ No file systems specified for deletion.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Prepare preview (names + regions) for all resolved IDs
    by_id = {f.get("id"): f for f in scoped_fs}
    for fid in sorted(resolved_ids):
        info = by_id.get(fid)
        if not info:
            # ID provided that isn't in current scope; fall back to global lookup before erroring
            info = next((f for f in all_fs if f.get("id") == fid), None)
            if not info:
                typer.secho(f"❌ No file system found with ID: {fid}", fg=typer.colors.RED)
                raise typer.Exit(code=1)

        nm = info.get("name", "unnamed")
        rfield = info.get("region", {}) or {}
        rname = get_region_name(rfield)
        rlabel = rfield.get("label") if isinstance(rfield, dict) else None
        rdisp = f"{rname} ({rlabel})" if rlabel else rname
        preview_rows.append((nm, fid, rdisp))

    typer.echo(f"🗑 Preparing to delete {len(resolved_ids)} file system(s)...")

    # 📋 Preview (match SSH key UX)
    if not yes and preview_rows:
        name_width = max(len(nm) for nm, _, _ in preview_rows)
        typer.echo("\n🗒 File systems selected for deletion:\n")
        for nm, fid, rdisp in preview_rows:
            typer.echo(f"• {nm:<{name_width}}  (ID: {fid}, Region: {rdisp})")
        typer.echo()

    # ⚠️ Warn if deleting all visible in scope
    if len(resolved_ids) == len(scoped_fs):
        scope_msg = f"in region '{region}'" if region else "from your account"
        typer.secho(f"⚠️ You are about to delete ALL file systems {scope_msg}!", fg=typer.colors.YELLOW)
        if not typer.confirm("Are you absolutely sure?", default=False):
            typer.echo("🚫 Deletion cancelled.")
            raise typer.Exit()

    # Confirm
    if not yes:
        if not typer.confirm(f"⚠️  Are you sure you want to delete {len(resolved_ids)} file system(s)?"):
            typer.echo("🚫 Deletion cancelled.")
            raise typer.Exit()

    # 🚀 Perform deletion (loop like SSH keys)
    for fid in resolved_ids:
        typer.echo(f"⏳ Deleting file system: {fid}...")
        result = client.delete_file_system(fid)

        if isinstance(result, dict) and result.get("error"):
            typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = result["error"].get("suggestion") if isinstance(result.get("error"), dict) else None
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
        else:
            typer.secho(f"✅ Deleted file system {fid}", fg=typer.colors.GREEN)

# ─────────────────────────────────────────────
# 🔥 Firewall Commands // 
# ─────────────────────────────────────────────

# ---------- List available firewall rules ----------
@app.command(name="get-firewall-rules", help="List available firewall rules in your Lambda Cloud account")
def get_firewall_rules():
    """Lists available firewall rule templates/catalog (as provided by the API)."""
    rules = get_client().get_firewall_rules().get("data", []) or []
    if not rules:
        typer.secho("ℹ️  No firewall rules found.", fg=typer.colors.YELLOW)
        return

    # Fixed widths for nice alignment
    proto_w, port_w, src_w, desc_w = 6, 13, 22, 40
    header = f"{'PROTO':<{proto_w}}  {'PORT(S)':<{port_w}}  {'SOURCE':<{src_w}}  {'DESCRIPTION':<{desc_w}}"
    typer.echo(header)
    typer.echo("-" * (proto_w + port_w + src_w + desc_w + 6))

    def fmt_ports(r):
        pr = r.get("port_range") or []
        if isinstance(pr, list) and len(pr) == 2 and pr[0] == pr[1]:
            return str(pr[0])
        elif isinstance(pr, list) and len(pr) == 2:
            return f"{pr[0]}-{pr[1]}"
        return "-"

    for rule in rules:
        proto = (rule.get("protocol") or "").lower()[:proto_w]
        ports = fmt_ports(rule)[:port_w]
        source = (rule.get("source_network") or "-")[:src_w]
        desc = (rule.get("description") or "-")[:desc_w]
        typer.echo(f"{proto:<{proto_w}}  {ports:<{port_w}}  {source:<{src_w}}  {desc:<{desc_w}}")

    typer.echo()
    typer.secho(f"🧱  Total: {len(rules)} rule(s).", fg=typer.colors.CYAN)


# ---------- List rulesets ----------
@app.command(name="get-firewall-rulesets", help="List all firewall rulesets configured in your Lambda Cloud account")
def get_firewall_rulesets(
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region (e.g. us-west-1)")
):
    """Lists firewall rulesets, optionally filtered by region."""
    rulesets = get_client().get_firewall_rulesets().get("data", []) or []
    if region:
        rulesets = [rs for rs in rulesets if get_region_name(rs.get("region")) == region]

    if not rulesets:
        msg = f"ℹ️  No firewall rulesets found{f' in region: {region}' if region else ''}."
        typer.secho(msg, fg=typer.colors.YELLOW)
        return

    rulesets.sort(key=lambda rs: rs.get("name", ""))

    id_w, name_w, region_w, count_w = 36, 24, 20, 8
    header = f"{'ID':<{id_w}}  {'Name':<{name_w}}  {'Region':<{region_w}}  {'#Rules':<{count_w}}"
    typer.echo(header)
    typer.echo("-" * (id_w + name_w + region_w + count_w + 6))

    for rs in rulesets:
        rs_id = rs.get("id", "")[:id_w]
        name = rs.get("name", "unnamed")[:name_w]
        rfield = rs.get("region", {}) or {}
        rname = get_region_name(rfield)
        rlabel = rfield.get("label") if isinstance(rfield, dict) else None
        rdisp = f"{rname} ({rlabel})" if rlabel else rname
        n_rules = len(rs.get("rules", []) or [])
        typer.echo(f"{rs_id:<{id_w}}  {name:<{name_w}}  {rdisp:<{region_w}}  {n_rules:<{count_w}}")

    typer.echo()
    typer.secho(f"🧱  Total: {len(rulesets)} ruleset(s).", fg=typer.colors.CYAN)


# ---------- Get ruleset by ID ----------
from typing import Optional, List
import json

@app.command(name="get-firewall-ruleset-by-id", help="Retrieve details of a specific firewall ruleset by ID or name")
def get_firewall_ruleset(
    ruleset_id: Optional[str] = typer.Option(None, "--ruleset-id", help="Ruleset ID"),
    ruleset_name: Optional[str] = typer.Option(None, "--ruleset-name", help="Ruleset name"),
    region: Optional[str] = typer.Option(None, "--region", help="When using --ruleset-name, optionally narrow to this region (e.g. us-west-1)"),
):
    """Show a ruleset by ID or name (with optional region scoping)."""
    if bool(ruleset_id) == bool(ruleset_name):
        typer.secho("❌ Provide exactly one of --ruleset-id or --ruleset-name.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    client = get_client()
    if ruleset_id:
        result = client.get_firewall_ruleset_by_id(ruleset_id)
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = err.get("suggestion")
            if suggestion: typer.echo(f"💡 Suggestion: {suggestion}")
            raise typer.Exit(code=1)
        typer.echo(json.dumps(result, indent=2))
        return

    # resolve by name
    rulesets = client.get_firewall_rulesets().get("data", []) or []
    scoped = [rs for rs in rulesets if not region or get_region_name(rs.get("region")) == region]
    matches = [rs for rs in scoped if rs.get("name") == ruleset_name]

    if len(matches) == 0:
        msg = f"❌ No ruleset found with name '{ruleset_name}'"
        if region: msg += f" in region '{region}'"
        typer.secho(msg + ".", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if len(matches) > 1:
        # show collisions to help the user pick an ID or add --region
        id_w, name_w, region_w = 36, 24, 20
        typer.secho(f"❌ Multiple rulesets named '{ruleset_name}' found:", fg=typer.colors.RED)
        header = f"{'ID':<{id_w}}  {'Name':<{name_w}}  {'Region':<{region_w}}"
        typer.echo(header); typer.echo("-" * (id_w + name_w + region_w + 4))
        for rs in matches:
            rid = rs.get("id","")[:id_w]
            rfield = rs.get("region",{}) or {}
            rname = get_region_name(rfield)
            rlabel = rfield.get("label") if isinstance(rfield, dict) else None
            rdisp = f"{rname} ({rlabel})" if rlabel else rname
            typer.echo(f"{rid:<{id_w}}  {ruleset_name:<{name_w}}  {rdisp:<{region_w}}")
        typer.echo("\nTip: Re-run with --ruleset-id <ID> or add --region to narrow.")
        raise typer.Exit(code=1)

    rid = matches[0]["id"]
    result = client.get_firewall_ruleset_by_id(rid)
    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion: typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)
    typer.echo(json.dumps(result, indent=2))

# ---------- Delete ruleset (with confirmation, name preview when possible) ----------
@app.command(name="delete-firewall-ruleset", help="Delete one or more firewall rulesets by ID or name")
def delete_firewall_ruleset(
    ruleset_ids: List[str] = typer.Option(None, "--ruleset-id", help="Ruleset ID to delete (use multiple times)"),
    ruleset_names: List[str] = typer.Option(None, "--ruleset-name", help="Ruleset name to delete (use multiple times)"),
    region: Optional[str] = typer.Option(None, "--region", help="When deleting by name, optionally narrow to this region"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation"),
):
    """Delete rulesets—multi-select, preview, region filter, and safety checks."""
    client = get_client()
    all_rs = client.get_firewall_rulesets().get("data", []) or []
    scoped = [rs for rs in all_rs if not region or get_region_name(rs.get("region")) == region]

    if not scoped:
        typer.secho(f"ℹ️  No firewall rulesets found{f' in region: {region}' if region else ''}.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    # resolve names → ids
    name_map: dict[str, list] = {}
    for rs in scoped:
        nm = rs.get("name")
        if nm: name_map.setdefault(nm, []).append(rs)

    resolved_ids = set(ruleset_ids or [])
    preview_rows = []

    for nm in ruleset_names or []:
        matches = name_map.get(nm, [])
        if len(matches) == 0:
            msg = f"❌ No ruleset found with name: {nm}"
            if region: msg += f" in region '{region}'"
            typer.secho(msg, fg=typer.colors.RED); raise typer.Exit(code=1)
        if len(matches) > 1:
            id_w, name_w, region_w = 36, 24, 20
            typer.secho(f"❌ Multiple rulesets named '{nm}' found.", fg=typer.colors.RED)
            header = f"{'ID':<{id_w}}  {'Name':<{name_w}}  {'Region':<{region_w}}"
            typer.echo(header); typer.echo("-" * (id_w + name_w + region_w + 4))
            for rs in matches:
                rid = rs.get("id","")[:id_w]
                rfield = rs.get("region",{}) or {}
                rname = get_region_name(rfield)
                rlabel = rfield.get("label") if isinstance(rfield, dict) else None
                rdisp = f"{rname} ({rlabel})" if rlabel else rname
                typer.echo(f"{rid:<{id_w}}  {nm:<{name_w}}  {rdisp:<{region_w}}")
            typer.echo("\nTip: Re-run with --ruleset-id <ID> or add --region to narrow.")
            raise typer.Exit(code=1)
        resolved_ids.add(matches[0]["id"])

    if not resolved_ids:
        typer.secho("❌ No rulesets specified for deletion.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    by_id = {rs.get("id"): rs for rs in scoped}
    for rid in sorted(resolved_ids):
        info = by_id.get(rid) or next((rs for rs in all_rs if rs.get("id")==rid), None)
        if not info:
            typer.secho(f"❌ No ruleset found with ID: {rid}", fg=typer.colors.RED); raise typer.Exit(code=1)
        nm = info.get("name","unnamed")
        rfield = info.get("region",{}) or {}
        rname = get_region_name(rfield)
        rlabel = rfield.get("label") if isinstance(rfield, dict) else None
        rdisp = f"{rname} ({rlabel})" if rlabel else rname
        preview_rows.append((nm, rid, rdisp))

    typer.echo(f"🗑 Preparing to delete {len(resolved_ids)} ruleset(s)...")
    if not yes and preview_rows:
        nm_w = max(len(nm) for nm,_,_ in preview_rows)
        typer.echo("\n🗒 Rulesets selected for deletion:\n")
        for nm, rid, rdisp in preview_rows:
            typer.echo(f"• {nm:<{nm_w}}  (ID: {rid}, Region: {rdisp})")
        typer.echo()

    if len(resolved_ids) == len(scoped):
        scope_msg = f"in region '{region}'" if region else "from your account"
        typer.secho(f"⚠️ You are about to delete ALL rulesets {scope_msg}!", fg=typer.colors.YELLOW)
        if not typer.confirm("Are you absolutely sure?", default=False):
            typer.echo("🚫 Deletion cancelled."); raise typer.Exit()

    if not yes:
        if not typer.confirm(f"⚠️  Delete {len(resolved_ids)} ruleset(s)?"):
            typer.echo("🚫 Deletion cancelled."); raise typer.Exit()

    for rid in resolved_ids:
        typer.echo(f"⏳ Deleting ruleset: {rid}...")
        result = client.delete_firewall_ruleset(rid)
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            typer.secho(f"❌ Error: {err.get('message','Unknown error')}", fg=typer.colors.RED)
            suggestion = err.get("suggestion")
            if suggestion: typer.echo(f"💡 Suggestion: {suggestion}")
        else:
            typer.secho(f"✅ Deleted ruleset {rid}", fg=typer.colors.GREEN)

# ---------- Create ruleset (keeps your default SSH rule, adds duplicate-name check per region) ----------
@app.command(name="create-firewall-ruleset", help="Create a new firewall ruleset in your Lambda Cloud account")
def create_firewall_ruleset(
    name: str = typer.Option(..., "--name", help="Ruleset name"),
    region: str = typer.Option(..., "--region", help="Region for the ruleset (e.g. us-west-1)")
):
    """Creates a ruleset with a default SSH rule; prevents duplicate names within the region."""
    client = get_client()

    existing = client.get_firewall_rulesets().get("data", []) or []
    in_region = [rs for rs in existing if get_region_name(rs.get("region")) == region]
    if any(rs.get("name") == name for rs in in_region):
        typer.secho(f"❌ A ruleset named '{name}' already exists in region '{region}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere",
        }
    ]

    typer.echo(f"🛡️  Creating firewall ruleset '{name}' in region '{region}'...")
    result = client.create_firewall_ruleset(name, region, rules)

    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)

    data = result.get("data") if isinstance(result, dict) and "data" in result else result
    rs_id = (data or {}).get("id") if isinstance(data, dict) else None

    typer.secho("✅ Ruleset created successfully!", fg=typer.colors.GREEN)
    if rs_id: typer.echo(f"ID: {rs_id}")
    typer.echo(f"Name: {name}")
    typer.echo(f"Region: {region}")


# ---------- Update ruleset (keeps your default SSH rule body) ----------
@app.command(name="update-firewall-ruleset", help="Update an existing firewall ruleset in your Lambda Cloud account")
def update_firewall_ruleset(
    ruleset_id: Optional[str] = typer.Option(None, "--ruleset-id", help="Target ruleset ID"),
    ruleset_name: Optional[str] = typer.Option(None, "--ruleset-name", help="Target ruleset name"),
    region: Optional[str] = typer.Option(None, "--region", help="When using --ruleset-name, optionally narrow to this region"),
    new_name: str = typer.Option(..., "--name", help="New name for the ruleset"),
):
    """
    Update a ruleset's name and rules. Accepts ID or name (+ optional region).
    """
    if bool(ruleset_id) == bool(ruleset_name):
        typer.secho("❌ Provide exactly one of --ruleset-id or --ruleset-name.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    client = get_client()

    # Resolve target ruleset id
    rid = ruleset_id
    if not rid:
        rulesets = client.get_firewall_rulesets().get("data", []) or []
        scoped = [rs for rs in rulesets if not region or get_region_name(rs.get("region")) == region]
        matches = [rs for rs in scoped if rs.get("name") == ruleset_name]
        if len(matches) == 0:
            msg = f"❌ No ruleset found with name '{ruleset_name}'"
            if region: msg += f" in region '{region}'"
            typer.secho(msg + ".", fg=typer.colors.RED); raise typer.Exit(code=1)
        if len(matches) > 1:
            id_w, name_w, region_w = 36, 24, 20
            typer.secho(f"❌ Multiple rulesets named '{ruleset_name}' found.", fg=typer.colors.RED)
            header = f"{'ID':<{id_w}}  {'Name':<{name_w}}  {'Region':<{region_w}}"
            typer.echo(header); typer.echo("-" * (id_w + name_w + region_w + 4))
            for rs in matches:
                rfield = rs.get("region",{}) or {}
                rname = get_region_name(rfield)
                rlabel = rfield.get("label") if isinstance(rfield, dict) else None
                rdisp = f"{rname} ({rlabel})" if rlabel else rname
                typer.echo(f"{rs.get('id',''):<{id_w}}  {ruleset_name:<{name_w}}  {rdisp:<{region_w}}")
            typer.echo("\nTip: Re-run with --ruleset-id <ID> or add --region to narrow.")
            raise typer.Exit(code=1)
        rid = matches[0]["id"]
        # infer region if not supplied
        region = get_region_name(matches[0].get("region"))

    # Prevent duplicate name in the same region
    target = client.get_firewall_ruleset_by_id(rid)
    body = target.get("data") if isinstance(target, dict) and "data" in target else target
    rfield = (body or {}).get("region", {}) or {}
    current_region = get_region_name(rfield) if rfield else region
    existing = client.get_firewall_rulesets().get("data", []) or []
    in_region = [x for x in existing if get_region_name(x.get("region")) == current_region]
    if any(x.get("name") == new_name and x.get("id") != rid for x in in_region):
        typer.secho(f"❌ Another ruleset named '{new_name}' already exists in region '{current_region}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Keep your default SSH rule
    rules = [{
        "protocol": "tcp",
        "port_range": [22, 22],
        "source_network": "0.0.0.0/0",
        "description": "Allow SSH from anywhere",
    }]

    typer.echo(f"🛡️  Updating ruleset '{rid}'...")
    result = client.update_firewall_ruleset(rid, new_name, rules)
    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        typer.secho(f"❌ Error: {err.get('message','Unknown error')}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion: typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)

    typer.secho("✅ Ruleset updated successfully!", fg=typer.colors.GREEN)
    typer.echo(f"ID: {rid}")
    typer.echo(f"Name: {new_name}")
    if current_region: typer.echo(f"Region: {current_region}")

# ---------- Patch global firewall (confirm first) ----------
@app.command(name="patch-global-firewall", help="Modify the global firewall ruleset for your Lambda Cloud account")
def patch_global_firewall(
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation")
):
    """Patches global ruleset with the default SSH rule."""
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere",
        }
    ]

    if not yes:
        typer.secho("⚠️  This will modify your GLOBAL firewall ruleset.", fg=typer.colors.YELLOW)
        if not typer.confirm("Proceed?", default=False):
            typer.echo("🚫 Update cancelled.")
            raise typer.Exit()

    typer.echo("🛡️  Patching global firewall ruleset...")
    result = get_client().patch_global_firewall_ruleset(rules)

    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)

    typer.secho("✅ Global ruleset patched.", fg=typer.colors.GREEN)


# ---------- Get global firewall ----------
@app.command(name="get-global-firewall", help="Retrieve the global firewall ruleset applied to your Lambda Cloud account")
def get_global_firewall():
    """Shows the global firewall ruleset (pretty-printed)."""
    result = get_client().get_global_firewall_ruleset()
    if isinstance(result, dict) and result.get("error"):
        err = result["error"]
        typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = err.get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        raise typer.Exit(code=1)

    typer.echo(json.dumps(result, indent=2))


# ─────────────────────────────────────────────
# 🛠 CLI Maintenance Commands // self_update
# ─────────────────────────────────────────────

@app.command(name="self-update", help="Check for updates and upgrade to the latest version of the Lambda Cloud CLI")
def self_update(yes: bool = typer.Option(False, "--yes", help="Skip confirmation")):
    """Upgrade lambda-cloud-cli to the latest version from PyPI"""
    import subprocess
    import sys

    try:
        from importlib.metadata import version as get_version  # Python 3.8+
    except ImportError:
        from importlib_metadata import version as get_version  # For Python <3.8

    package = "lambda-cloud-cli"

    try:
        current_version = get_version(package)
        typer.echo(f"📦 Currently installed: {package} v{current_version}")
    except Exception:
        typer.secho("⚠️ Could not determine current version.", fg=typer.colors.YELLOW)
        current_version = None

    if not yes:
        confirm = typer.confirm("⚠️ This will attempt to upgrade the CLI via pip. Continue?")
        if not confirm:
            typer.echo("🚫 Update cancelled.")
            raise typer.Exit()

    typer.echo("📥 Updating Lambda CLI...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            try:
                new_version = get_version(package)
                if new_version != current_version:
                    typer.secho(f"✅ Update complete! Now using: {package} v{new_version}", fg=typer.colors.GREEN)
                else:
                    typer.secho("ℹ️  CLI was already up to date.", fg=typer.colors.CYAN)
            except Exception:
                typer.secho("✅ Update finished, but could not verify new version.", fg=typer.colors.GREEN)
        else:
            typer.secho("❌ Update failed.", fg=typer.colors.RED)
            typer.echo(result.stderr)

    except Exception as e:
        typer.secho("❌ An error occurred during update.", fg=typer.colors.RED)
        typer.echo(str(e))

# ─────────────────────────────────────────────
# 📚 CLI Usage & Reference Commands // examples, docs
# ─────────────────────────────────────────────

@app.command(name="examples", help="Show common usage examples")
def examples():
    typer.echo(r"""
Lambda CLI Usage Examples

🔐 Authenticate:
  # Login and store your API key
  lambda-cli login

  # Check who you're logged in as
  lambda-cli whoami

  # Logout and delete your stored API key
  lambda-cli logout

🚀 Launch Instances:
  # Launch with manual name
  lambda-cli launch-instance \
    --region-name us-west-1 \
    --instance-type gpu_1x_a10 \
    --ssh-key-name my-key \
    --name my-instance \
    --file-system-name myfs \
    --mount-point /mnt/myfs

  # Launch with auto-generated name
  lambda-cli launch-instance \
    --region-name us-west-1 \
    --instance-type gpu_1x_a10 \
    --ssh-key-name my-key \
    --auto-name \

  # Launch using interactive wizard
  lambda-cli interactive-launch

📥 Clone Instances:
  # Clone by instance ID
  lambda-cli clone-instance \
    --instance-id abc123 \
    --new-name clone-instance \
    --include-filesystem \

  # Clone by instance name
  lambda-cli clone-instance \
    --instance-name base-instance \
    --new-name clone-instance \
    --include-filesystem

  # Use a different SSH key while cloning
  lambda-cli clone-instance \
    --instance-id abc123 \
    --new-name clone-instance \
    --ssh-key-name new-key \

  # Clone using interactive wizard
  lambda-cli interactive-clone

📋 List Instances:
  # Filter by region
  lambda-cli list-instances --region us-west-1

⚙️  List Available Instance Types:
  lambda-cli list-instance-types

🔍 View Instance Details:
  # Instance by ID
  lambda-cli get-instance \
    --instance-id abc123456789

  # Instance by name
  lambda-cli get-instance \
    --instance-name my-instance
  
❌ Terminate Instances:
  # Terminate by instance ID
  lambda-cli terminate-instance \
    --instance-id abc123

  # Terminate by instance name
  lambda-cli terminate-instance \
    --instance-name my-instance

  # Terminate multiple instances by name and/or ID
  lambda-cli terminate-instance \
    --instance-name a --instance-id b \
    
📝 Rename Instances:
  # Rename by instance ID
  lambda-cli update-instance-name \
    --instance-id abc123 \
    --new-name new-name

  # Rename by instance name
  lambda-cli update-instance-name \
    --instance-name old-name \
    --new-name new-name

📓 Jupyter Access:
  # Open Jupyter URL by instance ID
  lambda-cli open-jupyter \
    --instance-id abc123

  # Open Jupyter URL by instance name
  lambda-cli open-jupyter \
    --instance-name my-instance

🔐 SSH Key Management:
  # List all registered SSH keys
  lambda-cli list-ssh-keys

  # Add an SSH key
  lambda-cli add-ssh-key \
    --name my-key \
    --public-key "ssh-rsa AAAAB3Nza..."

  # Delete SSH key by ID
  lambda-cli delete-ssh-key \
    --key-id abc123 \

  # Delete SSH key by name
  lambda-cli delete-ssh-key \
    --key-name my-key

🧱 File System Management:
  # List all file systems
  lambda-cli list-file-systems

  # Create a new file system
  lambda-cli create-file-system \
    --name myfs \
    --region us-west-1

  # Delete a file system by ID
  lambda-cli delete-file-system \
    --fs-id 1234abcd

  # Delete a file system by name
  lambda-cli delete-file-system \
    --fs-name myfs

  # Delete a filesystem by by name scoped to region
  lambda-cli delete-file-system \
    --fs-name myfs --region us-west-1

🧯 Firewall Rules:
  # View available rules
  lambda-cli get-firewall-rules

  # List all rulesets
  lambda-cli get-firewall-rulesets

  # Get details of a ruleset
  lambda-cli get-firewall-ruleset-by-id \
    --ruleset-id abc123

  # Create a basic SSH ruleset
  lambda-cli create-firewall-ruleset \
    --name allow-ssh \
    --region us-west-1

  # Update an existing ruleset
  lambda-cli update-firewall-ruleset \
    --ruleset-id abc123 \
    --name updated-name

  # Delete a ruleset
  lambda-cli delete-firewall-ruleset \
    --ruleset-id abc123

  # Patch the global ruleset
  lambda-cli patch-global-firewall

  # View global rules
  lambda-cli get-global-firewall
  
💰 Estimate Billing:
  # Total cost of active instances
  lambda-cli billing

  # Filter by region
  lambda-cli billing --region us-west-1

  # Filter by instance name substring
  lambda-cli billing --name-contains train

📷 Images:
  # View available images
  lambda-cli list-images

🔄 Maintenance & Updates:
  # Check and apply CLI update
  lambda-cli self-update

  # Enable shell autocompletion
  lambda-cli --install-completion

  # Get CLI version
  pip show lambda-cloud-cli
""")

@app.command(name="docs", help="Show full CLI documentation and usage guidance")
def docs():
    return examples()

# ─────────────────────────────────────────────
# Run App
# ─────────────────────────────────────────────
app()



