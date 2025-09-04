@app.command(name="create-file-system",help="Create a new file system in your Lambda Cloud account")
def create_file_system(name: str, region: str):
    result = get_client().create_file_system(name, region)
    typer.echo(result)

@app.command(name="delete-file-system",help="Delete a file system from your Lambda Cloud account")
def delete_file_system(fs_id: str):
    result = get_client().delete_file_system(fs_id)
    typer.echo(result)

@app.command(name="list-images",help="Show available images in your Lambda Cloud account")
def list_images():
    images = get_client().list_images().get("data", [])
    for img in images:
        region = img.get("region", {}).get("name", "unknown")
        typer.echo(f"{img['id']}: {img['name']} ({region})")
