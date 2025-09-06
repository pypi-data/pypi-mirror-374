# This script will: 
# 1. Create a new workspace
# 2. Search for published templates matching a keyword
# 3. Add the template to the workspace, unlink and initialize it
# 4. Deploy the added VM

from pytopomojo import Topomojo

topomojo = Topomojo("https://example.com/topomojo", "<put your API Key here>")

# Create a new workspace
new_workspace = topomojo.create_workspace({"name": "Example Workspace"})

# Search for the published kali template and add it to the workspace
kali_template = topomojo.get_templates(Term="kali", Filter="published")[0]
new_kali_template = topomojo.new_workspace_template({"workspaceId": new_workspace['id'], "templateId": kali_template['id']})

# unlink and initialize template
topomojo.unlink_template({"workspaceId": new_workspace['id'], "templateId": new_kali_template['id']})
topomojo.initialize_template(new_kali_template['id'])

# deploy vm
topomojo.deploy_vm_from_template(new_kali_template['id'])