import requests
import time
import json
import os
import logging
import traceback
from datetime import datetime

# 设置日志
def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"xiangong_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return log_file

# 记录日志并打印
def log_and_print(message):
    print(message)
    logging.info(message)

class XiangongDeployInstance:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "gpu_model": (["NVIDIA GeForce RTX 4090", "NVIDIA GeForce RTX 4090 D"], {"default": "NVIDIA GeForce RTX 4090"}),
                "gpu_count": ("INT", {"default": 1, "min": 1, "max": 8}),
                "data_center_id": ("INT", {"default": 1, "min": 1}),
                "image": ("STRING", {"default": "", "multiline": False}),
                "image_type": (["public", "community", "private"], {"default": "public"}),
                "name": ("STRING", {"default": "ComfyUI Instance", "multiline": False}),
                "max_attempts": ("INT", {"default": 60, "min": 1, "max": 1000}),
                "retry_interval": ("INT", {"default": 1, "min": 1, "max": 60}),
            },
            "optional": {
                "storage": ("BOOLEAN", {"default": False}),
                "storage_mount_path": ("STRING", {"default": "/root/cloud", "multiline": False}),
                "ssh_key": ("STRING", {"default": "", "multiline": False}),
                "system_disk_expand": ("BOOLEAN", {"default": False}),
                "system_disk_expand_size": ("INT", {"default": 0, "min": 0}),
                "debug_mode": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("result", "instance_id")
    FUNCTION = "deploy_instance"
    CATEGORY = "XiangongCloud"

    def deploy_instance(self, api_key, gpu_model, gpu_count, data_center_id, image, image_type, name,
                       max_attempts, retry_interval, storage=False, storage_mount_path="", 
                       ssh_key="", system_disk_expand=False, system_disk_expand_size=0, debug_mode=False):
        
        if not api_key:
            return ("错误: API密钥不能为空", "")
        
        if not image:
            return ("错误: 镜像ID不能为空", "")
        
        # 设置日志
        log_file = setup_logging()
        
        # 构建请求参数
        params = {
            "gpu_model": gpu_model,
            "gpu_count": gpu_count,
            "data_center_id": data_center_id,
            "image": image,
            "image_type": image_type,
            "storage": storage,
            "name": name
        }
        
        # 添加可选参数
        if storage and storage_mount_path:
            params["storage_mount_path"] = storage_mount_path
        if ssh_key:
            params["ssh_key"] = ssh_key
        if system_disk_expand:
            params["system_disk_expand"] = system_disk_expand
        if system_disk_expand_size > 0:
            params["system_disk_expand_size"] = system_disk_expand_size
        
        # API端点和请求头
        url = "https://api.xiangongyun.com/open/instance/deploy"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        attempt = 0
        success = False
        instance_id = None
        
        log_and_print(f"开始尝试创建仙宫云实例...\n配置: {json.dumps(params, indent=2, ensure_ascii=False)}")
        
        while attempt < max_attempts and not success:
            attempt += 1
            
            try:
                log_and_print(f"\n尝试 #{attempt}/{max_attempts}...")
                
                if debug_mode:
                    log_and_print("\n===== 请求详情 =====")
                    log_and_print(f"URL: {url}")
                    log_and_print(f"请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
                    log_and_print(f"请求体: {json.dumps(params, indent=2, ensure_ascii=False)}")
                
                # 发送请求
                response = requests.post(url, json=params, headers=headers)
                response_json = response.json()
                
                if debug_mode:
                    log_and_print("\n===== 响应详情 =====")
                    log_and_print(f"状态码: {response.status_code}")
                    log_and_print(f"响应头: {dict(response.headers)}")
                    log_and_print(f"响应体: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                
                # 检查是否成功 - 适应API实际返回格式
                if response.status_code == 200 and (response_json.get("code") == 0 or response_json.get("code") == 200) and "data" in response_json and "id" in response_json.get("data", {}):
                    instance_id = response_json.get("data", {}).get("id", "")
                    if instance_id:  # 确保实例ID不为空
                        success = True
                        log_and_print("\n===== 创建成功！=====")
                        log_and_print(f"实例ID: {instance_id}")
                        log_and_print(f"响应: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                        break
                    else:
                        log_and_print("警告：API返回成功状态，但没有提供有效的实例ID")
                else:
                    # 获取错误消息
                    error_message = response_json.get("message", "未知错误")
                    
                    # 检查错误类型并给出友好提示
                    user_friendly_error = error_message
                    if "资源不足" in error_message or "no gpu available" in error_message.lower():
                        user_friendly_error = "GPU数量不足，请稍后再试"
                    elif "余额不足" in error_message:
                        user_friendly_error = "账户余额不足，请充值后再试"
                    
                    log_and_print(f"创建失败: {user_friendly_error}")
                    log_and_print(f"原始错误: {error_message}")
                    log_and_print(f"响应码: {response.status_code}")
                    log_and_print(f"响应内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            
            except Exception as e:
                error_details = traceback.format_exc()
                log_and_print(f"请求过程中发生错误: {str(e)}")
                log_and_print(f"异常详情: {error_details}")
            
            # 如果未成功且未达到最大尝试次数，等待后继续
            if not success and attempt < max_attempts:
                log_and_print(f"等待{retry_interval}秒后重试...")
                time.sleep(retry_interval)
        
        # 输出最终结果
        if success:
            result = f"\n=== 最终结果 ===\n"
            result += f"成功创建实例！\n"
            result += f"实例ID: {instance_id}\n"
            result += f"尝试次数: {attempt}/{max_attempts}\n"
            result += f"日志文件: {log_file}"
            log_and_print(result)
            return (result, instance_id)
        else:
            result = f"\n=== 最终结果 ===\n"
            result += f"创建失败，已达到最大尝试次数 {max_attempts}。\n"
            result += f"日志文件: {log_file}"
            log_and_print(result)
            return (result, "")

class XiangongInstanceDetails:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "instance_id": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("instance_details",)
    FUNCTION = "get_instance_details"
    CATEGORY = "XiangongCloud"

    def get_instance_details(self, api_key, instance_id):
        if not api_key:
            return ("错误: API密钥不能为空",)
        
        if not instance_id:
            return ("错误: 实例ID不能为空",)
        
        url = f"https://api.xiangongyun.com/open/instance/detail?instance_id={instance_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            
            if response.status_code == 200 and (response_json.get("code") == 0 or response_json.get("code") == 200):
                instance = response_json.get("data", {})
                if not instance:
                    return (f"未找到ID为 {instance_id} 的实例详情。",)
                
                result = "实例详情:\n\n"
                result += f"ID: {instance.get('id')}\n"
                result += f"名称: {instance.get('name')}\n"
                result += f"状态: {instance.get('status')}\n"
                result += f"GPU型号: {instance.get('gpu_model')}\n"
                result += f"GPU数量: {instance.get('gpu_count')}\n"
                result += f"IP地址: {instance.get('ip')}\n"
                result += f"SSH端口: {instance.get('ssh_port')}\n"
                result += f"创建时间: {instance.get('created_at')}\n"
                
                # 添加其他可能的详细信息
                if instance.get('storage'):
                    result += f"云存储: 已挂载\n"
                    if instance.get('storage_mount_path'):
                        result += f"存储挂载路径: {instance.get('storage_mount_path')}\n"
                
                # 添加状态消息（如果有）
                if instance.get('status_message'):
                    result += f"\n状态消息: {instance.get('status_message')}\n"
                
                return (result,)
            else:
                return (f"查询失败: {response_json.get('message', '未知错误')}",)
        except Exception as e:
            return (f"查询过程中发生错误: {str(e)}",)

class XiangongListInstances:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("instances_list",)
    FUNCTION = "list_instances"
    CATEGORY = "XiangongCloud"

    def list_instances(self, api_key):
        if not api_key:
            return ("错误: API密钥不能为空",)
        
        url = "https://api.xiangongyun.com/open/instance/list"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()
            
            if response.status_code == 200 and (response_json.get("code") == 0 or response_json.get("code") == 200):
                instances = response_json.get("data", [])
                if not instances:
                    return ("没有找到实例。",)
                
                result = "实例列表:\n\n"
                for idx, instance in enumerate(instances, 1):
                    result += f"实例 {idx}:\n"
                    result += f"  ID: {instance.get('id')}\n"
                    result += f"  名称: {instance.get('name')}\n"
                    result += f"  状态: {instance.get('status')}\n"
                    result += f"  GPU型号: {instance.get('gpu_model')}\n"
                    result += f"  GPU数量: {instance.get('gpu_count')}\n"
                    result += f"  IP地址: {instance.get('ip')}\n"
                    result += f"  创建时间: {instance.get('created_at')}\n\n"
                
                return (result,)
            else:
                return (f"查询失败: {response_json.get('message', '未知错误')}",)
        except Exception as e:
            return (f"查询过程中发生错误: {str(e)}",)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "XiangongDeployInstance": XiangongDeployInstance,
    "XiangongInstanceDetails": XiangongInstanceDetails,
    "XiangongListInstances": XiangongListInstances
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XiangongDeployInstance": "部署仙宫云实例",
    "XiangongInstanceDetails": "查询实例详情",
    "XiangongListInstances": "仙宫云key"
}
