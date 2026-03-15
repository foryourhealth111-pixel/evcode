from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_ROOT = "https://api.github.com"


def read_token() -> str:
    token = sys.stdin.readline().strip()
    if not token:
        raise RuntimeError("missing GitHub token on stdin")
    return token


def request_json(method: str, url: str, token: str, payload: dict | None = None, content_type: str = "application/json") -> tuple[int, dict]:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": content_type,
            "User-Agent": "evcode-release-publisher",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        parsed = json.loads(body) if body else {}
        return error.code, parsed


def upload_asset(upload_url: str, asset: Path, token: str) -> dict:
    mime_type = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
    target_url = f"{upload_url}?{urllib.parse.urlencode({'name': asset.name})}"
    request = urllib.request.Request(
        target_url,
        data=asset.read_bytes(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": mime_type,
            "User-Agent": "evcode-release-publisher",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def ensure_release(owner: str, repo: str, tag: str, token: str) -> dict:
    status, body = request_json("GET", f"{API_ROOT}/repos/{owner}/{repo}/releases/tags/{tag}", token)
    if status == 200:
        return body
    if status != 404:
        raise RuntimeError(f"failed to query release for tag {tag}: {body}")
    status, body = request_json(
        "POST",
        f"{API_ROOT}/repos/{owner}/{repo}/releases",
        token,
        payload={
            "tag_name": tag,
            "name": f"EvCode {tag}",
            "draft": False,
            "prerelease": False,
            "body": "Standard and benchmark distribution packages for EvCode.",
        },
    )
    if status not in (200, 201):
        raise RuntimeError(f"failed to create release for tag {tag}: {body}")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description="Create/update a GitHub release and upload EvCode artifacts.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--asset", action="append", required=True, help="Asset file to upload")
    args = parser.parse_args()

    token = read_token()
    release = ensure_release(args.owner, args.repo, args.tag, token)
    upload_url = release["upload_url"].split("{", 1)[0]

    uploaded = []
    existing_assets = {asset["name"] for asset in release.get("assets", [])}
    for asset_path in args.asset:
        asset = Path(asset_path).resolve()
        if not asset.exists():
            raise RuntimeError(f"asset does not exist: {asset}")
        if asset.name in existing_assets:
            uploaded.append({"name": asset.name, "status": "skipped-existing"})
            continue
        result = upload_asset(upload_url, asset, token)
        uploaded.append({"name": asset.name, "status": "uploaded", "url": result.get("browser_download_url")})

    print(
        json.dumps(
            {
                "release_url": release["html_url"],
                "tag": args.tag,
                "uploaded_assets": uploaded,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
