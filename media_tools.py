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


def mux_original_audio(video_path, audio_path, match_audio_length=True):
    """Replace the generated soundtrack with the untouched source audio.

    When match_audio_length=True, trims the output to the exact duration of the audio,
    eliminating any trailing padding or silent dead frames.
    """
    root, ext = os.path.splitext(video_path)
    output = f"{root}_原音{ext}"
    v_dur = media_duration(video_path)
    a_dur = media_duration(audio_path)
    target_dur = a_dur if match_audio_length else v_dur
    _run_ffmpeg(["-i", video_path, "-i", audio_path, "-map", "0:v:0", "-map", "1:a:0",
                 "-t", f"{target_dur:.4f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", output])
    return output


def extract_last_frame(video_path, output_path=None):
    """Extract the exact final frame of a video to a PNG image."""
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), f"h3_last_frame_{uuid.uuid4().hex[:10]}.png")
    # -sseof -0.2 seeks near EOF; -update 1 continuously overwrites until the final decoded frame
    try:
        _run_ffmpeg(["-sseof", "-0.2", "-i", video_path, "-update", "1", "-q:v", "1", output_path])
    except Exception:
        pass
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        # Fallback for very short videos: decode from beginning
        _run_ffmpeg(["-i", video_path, "-update", "1", "-q:v", "1", output_path])
    return output_path


def slice_audio(audio_path, start_sec, duration_sec, output_path=None):
    """Slice an audio file accurately from start_sec for duration_sec, exported as uncompressed 16-bit PCM WAV at 44.1kHz."""
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), f"h3_aslice_{uuid.uuid4().hex[:10]}.wav")
    # Put -i before -ss for sample-accurate decoding, and export to uncompressed PCM WAV at 44.1kHz
    _run_ffmpeg(["-i", audio_path, "-ss", f"{start_sec:.4f}", "-t", f"{duration_sec:.4f}",
                 "-c:a", "pcm_s16le", "-ar", "44100", output_path])
    return output_path


def slice_video(video_path, start_sec, duration_sec, output_path=None):
    """Slice a video file accurately from start_sec for duration_sec, retimed to 24fps and scaled to 720px max short edge."""
    audio = has_audio_stream(video_path)
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), f"h3_vslice_{uuid.uuid4().hex[:10]}.mp4")
    # Put -i before -ss for exact frame decoding
    args = ["-i", video_path, "-ss", f"{start_sec:.4f}", "-t", f"{duration_sec:.4f}",
            "-vf", f"fps={H3_FPS},scale='if(gt(iw,ih),-2,min(720,iw))':'if(gt(iw,ih),min(720,ih),-2)'",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p"]
    args += ["-c:a", "aac", "-b:a", "192k"] if audio else ["-an"]
    _run_ffmpeg(args + [output_path])
    return output_path


def concat_video_segments(segment_paths, output_path=None):
    """Concatenate multiple video segments into one seamless video.

    First tries fast stream copy via concat demuxer. If streams differ, falls back to filter_complex re-encode.
    """
    if not segment_paths:
        raise ValueError("No video segments to concatenate")
    if len(segment_paths) == 1:
        return segment_paths[0]

    if not output_path:
        root, ext = os.path.splitext(segment_paths[0])
        output_path = f"{root}_concat_{uuid.uuid4().hex[:6]}{ext or '.mp4'}"

    # Try fast demuxer copy first
    concat_list_file = os.path.join(tempfile.gettempdir(), f"concat_{uuid.uuid4().hex[:8]}.txt")
    try:
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in segment_paths:
                clean_p = p.replace("\\", "/")
                f.write(f"file '{clean_p}'\n")
        _run_ffmpeg(["-f", "concat", "-safe", "0", "-i", concat_list_file, "-c", "copy", output_path])
        return output_path
    except Exception:
        # Fallback to re-encode filter_complex
        has_audio = any(has_audio_stream(p) for p in segment_paths)
        inputs = []
        for p in segment_paths:
            inputs.extend(["-i", p])
        n = len(segment_paths)
        if has_audio:
            filter_str = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(n)) + f"concat=n={n}:v=1:a=1[outv][outa]"
            _run_ffmpeg([*inputs, "-filter_complex", filter_str, "-map", "[outv]", "-map", "[outa]",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", output_path])
        else:
            filter_str = "".join(f"[{i}:v:0]" for i in range(n)) + f"concat=n={n}:v=1:a=0[outv]"
            _run_ffmpeg([*inputs, "-filter_complex", filter_str, "-map", "[outv]",
                         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", output_path])
        return output_path
    finally:
        if os.path.exists(concat_list_file):
            try:
                os.remove(concat_list_file)
            except OSError:
                pass


def snap_h3_frames(frames):
    """Snap frame count up to H3's trained 17n + 5 sequence."""
    frames = max(5, int(frames))
    while frames % 17 != 5:
        frames += 1
    return frames


SINGLE_SEGMENT_MAX_SECONDS = 16.0


def plan_segment_durations(total_seconds, max_segment_seconds=12.0, single_segment_threshold=SINGLE_SEGMENT_MAX_SECONDS):
    """Plan segment (start_seconds, duration_seconds, frame_count) for long video generation.

    If total_seconds <= single_segment_threshold (default 16.0s, accommodating common ~15.1s nominal 15s clips),
    returns a single segment.
    If total_seconds > single_segment_threshold, divides into balanced segments <= max_segment_seconds,
    each snapped to an H3-valid 17n+5 frame length so audio and video stay 100% synchronized.
    """
    if total_seconds <= single_segment_threshold:
        frames = snap_h3_frames(round(total_seconds * H3_FPS))
        return [(0.0, total_seconds, frames)]

    total_frames = math.ceil(total_seconds * H3_FPS)
    max_frames = snap_h3_frames(round(max_segment_seconds * H3_FPS))
    num_segments = math.ceil(total_frames / max_frames)
    target_per_seg = math.ceil(total_frames / num_segments)
    base_frames = snap_h3_frames(target_per_seg)

    segments = []
    curr_frame = 0
    for i in range(num_segments):
        if i == num_segments - 1:
            rem_frames = total_frames - curr_frame
            seg_frames = snap_h3_frames(rem_frames)
            segments.append((curr_frame / H3_FPS, seg_frames / H3_FPS, seg_frames))
        else:
            segments.append((curr_frame / H3_FPS, base_frames / H3_FPS, base_frames))
            curr_frame += base_frames
    return segments
