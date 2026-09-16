"""Portable Gradio integration for NyckM's H3 camera editor."""
import json
from pathlib import Path
from urllib.parse import quote

CAMERA_WEB = Path(__file__).resolve().parent / "ComfyUI/custom_nodes/3d-Camera-control-H3-Minimax/web"
DEFAULT_CAMERA = {
    "trajectory": json.dumps([
        {"time": 0, "azimuth": 0, "elevation": 0, "distance": 1},
        {"time": 1, "azimuth": 45, "elevation": 0, "distance": 1},
    ]),
    "frames": 124,
    "image_url": "",
}

EDITOR_JS = """
(async () => {
  const {createCameraEditor} = await import(MODULE_URL);
  const {installLanguage} = await import(LANGUAGE_URL);
  const mount = element.querySelector('.camera-editor-mount');
  let editor;
  const update = data => { props.value = {...props.value, ...data}; };
  editor = createCameraEditor({
    read: () => props.value.trajectory,
    write: trajectory => update({trajectory}),
    duration: () => (props.value.frames - 1) / 24,
    setDuration: frames => { update({frames}); editor?.sync(); },
    interpolation: () => 'smooth',
    linkedImage: () => props.value.image_url || '',
    elevationRange: () => 30,
    frameMode: () => 'Freeze Frame',
    loopClosure: () => 'auto',
    promptDetail: () => 'v15 baseline',
    runtimeTask: () => 'scene coverage | camera path',
  });
  mount.append(editor.element);
  // This tab uses one uploaded image and the FL2VA scene-anchor encoder.
  editor.element.querySelector('[aria-label="Modo de referência / Reference mode"]').disabled = true;
  editor.element.querySelector('[data-action="image"]').hidden = true;
  installLanguage(editor.element, () => 'English', () => {});
  watch('value', () => editor.sync());
})().catch(error => { element.querySelector('.camera-editor-mount').textContent = '3D 編輯器載入失敗：' + error.message; });
""".replace("MODULE_URL", json.dumps("/gradio_api/file=" + CAMERA_WEB.as_posix() + "/panel.js")).replace(
    "LANGUAGE_URL", json.dumps("/gradio_api/file=" + CAMERA_WEB.as_posix() + "/language.js"))


def update_camera_image(image_path, state):
    return {**state, "image_url": "/gradio_api/file=" + quote(image_path.replace("\\", "/"), safe="/:") if image_path else ""}


def apply_camera_graph(graph, state, instruction, width, height):
    profiles = {124: "124 frames (~5.17s)", 243: "243 frames (~10.13s)", 362: "362 frames (~15.08s)"}
    frames = int(state["frames"])
    if frames not in profiles:
        raise ValueError("攝影機片長必須為 124、243 或 362 幀。")
    graph["50"] = {"class_type": "BruxosH3Camera", "inputs": {
        "camera_trajectory": state["trajectory"], "profile": profiles[frames],
        "interpolation": "smooth", "instruction": instruction,
        "reference_image": ["10", 0], "ui_language": "English",
        "frame_mode": "Freeze Frame", "loop_closure": "auto",
        "orbit_direction": "invert H3 orbit",
        "elevation_range": "+/-30", "experiment_mode": "Off",
    }}
    graph["7"] = {"class_type": "TextEncodeH3Edit", "inputs": {
        "clip": ["2", 0], "vae": ["3", 0], "source_image": ["10", 0],
        "prompt": instruction, "compiled_prompt": ["50", 0], "options": ["50", 1],
        "primary_image_role": "edit | strong scene anchor (FL2VA)",
        "reference_mode": "none (source only)", "width": width, "height": height,
        "source_fit": "crop center", "prompt_mode": "directed | frozen scene coverage",
        "semantic_resolution": 1024, "native_reference_size": "match output area",
    }}
    graph["40"]["inputs"]["fps"] = ["50", 6]
    graph["41"]["inputs"]["filename_prefix"] = "video/H3_Camera_Q4"
    return graph
