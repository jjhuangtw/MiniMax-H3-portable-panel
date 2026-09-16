"""Media helpers for the H3 panel: probing, reference-video preparation, auto canvas size and audio muxing."""
import math
import os
import subprocess
import tempfile
import uuid

import av
import imageio_ffmpeg
from PIL import Image

H3_FPS = 24
# Ref2VA reference videos are trained on 2-15 s clips; 362 frames is the longest 17n+5 length within 15.1 s.
MAX_REF_SECONDS = 362 / H3_FPS
CANVAS_MULTIPLE = 32

AUTO_RESOLUTION_CHOICES = {
    "自動・依素材比例（約 0.4 MP，≈864×480）": 0.42,
    "自動・依素材比例（約 0.6 MP，≈1056×576）": 0.6,
    "自動・依素材比例（約 0.9 MP，≈1280×704）": 0.9,
}


def ffmpeg_exe():
    return imageio_ffmpeg.get_ffmpeg_exe()


def media_duration(path):
    with av.open(path) as container:
        if container.duration:
            return container.duration / 1_000_000
        stream = (container.streams.audio or container.streams.video)[0]
        return float(stream.duration * stream.time_base)


def has_audio_stream(path):
    with av.open(path) as container:
        return bool(container.streams.audio)


def visual_size(path):
    """Width and height of an image, or of a video's first stream."""
    try:
        with Image.open(path) as image:
            return image.size
    except OSError:
        with av.open(path) as container:
            stream = container.streams.video[0]
            return stream.codec_context.width, stream.codec_context.height


def auto_canvas(source_path, megapixels):
    """Keep the source aspect ratio at roughly the requested pixel area, snapped to H3's 32 px grid."""
    width, height = visual_size(source_path)
    area = megapixels * 1024 * 1024
    scale = math.sqrt(area / (width * height))
    return (max(CANVAS_MULTIPLE, round(width * scale / CANVAS_MULTIPLE) * CANVAS_MULTIPLE),
            max(CANVAS_MULTIPLE, round(height * scale / CANVAS_MULTIPLE) * CANVAS_MULTIPLE))


def _run_ffmpeg(args):
    result = subprocess.run([ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", *args],
                            capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-800:] or "ffmpeg failed")


def prepare_reference_video(path):
    """Re-time to 24 fps, cap at the trained 15 s and shrink to a 720 px short edge.

    H3 reads reference frames as 24 fps, so a 30/60 fps upload would otherwise play back too slowly.
    Returns (prepared_path, has_audio, seconds).
    """
    audio = has_audio_stream(path)
    output = os.path.join(tempfile.gettempdir(), f"h3_ref_{uuid.uuid4().hex[:10]}.mp4")
    args = ["-i", path, "-t", f"{MAX_REF_SECONDS:.3f}",
            "-vf", f"fps={H3_FPS},scale='if(gt(iw,ih),-2,min(720,iw))':'if(gt(iw,ih),min(720,ih),-2)'",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p"]
    args += ["-c:a", "aac", "-b:a", "192k"] if audio else ["-an"]
    _run_ffmpeg(args + [output])
    return output, audio, media_duration(output)


def mux_original_audio(video_path, audio_path):
    """Replace the generated soundtrack with the untouched source audio, padded or cut to the video length."""
    root, ext = os.path.splitext(video_path)
    output = f"{root}_原音{ext}"
    # An explicit -t: "apad" never ends, and -shortest does not stop it while the video stream is copied.
    _run_ffmpeg(["-i", video_path, "-i", audio_path, "-map", "0:v:0", "-map", "1:a:0", "-t", f"{media_duration(video_path):.3f}",
                 "-c:v", "copy", "-af", "apad", "-c:a", "aac", "-b:a", "192k", output])
    return output
