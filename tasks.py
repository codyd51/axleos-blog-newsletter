import re

from invoke import task
from invoke.context import Context


@task
def run(ctx: Context) -> None:
    flags = ["--timeout", "0", "--chdir", "./newsletter/"]
    ctx.run(f"gunicorn {' '.join(flags)} app:app", pty=True)


@task
def deploy(ctx: Context) -> None:
    # Build the Docker image and deploy it to Cloud Run.
    gcp_project = "axleos-blog-newsletter"
    print("Deploying to App Engine...")
    git_branch = ctx.run("git rev-parse --abbrev-ref HEAD", hide="stdout").stdout.strip().lower()[:53]
    gcloud_compat_git_branch = re.sub(r"[^a-z0-9-]", "", git_branch)
    git_short_hash = ctx.run("git rev-parse --short HEAD", hide="stdout").stdout.strip().lower()
    version = f"{git_short_hash}-{gcloud_compat_git_branch}"[:35]
    ctx.run(f"gcloud app deploy app.yaml --project {gcp_project} --version {version}")


if __name__ == '__main__':
    # PT: This entry point is primarily useful for using Pycharm breakpoints, as they're cumbersome when running
    # gunicorn via an invoke task.
    from app import app
    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as httpd:
        print('Serving...')
        # Serve until process is killed
        httpd.serve_forever()
