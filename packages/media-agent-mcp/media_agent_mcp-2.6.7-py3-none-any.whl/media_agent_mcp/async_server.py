#!/usr/bin/env python3
"""Async Media Agent MCP Server - A Model Context Protocol server for media processing with async support.

This server provides 11 async tools for media processing using threading:
1. TOS - Save content as URL
2. Video Concat - Concatenate two videos
3. Video Last Frame - Get the last frame from a video
4. Combine Audio Video - Combine video and audio with optional delay
5. Seedream - Creating images (AI model)
6. Seedance (lite & pro) - Creating videos (AI model)
7. Seededit - Maintain the main character (AI model)
8. Seed1.6 (VLM) - Do vision tasks in workflow (AI model)
9. Image Selector - Choose the best one from images
10. Video Selector - Choose the best video from videos
11. TTS - Convert text to speech and return audio URL

All tools are wrapped with threading to provide async functionality without modifying original functions.
"""

import argparse
import asyncio
import logging
from typing import List, Optional
import json
from dotenv import load_dotenv
import uvicorn
import anyio
from functools import wraps
import os
import sys
import signal
import subprocess

def async_retry(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error_message = None
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    if isinstance(result, dict) and result.get('status') == 'error':
                        last_error_message = result.get('message', 'Unknown error')
                        logger.warning(f"Attempt {attempt + 1} of {max_retries} failed for {func.__name__}. Error: {last_error_message}. Retrying in {delay}s...")
                        if attempt < max_retries - 1:  # Don't sleep on the last attempt
                            await asyncio.sleep(delay)
                        continue
                    return result
                except Exception as e:
                    last_exception = str(e)
                    logger.error(f"Attempt {attempt + 1} of {max_retries} failed for {func.__name__} with exception: {e}. Retrying in {delay}s...")
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        await asyncio.sleep(delay)
            
            # Use the last actual error message instead of generic retry message
            final_error_message = last_error_message or last_exception or f"Function {func.__name__} failed after {max_retries} retries"
            logger.error(f"Function {func.__name__} failed after {max_retries} retries. Last error: {final_error_message}")
            return {"status": "error", "data": None, "message": final_error_message}
        return wrapper
    return decorator

from mcp.server.fastmcp import FastMCP

# Import async wrappers
from media_agent_mcp.async_wrapper import (
    async_video_concat_tool, async_video_last_frame_tool, 
    async_combine_audio_video_tool,
    async_seedream_generate_image_tool, async_seedance_generate_video_tool, 
    async_seededit_tool, async_vlm_vision_task_tool, 
    async_image_selector_tool, async_video_selector_tool, 
    async_tos_save_content_tool, cleanup_executor,
    async_openaiedit_tool, async_google_edit_tool,
    async_get_voice_speaker_tool, async_get_tts_video_tool,
    async_tts_tool,
    async_add_subtitles_to_video_tool,
    async_install_tools_plugin,
    async_video_stack_tool,
    async_omni_human_tool
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Swallow ClosedResourceError from AnyIO (e.g., SSE client disconnected)
class IgnoreClosedResourceErrorMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except anyio.ClosedResourceError:
            logger.warning("SSE client disconnected (ClosedResourceError). Ignoring.")
            return

# Enhanced middleware that supports reconnection for SSE clients
class ReconnectableSSEMiddleware:
    def __init__(self, app):
        self.app = app
        self.connections = {}  # 存储活跃连接

    async def __call__(self, scope, receive, send):
        # 为每个连接生成唯一ID
        connection_id = scope.get('client', ('unknown', 0))[0] + ':' + str(scope.get('client', ('unknown', 0))[1])
        
        # 包装send函数以跟踪连接状态
        original_send = send
        
        async def wrapped_send(message):
            if message.get('type') == 'http.response.start':
                # 记录新连接
                self.connections[connection_id] = {'active': True}
                logger.info(f"New SSE connection established: {connection_id}")
            elif message.get('type') == 'http.response.body' and message.get('more_body', False) is False:
                # 连接结束
                if connection_id in self.connections:
                    self.connections[connection_id]['active'] = False
                    logger.info(f"SSE connection closed normally: {connection_id}")
            
            # 调用原始send
            await original_send(message)
        
        try:
            # 使用包装后的send函数
            await self.app(scope, receive, wrapped_send)
        except anyio.ClosedResourceError:
            # 客户端断开连接
            if connection_id in self.connections:
                self.connections[connection_id]['active'] = False
            
            logger.warning(f"SSE client disconnected (ClosedResourceError): {connection_id}. Client can reconnect.")
            # 不抛出异常，允许客户端重连
            return

# 在出现错误时重启应用的中间件
class RestartOnErrorMiddleware:
    def __init__(self, app):
        self.app = app
        self.restart_cooldown = 5  # 重启冷却时间（秒）
        self.script_path = os.path.abspath(sys.argv[0])
        self.args = sys.argv[1:]

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except anyio.ClosedResourceError:
            logger.warning("检测到 ClosedResourceError，准备重启应用...")
            # 等待一段时间，确保日志输出
            await asyncio.sleep(1)
            
            # 启动新进程，使用不同的端口避免冲突
            # 解析当前命令行参数以获取当前端口
            temp_parser = argparse.ArgumentParser()
            temp_parser.add_argument('--port', type=int, default=8000)
            temp_parser.add_argument('--host', type=str, default='127.0.0.1')
            temp_parser.add_argument('--transport', type=str, default='stdio')
            # 添加其他可能的参数，避免解析错误
            temp_parser.add_argument('--run-be', action='store_true')
            temp_parser.add_argument('--be-host', type=str, default='0.0.0.0')
            temp_parser.add_argument('--be-port', type=int, default=5000)
            temp_parser.add_argument('--version', action='store_true')
            
            # 忽略未知参数，避免解析错误
            known_args, _ = temp_parser.parse_known_args(self.args)
            
            # 计算新端口，当前端口+1
            new_port = known_args.port + 1
            logger.info(f"将使用新端口 {new_port} 启动新进程")
            
            # 准备新的命令行参数
            new_args = self.args.copy()
            
            # 如果命令行参数中有端口参数，则替换为新端口
            if '--port' in new_args:
                port_index = new_args.index('--port') + 1
                if port_index < len(new_args):
                    new_args[port_index] = str(new_port)
            else:
                new_args.extend(['--port', str(new_port)])
                
            logger.info(f"启动新进程: {self.script_path} {' '.join(new_args)}")
            new_process = subprocess.Popen([sys.executable, self.script_path] + new_args)
            
            # 等待确认新进程已启动
            logger.info(f"等待确认新进程已启动...")
            await asyncio.sleep(3)
            
            # 检查新进程是否成功启动
            if new_process.poll() is None:  # None表示进程仍在运行
                logger.info(f"新进程成功启动，将在 {self.restart_cooldown} 秒后终止当前进程...")
                await asyncio.sleep(self.restart_cooldown)
                
                # 终止当前进程
                logger.info("终止当前进程")
                sys.exit(0)
            else:
                logger.error(f"新进程启动失败，退出码: {new_process.returncode}，当前进程将继续运行")
                return
            return

# Initialize FastMCP server (will be configured in main function)
load_dotenv()
mcp = FastMCP("Media-Agent-MCP-Async")


@mcp.tool()
@async_retry()
async def video_concat_tool(video_urls: List[str]) -> dict:
    """
    Asynchronously concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_concat_tool(video_urls)
    return result


@mcp.tool()
@async_retry()
async def video_last_frame_tool(video_url: str) -> dict:
    """
    Asynchronously extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL of the video file
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_last_frame_tool(video_url)
    return result


@mcp.tool()
@async_retry()
async def combine_audio_video_tool(video_url: str, audio_url: str, delay_ms: float = 0.0) -> dict:
    """
    Asynchronously combine video and audio from URLs with optional delay.
    
    Args:
        video_url: URL of the video file
        audio_url: URL of the audio file
        delay_ms: Delay in milliseconds for the audio to start
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_combine_audio_video_tool(video_url, audio_url, delay_ms)
    return result


@mcp.tool()
@async_retry()
async def seedream_generate_image_tool(prompt: str, size: str = "1024x1024") -> dict:
    """
    Asynchronously generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seedream_generate_image_tool(prompt, size)
    return result


@mcp.tool()
@async_retry()
async def seedance_generate_video_tool(prompt: str, first_frame_image: str, 
                                            last_frame_image: str = None, duration: int = 5, 
                                            resolution: str = "720p") -> dict:
    """
    Asynchronously generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seedance_generate_video_tool(prompt, first_frame_image, last_frame_image, duration, resolution)
    return result


@mcp.tool()
@async_retry()
async def seededit_tool(image_url: str, prompt: str) -> dict:
    """
    Asynchronously edit an image using the OpenAI Images API.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seededit_tool(image_url, prompt)
    return result


@mcp.tool()
@async_retry()
async def openaiedit_tool(image_urls: List[str], prompt: str, size: str = "1024x1024") -> dict:
    """
    Asynchronously edit an image using the OpenAI Images API.
    
    Args:
        image_urls: List of input image URLs for editing (1 to 4 images)
        prompt: Text prompt for image editing
        size: The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_openaiedit_tool(image_urls, prompt, size)
    return result


@mcp.tool()
@async_retry()
async def google_edit_tool(image_urls: List[str], prompt: str) -> dict:
    """
    Asynchronously edit an image using the Google Gemini API.
    
    Args:
        image_urls: List of input image URLs for editing
        prompt: Text prompt for image editing
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_google_edit_tool(image_urls, prompt)
    return result


@async_retry()
async def vlm_vision_task_tool(messages: List) -> dict:
    """
    Asynchronously perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_vlm_vision_task_tool(messages)
    return result


@mcp.tool()
@async_retry()
async def image_selector_tool(image_paths: List[str], prompt: str) -> dict:
    """
    Asynchronously select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
        
    Returns:
        Dictionary with status, data, and message
    """
    try:
        result = await async_image_selector_tool(image_paths, prompt)
    except Exception as e:
        logger.error(f"Error in image_selector_tool: {str(e)}")
        result = {"status": "error", "data": None, "message": str(e)}
    
    return result


@mcp.tool()
@async_retry()
async def video_selector_tool(video_paths: List[str], prompt: str) -> dict:
    """
    Asynchronously select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_selector_tool(video_paths, prompt)
    return result


@async_retry()
async def tos_save_content_tool(content: str, file_extension: str = "txt", 
                                     object_key: Optional[str] = None) -> dict:
    """
    Asynchronously save content to TOS and return URL.
    
    Args:
        content: Content to save
        file_extension: File extension for the content (default: txt)
        object_key: Optional key to use for the object in TOS
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_tos_save_content_tool(content, file_extension, object_key)
    return result


# Utility function for concurrent execution
async def run_multiple_tools_concurrently(*coroutines):
    """
    Run multiple async tools concurrently.
    
    Args:
        *coroutines: Variable number of coroutines to run concurrently
        
    Returns:
        List of results from all coroutines
    """
    return await asyncio.gather(*coroutines, return_exceptions=True)


@mcp.tool()
@async_retry()
async def get_voice_speaker_tool(language: str, gender: str) -> dict:
    """
    Asynchronously get available TTS speakers filtered by language and gender.
    
    Args:
        language: Language enum (English, Chinese, American English, Australian English, British English, Japanese, Spanish)
        gender: Gender enum (Male, Female)
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_get_voice_speaker_tool(language, gender)
    return result


@mcp.tool()
@async_retry()
async def get_tts_video_tool(video_url: str, speaker_id: str, text: str, can_summarize: bool = False) -> dict:
    """
    Asynchronously generate a TTS voiceover and combine it with a video.
    Audio will be automatically centered in the video.
    
    Args:
        video_url: URL of the source video
        speaker_id: ID of the speaker to use for TTS
        text: Text to convert to speech
        can_summarize: Whether to summarize the text when audio is too long
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_get_tts_video_tool(video_url, speaker_id, text, can_summarize)
    return result


@mcp.tool()
@async_retry()
async def add_subtitles_to_video(video_url: str, subtitles_input: str, font_name: Optional[str] = None, font_color: Optional[str] = None, position: Optional[str] = None) -> dict:
    """
    Asynchronously add subtitles to a video with automatic styling and multi-line text support.
    If font_name or font_color is not provided, the tool will call Seed1.6 to analyze the video and auto-select based on predefined font descriptions.
    
    Args:
        video_url: URL of the video file to add subtitles to
        subtitles_input: SRT format subtitle content or path to SRT file. 
                        Example SRT format:
                        "1\n00:00:01,000 --> 00:00:04,000\nHello, this is the first subtitle line\nThis is a second line\n\n2\n00:00:05,000 --> 00:00:08,000\n这是第二条字幕\n支持中文和多行文本"
        font_name: Optional font name or absolute font path. If None, auto-selected.
        font_color: Optional hex color like #FFFF00. If None, auto-selected.
        position: Optional subtitle position: top, middle, or bottom. Defaults to bottom.
    
    Returns:
        Dictionary with status, data (video URL with subtitles), and message
    """
    result = await async_add_subtitles_to_video_tool(video_url, subtitles_input, font_name, font_color, position)
    return result


@mcp.tool()
@async_retry()
async def video_stack_tool(main_video_url: str, secondary_video_url: str) -> dict:
    """
    Asynchronously stacks the main video (bottom) and secondary video (top), automatically matches the main video duration, and uploads to TOS.
    
    Args:
        main_video_url: Main video URL
        secondary_video_url: Secondary video URL
    
    Returns:
        Dictionary containing status, TOS URL, and message
    """
    result = await async_video_stack_tool(main_video_url, secondary_video_url)
    return result

# @mcp.tool()
# @async_retry()
# async def install_tools_plugin() -> dict:
#     """
#     Asynchronously install development tools (ffmpeg and ffprobe) if not present, or return version and path if already installed.
    
#     Returns:
#         Dictionary with status, data (tools info), and message
#     """
#     result = await async_install_tools_plugin()
#     return result


@mcp.tool()
@async_retry()
async def omni_human_tool(image_url: str, audio_url: str) -> dict:
    """
    Asynchronously generate a video using Omni Human AI model.
    
    Args:
        image_url: URL of the input image
        audio_url: URL of the input audio
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_omni_human_tool(image_url, audio_url)
    return result


@mcp.tool()
@async_retry()
async def tts_tool(text: str, speaker_id: str) -> dict:
    """
    Asynchronously convert text to speech and upload to TOS.
    
    Args:
        text: Text to convert to speech
        speaker_id: Speaker ID for voice selection
    
    Returns:
        Dictionary with status, data (audio URL), and message
    """
    result = await async_tts_tool(text, speaker_id)
    return result


def main():
    """Main entry point for the Async MCP server."""
    import os
    import sys
    import subprocess
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Async Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='stdio',
                        help='Transport method: sse or stdio (default: stdio)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8000)')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    parser.add_argument('--run-be', action='store_true',
                        help='Run the backend server')
    parser.add_argument('--be-host', type=str, default='0.0.0.0',
                        help='Host for backend server (default: 0.0.0.0)')
    parser.add_argument('--be-port', type=int, default=5000,
                        help='Port for backend server (default: 8001)')

    args = parser.parse_args()

    if args.version:
        print("Async Media Agent MCP Server v0.1.0")
        return

    if args.run_be:
        logger.info(f"Starting backend server on {args.be_host}:{args.be_port}...")
        be_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'be'))
        if not os.path.isdir(be_path):
            logger.error(f"Backend directory not found at: {be_path}")
            return
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import sys, app; "
                        "flask_app = getattr(app, '_flask_app', getattr(app, 'app', None)); "
                        "assert flask_app is not None, 'No Flask application instance found in app.py'; "
                        "flask_app.run(host=sys.argv[1], port=int(sys.argv[2]), debug=False)"
                    ),
                    args.be_host,
                    str(args.be_port),
                ],
                cwd=be_path,
                check=True
            )
        except FileNotFoundError:
            logger.error("`uvicorn` command not found. Please ensure it is installed in your environment.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start backend server: {e}")
        return

    logger.info("Starting Async Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")

    logger.info("Available async tools:")
    logger.info("  1. video_last_frame_tool_async - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool_async - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool_async - Generate images with AI (async)")
    logger.info("  4. seedance_generate_video_tool_async - Generate videos with AI (async)")
    logger.info("  5. seededit_tool_async - Edit images while maintaining character (async)")
    logger.info("  6. vlm_vision_task_tool_async - Perform vision tasks with OpenAI-compatible messages (async)")
    logger.info("  7. image_selector_tool_async - Select best image using VLM model (async)")
    logger.info("  8. video_selector_tool_async - Select best video using VLM model (async)")
    logger.info("  9. add_subtitles_to_video_async - Add subtitles to video with automatic styling")
    logger.info(" 10. get_voice_speaker_tool_async - Get available TTS speakers")
    logger.info(" 11. get_tts_video_tool_async - Generate TTS voiceover and merge with video")
    logger.info(" 12. video_stack_tool_async - 垂直堆叠视频并上传至TOS")
    logger.info(" 13. install_tools_plugin_async - Install development tools (ffmpeg and ffprobe)")
    logger.info(" 14. omni_human_tool_async - Generate a video using Omni Human AI model")
    logger.info(" 15. google_edit_tool_async - Edit images with Google Gemini (async)")
    logger.info("")
    logger.info("All tools support concurrent execution using asyncio.gather() or run_multiple_tools_concurrently()")

    try:
        # Start the server with specified transport
        if args.transport == 'sse':
            logger.info(f"Starting async SSE server on {args.host}:{args.port}")
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            # Use uvicorn to run SSE app with extended keep-alive timeout (5 minutes)
            uvicorn.run(
                RestartOnErrorMiddleware(mcp.sse_app()),
                host=args.host,
                port=args.port,
                timeout_keep_alive=300
            )
        else:
            # Default stdio transport
            mcp.run(transport="stdio")
    finally:
        # Clean up thread pool executor on shutdown
        logger.info("Cleaning up thread pool executor...")
        cleanup_executor()


if __name__ == "__main__":
    main()