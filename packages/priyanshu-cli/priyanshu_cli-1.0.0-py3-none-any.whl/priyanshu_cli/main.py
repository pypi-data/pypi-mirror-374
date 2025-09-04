import click
import requests

GITHUB_API = "https://api.github.com/users"

@click.command()
@click.argument("username")
def get_repos(username):
    """
    Simple CLI tool to fetch all public repositories of a GitHub user.
    Usage: priyanshu-cli <github-username>
    """
    url = f"{GITHUB_API}/{username}/repos"
    response = requests.get(url)

    if response.status_code == 200:
        repos = response.json()
        if repos:
            click.echo(f"\n🔹 Public repositories of '{username}':\n")
            for idx, repo in enumerate(repos, start=1):
                click.echo(f"{idx}. {repo['name']}")
        else:
            click.echo(f"\n⚠️ User '{username}' has no public repositories.")
    elif response.status_code == 404:
        click.echo(f"\n❌ User '{username}' not found!")
    else:
        click.echo(f"\n⚠️ Error: {response.status_code} - Something went wrong.")

if __name__ == "__main__":
    get_repos()
