import click
from .client import Client
import os
import json


@click.group()
@click.option(
    "--api-key",
    envvar="SIIN_API_KEY",
    default=os.getenv("SIIN_API_KEY"),
    help="Your API key.",
)
@click.pass_context
def cli(ctx, api_key):
    """Siin Studio CLI"""
    ctx.ensure_object(dict)
    if not api_key:
        raise click.UsageError(
            "API key is required. Use --api-key or set SIIN_API_KEY env var."
        )
    ctx.obj["client"] = Client(api_key)


@cli.command()
@click.pass_context
def list_projects(ctx):
    """List all projects metadata."""
    client = ctx.obj["client"]
    result = client.get_all_projects_metadata()
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("project_id")
@click.pass_context
def project_metadata(ctx, project_id):
    """Get metadata for a specific project."""
    client = ctx.obj["client"]
    result = client.get_one_project_metadata(project_id)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("project_id")
@click.pass_context
def project_progress(ctx, project_id):
    """Get progress for a specific project."""
    client = ctx.obj["client"]
    result = client.get_project_progress(project_id)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("media_id")
@click.option("--review-status", type=str, default=None, help="Review status filter.")
@click.option("--done", type=bool, default=None, help="Done status filter.")
@click.pass_context
def filter_chunks_cmd(ctx, media_id, review_status, done):
    """Filter chunks for a media ID."""
    client = ctx.obj["client"]
    result = client.filter_chunks(media_id, review_status, done)
    click.echo(result)


@cli.command()
@click.argument("media_id")
@click.pass_context
def download_dataset_cmd(ctx, media_id):
    """Download dataset for a media ID."""
    client = ctx.obj["client"]
    result = client.download_dataset(media_id)
    click.echo(result)


@cli.command()
@click.option("--start", type=int, default=0, help="Start index for notifications.")
@click.option(
    "--limit", type=int, default=100, help="Number of notifications to fetch."
)
@click.option(
    "--only-unread/--all", default=True, help="Show only unread notifications."
)
@click.pass_context
def show_all_notifications_cmd(ctx, start, limit, only_unread):
    """Show all notifications."""
    client = ctx.obj["client"]
    result = client.show_all_notifications(start, limit, only_unread)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("notification_id", required=False)
@click.pass_context
def mark_notification_as_read_cmd(ctx, notification_id):
    """Mark a notification as read."""
    client = ctx.obj["client"]
    result = client.mark_notification_as_read(notification_id)
    click.echo(result)


@cli.command()
@click.argument("project_id")
@click.pass_context
def retrieve_project_permissions_cmd(ctx, project_id):
    """Retrieve project permissions."""
    client = ctx.obj["client"]
    result = client.retrieve_project_permissions(project_id)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("project_id")
@click.pass_context
def get_project_team_cmd(ctx, project_id):
    """Get project team members."""
    client = ctx.obj["client"]
    result = client.get_project_team(project_id)
    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    cli(obj={})
