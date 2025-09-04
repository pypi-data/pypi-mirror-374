from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os
import re
import shutil
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# 使用用户临时目录存放日志文件
log_dir = Path(tempfile.gettempdir()) / "video-compressor-mcp"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "debug.log"

file_handler = RotatingFileHandler(str(log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.propagate = False

FFMPEG_BINARY = os.environ.get('FFMPEG_BINARY')
FFPROBE_BINARY = os.environ.get('FFPROBE_BINARY')


def _ffmpeg_run(stream_spec, **kwargs):
    if 'overwrite_output' not in kwargs:
        kwargs['overwrite_output'] = True
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BINARY, **kwargs)

def _prepare_path(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise RuntimeError(f"Error: Input file not found at {input_path}")
    try:
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creating output directory for {output_path}: {str(e)}")
    if os.path.exists(output_path):
        raise RuntimeError(
            f"Error: Output file already exists at {output_path}. Please choose a different path or delete the existing file.")

mcp = FastMCP("VideoCompressServer")

def _run_ffmpeg_with_fallback(input_path: str, output_path: str, primary_kwargs: dict, fallback_kwargs: dict) -> str:
    try:
        _ffmpeg_run(ffmpeg.input(input_path).output(output_path, **primary_kwargs), capture_stdout=True,
                    capture_stderr=True)
        return f"Operation successful (primary method) and saved to {output_path}"
    except ffmpeg.Error as e_primary:
        try:
            _ffmpeg_run(ffmpeg.input(input_path).output(output_path, **fallback_kwargs), capture_stdout=True,
                        capture_stderr=True)
            return f"Operation successful (fallback method) and saved to {output_path}"
        except ffmpeg.Error as e_fallback:
            err_primary_msg = e_primary.stderr.decode('utf8') if e_primary.stderr else str(e_primary)
            err_fallback_msg = e_fallback.stderr.decode('utf8') if e_fallback.stderr else str(e_fallback)
            raise RuntimeError(
                f"Error. Primary method failed: {err_primary_msg}. Fallback method also failed: {err_fallback_msg}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def set_video_bitrate(input_video_path: str, output_video_path: str, video_bitrate: str) -> str:
    """设置视频码率。

    Args:
        input_video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        video_bitrate: 目标视频码率（如 '2500k'、'1M'）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(input_video_path, output_video_path)
    # 校验码率格式
    if not re.match(r'^\d+[kKmM]?$', video_bitrate):
        raise RuntimeError(
            f"Error: Invalid video_bitrate format '{video_bitrate}'. Expected format like '2500k', '1M', or '1000'.")

    primary_kwargs = {'video_bitrate': video_bitrate, 'acodec': 'copy'}
    fallback_kwargs = {'video_bitrate': video_bitrate}
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)


@mcp.tool()
def set_video_resolution(input_video_path: str, output_video_path: str, resolution: str) -> str:
    """设置视频分辨率。

    Args:
        input_video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        resolution: 目标分辨率，支持 '宽x高'（如 '1920x1080'）或仅高度（如 '720'，宽度自动按比例）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(input_video_path, output_video_path)
    # 校验分辨率格式
    if 'x' in resolution:
        if not re.match(r'^\d{2,5}x\d{2,5}$', resolution):
            raise RuntimeError(f"Error: Invalid resolution format '{resolution}'. Expected format like '1920x1080'.")
    else:
        if not re.match(r'^\d{2,5}$', resolution):
            raise RuntimeError(f"Error: Invalid resolution format '{resolution}'. Expected height like '720'.")

    vf_filters = []
    if 'x' in resolution:
        vf_filters.append(f"scale={resolution}")
    else:
        vf_filters.append(f"scale=-2:{resolution}")
    vf_filter_str = ",".join(vf_filters)
    primary_kwargs = {'vf': vf_filter_str, 'acodec': 'copy'}
    fallback_kwargs = {'vf': vf_filter_str}
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)


@mcp.tool()
def set_video_frame_rate(input_video_path: str, output_video_path: str, frame_rate: int) -> str:
    """设置视频帧率。

    Args:
        input_video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        frame_rate: 目标帧率（如 24、30、60）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(input_video_path, output_video_path)
    # 校验帧率范围
    if frame_rate <= 0 or frame_rate > 240:
        raise RuntimeError(f"Error: Invalid frame_rate '{frame_rate}'. Expected range: 1-240 fps.")

    primary_kwargs = {'r': frame_rate, 'acodec': 'copy'}
    fallback_kwargs = {'r': frame_rate}
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)


@mcp.tool()
def set_video_codec(input_video_path: str, output_video_path: str, video_codec: str) -> str:
    """设置视频编码器。

    Args:
        input_video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        video_codec: 目标视频编码器（如 'libx264'、'libx265'、'vp9'）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(input_video_path, output_video_path)
    # 常见视频编码器校验
    common_codecs = {
        'libx264', 'libx265', 'h264', 'h265', 'hevc',
        'vp8', 'vp9', 'libvpx', 'libvpx-vp9',
        'mpeg4', 'wmv2', 'copy'
    }
    if video_codec not in common_codecs:
        logger.warning(f"Warning: '{video_codec}' is not a common video codec. Proceeding anyway.")

    # 为常见编码器设置兼容的像素格式
    extra_kwargs = {}
    if video_codec in {'libx264', 'libx265', 'h264', 'h265', 'hevc'}:
        extra_kwargs['pix_fmt'] = 'yuv420p'

    primary_kwargs = {'vcodec': video_codec, 'acodec': 'copy', **extra_kwargs}
    fallback_kwargs = {'vcodec': video_codec, **extra_kwargs}
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()