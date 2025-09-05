#!/usr/bin/env python3
"""
抖音无水印视频下载并提取文本的 MCP 服务器

该服务器提供以下功能：
1. 解析抖音分享链接获取无水印视频链接
2. 下载视频并提取音频
3. 从音频中提取文本内容
4. 自动清理中间文件
"""

import os
import re
import json
import requests
import tempfile
import asyncio
import time
from pathlib import Path
from typing import Optional, Tuple
import ffmpeg
from tqdm.asyncio import tqdm
from urllib import request
from http import HTTPStatus
import dashscope

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context


# 创建 MCP 服务器实例
mcp = FastMCP("kbase-mcp-server",
              dependencies=["requests", "ffmpeg-python", "tqdm", "dashscope"])

# 请求头，模拟移动端访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1'
}

# 默认 API 配置
DEFAULT_MODEL = "paraformer-v2"


class DouyinProcessor:
    """抖音视频处理器"""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or DEFAULT_MODEL
        self.temp_dir = Path(tempfile.mkdtemp())
        # 设置阿里云百炼API密钥
        dashscope.api_key = api_key
    
    def __del__(self):
        """清理临时目录"""
        import shutil
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def parse_share_url(self, share_text: str) -> dict:
        """从分享文本中提取无水印视频链接"""
        # 提取分享链接
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', share_text)
        if not urls:
            raise ValueError("未找到有效的分享链接")
        
        share_url = urls[0]
        share_response = requests.get(share_url, headers=HEADERS)
        video_id = share_response.url.split("?")[0].strip("/").split("/")[-1]
        share_url = f'https://www.iesdouyin.com/share/video/{video_id}'
        
        # 获取视频页面内容
        response = requests.get(share_url, headers=HEADERS)
        response.raise_for_status()
        
        pattern = re.compile(
            pattern=r"window\._ROUTER_DATA\s*=\s*(.*?)</script>",
            flags=re.DOTALL,
        )
        find_res = pattern.search(response.text)

        if not find_res or not find_res.group(1):
            raise ValueError("从HTML中解析视频信息失败")

        # 解析JSON数据
        json_data = json.loads(find_res.group(1).strip())
        VIDEO_ID_PAGE_KEY = "video_(id)/page"
        NOTE_ID_PAGE_KEY = "note_(id)/page"
        
        if VIDEO_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][VIDEO_ID_PAGE_KEY]["videoInfoRes"]
        elif NOTE_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][NOTE_ID_PAGE_KEY]["videoInfoRes"]
        else:
            raise Exception("无法从JSON中解析视频或图集信息")

        data = original_video_info["item_list"][0]

        # 获取视频信息
        video_url = data["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
        desc = data.get("desc", "").strip() or f"douyin_{video_id}"
        
        # 替换文件名中的非法字符
        desc = re.sub(r'[\\/:*?"<>|]', '_', desc)
        
        return {
            "url": video_url,
            "title": desc,
            "video_id": video_id
        }
    
    async def download_video(self, video_info: dict, ctx: Context) -> Path:
        """异步下载视频到临时目录"""
        filename = f"{video_info['video_id']}.mp4"
        filepath = self.temp_dir / filename
        
        ctx.info(f"正在下载视频: {video_info['title']}")
        
        response = requests.get(video_info['url'], headers=HEADERS, stream=True)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        
        # 异步下载文件，显示进度
        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = downloaded / total_size
                        await ctx.report_progress(downloaded, total_size)
        
        ctx.info(f"视频下载完成: {filepath}")
        return filepath
    
    def extract_audio(self, video_path: Path) -> Path:
        """从视频文件中提取音频"""
        audio_path = video_path.with_suffix('.mp3')
        
        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='libmp3lame', q=0)
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            return audio_path
        except Exception as e:
            raise Exception(f"提取音频时出错: {str(e)}")
    
    def extract_text_from_video_url(self, video_url: str) -> str:
        """从视频URL中提取文字（使用阿里云百炼API）"""
        try:
            # 发起异步转录任务
            task_response = dashscope.audio.asr.Transcription.async_call(
                model=self.model,
                file_urls=[video_url],
                language_hints=['zh', 'en']
            )
            
            # 等待转录完成
            transcription_response = dashscope.audio.asr.Transcription.wait(
                task=task_response.output.task_id
            )
            
            if transcription_response.status_code == HTTPStatus.OK:
                # 获取转录结果
                for transcription in transcription_response.output['results']:
                    url = transcription['transcription_url']
                    result = json.loads(request.urlopen(url).read().decode('utf8'))
                    
                    # 保存结果到临时文件
                    temp_json_path = self.temp_dir / 'transcription.json'
                    with open(temp_json_path, 'w') as f:
                        json.dump(result, f, indent=4, ensure_ascii=False)
                    
                    # 提取文本内容
                    if 'transcripts' in result and len(result['transcripts']) > 0:
                        return result['transcripts'][0]['text']
                    else:
                        return "未识别到文本内容"
                        
            else:
                raise Exception(f"转录失败: {transcription_response.output.message}")
                
        except Exception as e:
            raise Exception(f"提取文字时出错: {str(e)}")
    
    def cleanup_files(self, *file_paths: Path):
        """清理指定的文件"""
        for file_path in file_paths:
            if file_path.exists():
                file_path.unlink()


@mcp.tool()
def get_douyin_download_link(share_link: str) -> str:
    """
    获取抖音视频的无水印下载链接
    
    参数:
    - share_link: 抖音分享链接或包含链接的文本
    
    返回:
    - 包含下载链接和视频信息的JSON字符串
    """
    try:
        processor = DouyinProcessor("")  # 获取下载链接不需要API密钥
        video_info = processor.parse_share_url(share_link)
        
        return json.dumps({
            "status": "success",
            "video_id": video_info["video_id"],
            "title": video_info["title"],
            "download_url": video_info["url"],
            "description": f"视频标题: {video_info['title']}",
            "usage_tip": "可以直接使用此链接下载无水印视频"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"获取下载链接失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def extract_douyin_text(
    share_link: str,
    model: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    从抖音分享链接提取视频中的文本内容
    
    参数:
    - share_link: 抖音分享链接或包含链接的文本
    - model: 语音识别模型（可选，默认使用paraformer-v2）
    
    返回:
    - 提取的文本内容
    
    注意: 需要设置环境变量 DASHSCOPE_API_KEY
    """
    try:
        # 从环境变量获取API密钥
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            raise ValueError("未设置环境变量 DASHSCOPE_API_KEY，请在配置中添加阿里云百炼API密钥")
        
        processor = DouyinProcessor(api_key, model)
        
        # 解析视频链接
        ctx.info("正在解析抖音分享链接...")
        video_info = processor.parse_share_url(share_link)
        
        # 直接使用视频URL进行文本提取
        ctx.info("正在从视频中提取文本...")
        text_content = processor.extract_text_from_video_url(video_info['url'])
        
        ctx.info("文本提取完成!")
        return text_content
        
    except Exception as e:
        ctx.error(f"处理过程中出现错误: {str(e)}")
        raise Exception(f"提取抖音视频文本失败: {str(e)}")


@mcp.tool()
def parse_douyin_video_info_detail(share_link: str) -> str:
    """
    解析抖音分享链接，获取视频基本信息
    
    参数:
    - share_link: 抖音分享链接或包含链接的文本
    
    返回:
    - 视频信息（JSON格式字符串）
    """
    try:
        processor = DouyinProcessor("")  # 不需要API密钥来解析链接
        video_info = processor.parse_share_url(share_link)

        return json.dumps({
            "video_id": video_info["video_id"],
            "title": video_info["title"],
            "download_url": video_info["url"],
            "status": "success"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False, indent=2)



@mcp.tool()
def fetch_external_data(page_num: int = 1, page_size: int = 20) -> str:
    """
    获取外部数据
    
    参数:
    - page_num: 页码，默认为1
    - page_size: 每页数量，默认为20
    
    返回:
    - API响应结果的字符串形式
    """
    import requests
    
    url = f'https://v2.fangcloud.com/aiapi/knowledgeDataCollect/externaDataCollectpage?_={int(time.time()*1000)}'
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://v2.fangcloud.com',
        'Pragma': 'no-cache',
        'Referer': 'https://v2.fangcloud.com/console/gather/external',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    # 注意：实际使用时需要替换为有效的Cookie
    cookies = {
        '__guid': '67627350.493078613471557440.1747312329462.944',
        'device_token': '0c4be4b62e5c22af69b481e136ea5cb6',
        '__root_domain_v': '.fangcloud.com',
        '_qddaz': 'QD.553549197110339',
        '_c_WBKFRo': '7bGUYvSfNsAJHOxfvYNeQtvxJPttAq5VkYL43LtB',
        'Hm_lvt_05713beafc7f9b26f552d1d194d915d2': '1752138521',
        'Qs_lvt_389248': '1752138520,1752231249',
        'Qs_pv_389248': '153042335511384480,1997181492032253000',
        'lang': 'zh-CN',
        '__DC_sid': '67627350.1390666347727731000.1756887501908.5254',
        'Hm_lvt_762d2bc251bef4b42a758268dc7edda3': '1755670682,1756436725,1756799141,1756887504',
        'HMACCOUNT': '7C58F7722482AAD1',
        'LoginRedirect': 'https%3A%2F%2Fv2.fangcloud.com%2Fdesktop%2Faihome%2Fqa',
        'session_sso_cookie_name': '57f7c047bb8342b98b4b97ad451e63a0',
        'fc_session': 'eyJpdiI6ImltakVySHhNZ1BPNmxjeFM5aXJmN1E9PSIsInZhbHVlIjoiK3dNOVQ2YUhMaEowNG5MbHNmb1NualJjbFwvK3ZyXC9hNlZNaldBRjByQzJNUkZaV0t0dmhXQ0NXc1ZYdHJzcHltWG9oS2pCeDlQODBPRVBoNWZFZGYxUT09IiwibWFjIjoiN2E5YjhlMmU3MDc4ZjA0M2ZmNGQ0ZDBjNjczZjlmMTY5OWYyZDhmZjE4MDUxMzFlOTFiZDdmMmYzNTg5MDQ3NiJ9',
        'is_ai_cloud_enabled': 'always',
        '__DC_monitor_count': '7',
        '__DC_gid': '67627350.696092156.1747312329462.1756887511169.729',
        'XSRF-TOKEN': 'ewogICJpdiIgOiAidEFLNWxMVkQyRHo0RW5aYW1DeENaQT09IiwKICAidmFsdWUiIDogIkpCVjl4NHVlNUtBdFk4QXEwU2tTY0NLaUp1OFQ2ZDlMSHpsa1V0OGlUK2NUT3JJTzQ0d2V3K05zMFBqazZqQUZmTTZOV0xOUkNIeDFEeTNueTA3UzBnPT0iLAogICJtYWMiIDogIjBkOGQyZjBmMzA0NmZlMDRkNTQwNmMxMzcwNDEyMmY0Y2VhM2JkODU2MDA2MjMxYjc0MjVjMGFhMzY5YzM0N2QiCn0=',
        'Hm_lpvt_762d2bc251bef4b42a758268dc7edda3': '1756887512'
    }
    
    data = {
        "pageNum": page_num,
        "pageSize": page_size
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"请求失败: {str(e)}"


@mcp.tool()
def push_ai_qa_to_library(question: str, content: str) -> str:
    """
    将AI问答内容推送到知识库

    参数:
    - question: 问题
    - content: 回答内容

    返回:
    - API响应结果的字符串形式
    """
    import requests
    import time

    url = f'https://ask.fangcloud.com/kbase/library/pushAiQaToLibrary?_={int(time.time() * 1000)}'

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://ask.fangcloud.com',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Referer': 'https://ask.fangcloud.com/kbase-web/v4/index/kbase',
        'RequestToken': 'SMSPEwTv0TcWEP6z18EwiNInLrJcIAllygNad0Fp',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'ewogICJpdiIgOiAiYm5Lc281MTVweHMwbGRoNFAzL0xFQT09IiwKICAidmFsdWUiIDogIndOellCeEFMMmRxOVN3TDhQNjVjQXAwZG9USnBzZ0RYd1RYRXVGU2FtN3lIaldodkVKVHRZcWlXRDBNdVdMQUlBbXk2QXhNTXdkVG5BYlhNSlpTN253PT0iLAogICJtYWMiIDogImI1Zjk1ZjhiMTc1ZjVkMzI0MjVmOTZhYWRjMzhjYTc1OGY1YWY3Yzc4N2QwNDQ5OTIzNzVlZTY4ZTk1MzI2MGIiCn0='
    }

    # 从环境变量获取API密钥
    kbase_key = os.getenv('KBASE_KEY')
    if not kbase_key:
        raise ValueError("未设置环境变量 KBASE_KEY，请在配置中添加知识库密钥")

    if not isinstance(kbase_key, str):
        # 如果是集合或其他类型，转换为字符串
        kbase_key = str(kbase_key)

    cookies = {
        'cookie': kbase_key
    }

    data = {
        "libraryId": '17a7fd4e713b89aa69174d95a6335a10',
        "documentId": 0,
        "qaInfo": {
            "question": question,
            "content": content
        }
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"请求失败: {str(e)}"



@mcp.resource("douyin://video/{video_id}")
def get_video_info(video_id: str) -> str:
    """
    获取指定视频ID的详细信息
    
    参数:
    - video_id: 抖音视频ID
    
    返回:
    - 视频详细信息
    """
    share_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    try:
        processor = DouyinProcessor("")
        video_info = processor.parse_share_url(share_url)
        return json.dumps(video_info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取视频信息失败: {str(e)}"


@mcp.prompt()
def douyin_text_extraction_guide() -> str:
    """抖音视频文本提取使用指南"""
    return """
# 抖音视频文本提取使用指南

## 功能说明
这个MCP服务器可以从抖音分享链接中提取视频的文本内容，以及获取无水印下载链接。

## 环境变量配置
请确保设置了以下环境变量：
- `DASHSCOPE_API_KEY`: 阿里云百炼API密钥

## 使用步骤
1. 复制抖音视频的分享链接
2. 在Claude Desktop配置中设置环境变量 DASHSCOPE_API_KEY
3. 使用相应的工具进行操作

## 工具说明
- `extract_douyin_text`: 完整的文本提取流程（需要API密钥）
- `get_douyin_download_link`: 获取无水印视频下载链接（无需API密钥）
- `parse_douyin_video_info`: 仅解析视频基本信息
- `add_two_integers`: 计算两个整数的加法运算
- `fetch_external_data`: 获取外部数据（需要有效Cookie）
- `push_ai_qa_to_library`: 将AI问答内容推送到知识库（需要有效Cookie）
- `douyin://video/{video_id}`: 获取指定视频的详细信息

## Claude Desktop 配置示例
```json
{
  "mcpServers": {
    "douyin-mcp": {
      "command": "uvx",
      "args": ["kkse-mcp-server"],
      "env": {
        "DASHSCOPE_API_KEY": "your-dashscope-api-key-here"
      }
    }
  }
}
```

## 注意事项
- 需要提供有效的阿里云百炼API密钥（通过环境变量）
- 使用阿里云百炼的paraformer-v2模型进行语音识别
- 支持大部分抖音视频格式
- 获取下载链接无需API密钥
"""


def main():
    """启动MCP服务器"""
    mcp.run()


if __name__ == "__main__":
    main()