# This script exports all workspaces from TopoMojo and downloads each workspace as an individual zip file.
# It accepts an optional command-line argument to specify the output directory for the downloaded files.
# Arguments:
#   --output-directory (-o): Directory to save downloaded workspaces. Defaults to the current directory.

from pytopomojo import Topomojo, TopomojoException
import os, argparse

parser = argparse.ArgumentParser(description="Download TopoMojo workspaces")
parser.add_argument(
    "--output-directory", "-o", default=".", help="Directory to save downloaded workspaces"
)
args = parser.parse_args()

output_dir = args.output_directory
os.makedirs(output_dir, exist_ok=True)

topomojo = Topomojo("https://example.com/topomojo", "<put your API Key here>")

workspaces = topomojo.get_workspaces()

workspace_guids = [w["id"] for w in workspaces]
workspace_slugs = [w["slug"] for w in workspaces]

for workspace in workspaces:
    output_path = os.path.join(output_dir, f"{workspace['slug']}.zip")
    topomojo.download_workspaces([workspace["id"]], output_path)
