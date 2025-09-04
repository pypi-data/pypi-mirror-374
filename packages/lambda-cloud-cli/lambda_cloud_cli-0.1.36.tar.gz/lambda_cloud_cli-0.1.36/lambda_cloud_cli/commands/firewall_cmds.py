# firewall_cmds.py
from typing import Optional, List
import json
import typer

def register_firewall_commands(app: typer.Typer, get_client, get_region_name):
    # ---------- List available firewall rules ----------
    @app.command(name="get-firewall-rules", help="List available firewall rules in your Lambda Cloud account")
    def get_firewall_rules():
        rules = get_client().get_firewall_rules().get("data", []) or []
        if not rules:
            typer.secho("ℹ️  No firewall rules found.", fg=typer.colors.YELLOW)
            return

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
    @app.command(name="get-firewall-ruleset-by-id", help="Retrieve details of a specific firewall ruleset by ID")
    def get_firewall_ruleset_by_id(
        ruleset_id: str = typer.Option(..., "--ruleset-id", help="Firewall ruleset ID")
    ):
        result = get_client().get_firewall_ruleset_by_id(ruleset_id)
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = err.get("suggestion")
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
            raise typer.Exit(code=1)
        typer.echo(json.dumps(result, indent=2))

    # ---------- Delete ruleset ----------
    @app.command(name="delete-firewall-ruleset", help="Delete a firewall ruleset by its ID")
    def delete_firewall_ruleset(
        ruleset_id: str = typer.Option(..., "--ruleset-id", help="Firewall ruleset ID to delete"),
        yes: bool = typer.Option(False, "--yes", help="Skip confirmation prompt"),
    ):
        preview = None
        try:
            fetched = get_client().get_firewall_ruleset_by_id(ruleset_id)
            if isinstance(fetched, dict):
                preview = fetched.get("data") or fetched
        except Exception:
            pass

        name = (preview or {}).get("name")
        rfield = (preview or {}).get("region", {}) or {}
        rname = get_region_name(rfield) if rfield else None
        rlabel = rfield.get("label") if isinstance(rfield, dict) else None
        rdisp = f"{rname} ({rlabel})" if rname and rlabel else (rname or "unknown")

        if not yes:
            prompt = f"⚠️  Delete firewall ruleset {ruleset_id}"
            if name:
                prompt += f" (Name: {name}"
                prompt += f", Region: {rdisp}" if rname else ""
                prompt += ")?"
            else:
                prompt += "?"
            if not typer.confirm(prompt):
                typer.echo("🚫 Deletion cancelled.")
                raise typer.Exit()

        typer.echo(f"⏳ Deleting ruleset: {ruleset_id}...")
        result = get_client().delete_firewall_ruleset(ruleset_id)
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = err.get("suggestion")
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
            raise typer.Exit(code=1)
        typer.secho("✅ Ruleset deleted.", fg=typer.colors.GREEN)

    # ---------- Create ruleset ----------
    @app.command(name="create-firewall-ruleset", help="Create a new firewall ruleset in your Lambda Cloud account")
    def create_firewall_ruleset(
        name: str = typer.Option(..., "--name", help="Ruleset name"),
        region: str = typer.Option(..., "--region", help="Region for the ruleset (e.g. us-west-1)")
    ):
        client = get_client()
        existing = client.get_firewall_rulesets().get("data", []) or []
        in_region = [rs for rs in existing if get_region_name(rs.get("region")) == region]
        if any(rs.get("name") == name for rs in in_region):
            typer.secho(f"❌ A ruleset named '{name}' already exists in region '{region}'.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        rules = [{
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere",
        }]

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

    # ---------- Update ruleset ----------
    @app.command(name="update-firewall-ruleset", help="Update an existing firewall ruleset in your Lambda Cloud account")
    def update_firewall_ruleset(
        ruleset_id: str = typer.Option(..., "--ruleset-id", help="Ruleset ID to update"),
        name: str = typer.Option(..., "--name", help="New name for the ruleset"),
    ):
        client = get_client()
        rs = client.get_firewall_ruleset_by_id(ruleset_id)
        region = None
        try:
            body = rs.get("data") if isinstance(rs, dict) and "data" in rs else rs
            rfield = (body or {}).get("region", {}) or {}
            region = get_region_name(rfield) if rfield else None
        except Exception:
            pass
        if region:
            existing = client.get_firewall_rulesets().get("data", []) or []
            in_region = [x for x in existing if get_region_name(x.get("region")) == region]
            if any(x.get("name") == name and x.get("id") != ruleset_id for x in in_region):
                typer.secho(f"❌ Another ruleset named '{name}' already exists in region '{region}'.", fg=typer.colors.RED)
                raise typer.Exit(code=1)

        rules = [{
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere",
        }]

        typer.echo(f"🛡️  Updating ruleset '{ruleset_id}'...")
        result = client.update_firewall_ruleset(ruleset_id, name, rules)
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = err.get("suggestion")
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
            raise typer.Exit(code=1)

        typer.secho("✅ Ruleset updated successfully!", fg=typer.colors.GREEN)
        typer.echo(f"ID: {ruleset_id}")
        typer.echo(f"Name: {name}")
        if region: typer.echo(f"Region: {region}")

    # ---------- Patch global ----------
    @app.command(name="patch-global-firewall", help="Modify the global firewall ruleset for your Lambda Cloud account")
    def patch_global_firewall(
        yes: bool = typer.Option(False, "--yes", help="Skip confirmation")
    ):
        rules = [{
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere",
        }]

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

    # ---------- Get global ----------
    @app.command(name="get-global-firewall", help="Retrieve the global firewall ruleset applied to your Lambda Cloud account")
    def get_global_firewall():
        result = get_client().get_global_firewall_ruleset()
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            typer.secho(f"❌ Error: {err.get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = err.get("suggestion")
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
            raise typer.Exit(code=1)
        typer.echo(json.dumps(result, indent=2))
