# Upload workspace export archives to TopoMojo
from pytopomojo import Topomojo

# Update the URL and API key to point to your TopoMojo instance
client = Topomojo("https://example.com/topomojo", "<put your API Key here>")

# Provide the path to a previously exported workspace zip file
client.upload_workspace("/path/to/workspace.zip")

# Or upload multiple archives
client.upload_workspaces(["/path/one.zip", "/path/two.zip"])
