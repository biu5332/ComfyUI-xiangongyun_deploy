# ComfyUI-Xiangong Deploy
A custom node extension for ComfyUI that allows you to deploy and manage GPU instances on Xiangong Cloud directly from your ComfyUI workflow.

## Features
- One-click Deployment : Deploy GPU instances on Xiangong Cloud with customizable configurations
- Instance Management : Query instance details and list all your instances
- Auto-retry Mechanism : Automatically retry deployment when resources are temporarily unavailable
- Detailed Logging : Comprehensive logging of all operations for troubleshooting
- User-friendly Error Messages : Clear error messages for common issues

## Installation
### Prerequisites
- ComfyUI installed
- Python 3.8+
- Xiangong Cloud account with API key

### Steps
1. Clone this repository to your ComfyUI custom_nodes directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/biu5332/ComfyUI-xiangongyun_deploy.git
 ```
```

2. Install required dependencies:
```bash
pip install requests
 ```

3. Restart ComfyUI

## Usage
### Deploy a Xiangong Cloud Instance
1. Add the "部署仙宫云实例" (Deploy Xiangong Cloud Instance) node to your workflow
2. Configure the required parameters:
   
   - api_key : Your Xiangong Cloud API key
   - gpu_model : GPU model (RTX 4090, etc.)
   - gpu_count : Number of GPUs
   - data_center_id : Data center ID
   - image : Image ID
   - image_type : Image type (public/community/private)
   - name : Instance name
   - max_attempts : Maximum retry attempts
   - retry_interval : Seconds between retries
3. Optional parameters:
   
   - storage : Enable cloud storage
   - storage_mount_path : Storage mount path
   - ssh_key : SSH key
   - system_disk_expand : Enable system disk expansion
   - system_disk_expand_size : System disk expansion size
   - debug_mode : Enable debug mode

### Query Instance Details
1. Add the "查询实例详情" (Query Instance Details) node to your workflow
2. Connect the instance_id output from the deployment node or manually enter an instance ID
3. Enter your API key
### List All Instances
1. Add the "仙宫云key" (Xiangong Cloud Key) node to your workflow
2. Enter your API key to list all instances associated with your account
## Disclaimer
IMPORTANT: Use this code at your own risk

This code is provided for educational and learning purposes only. Users should understand that:

1. This plugin calls the Xiangong Cloud API to deploy instances, which may incur charges. Please ensure you understand the relevant pricing standards before use.
2. The author is not responsible for any direct or indirect losses caused by using this code, including but not limited to:
   - Account charges
   - Data loss
   - Service interruption
   - Security issues
3. Before using this code, please ensure you have read and agreed to Xiangong Cloud's terms of service and API usage policies.
4. This code does not provide any form of warranty, including but not limited to applicability, reliability, or accuracy.
By using this code, you accept the above disclaimer. If you do not agree, please do not use this code.

## License
1. This code is limited to non-commercial use only. Without explicit written permission from the author, it is prohibited to use this code for any commercial purpose.
2. The author is not responsible for the consequences of using this code. Users shall bear all risks associated with using this code.
3. When distributing or modifying this code, this disclaimer and license terms must be retained.
