from importlib.util import find_spec
from pathlib import Path
from typing import Literal

from gradio import Error, Info
from imageio import mimsave
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)
from numpy import asarray, ndarray, transpose
from PIL import Image
from torch import Tensor, from_numpy, load as torch_load
from torchvision.transforms import ToPILImage

from visualizr.anitalker.config import TrainConfig
from visualizr.anitalker.experiment import LitModel
from visualizr.anitalker.face_sr.face_enhancer import enhancer_list
from visualizr.anitalker.templates import ffhq256_autoenc


def check_package_installed(package_name: str) -> bool:
    return find_spec(package_name) is not None


def frames_to_video(
    input_path: Path,
    audio_path: Path,
    output_path: Path,
    fps: int = 25,
) -> None:
    image_files = [input_path / img for img in sorted(input_path.iterdir())]
    clips = [ImageClip(m.as_posix()).set_duration(1 / fps) for m in image_files]
    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    final_video = video.set_audio(audio)
    final_video.write_videofile(
        output_path.as_posix(),
        fps,
        "libx264",
        audio_codec="aac",
    )


def load_image(img_path: Path, size: int) -> ndarray:
    img: Image.Image = Image.open(img_path).convert("RGB")
    img_resized: Image.Image = img.resize((size, size))
    img_np: ndarray = asarray(img_resized)
    img_transposed: ndarray = transpose(img_np, (2, 0, 1))  # 3 x 256 x 256
    return img_transposed / 255.0


def img_preprocessing(img_path: Path, size: int) -> Tensor:
    img_np: ndarray = load_image(img_path, size)  # [0, 1]
    img: Tensor = from_numpy(img_np).unsqueeze(0).float()  # [0, 1]
    normalized_image: Tensor = (img - 0.5) * 2.0  # [-1, 1]
    return normalized_image


def saved_image(img_tensor: Tensor, img_path: Path) -> None:
    pil_image_converter: ToPILImage = ToPILImage()
    img = pil_image_converter(img_tensor.detach().cpu().squeeze(0))
    img.save(img_path)


def remove_frames(frames_path: Path) -> None:
    try:
        for frame in frames_path.iterdir():
            frame.unlink()
            Info(f"Deleted {frame}")
    except OSError as e:
        Error(f"Failed to delete frames: {e}")


def load_stage_2_model(conf: TrainConfig, stage_2_checkpoint_path: Path) -> LitModel:
    Info("Loading stage 2 model")
    if not stage_2_checkpoint_path.exists():
        msg = f"Checkpoint not found: {stage_2_checkpoint_path}"
        raise FileNotFoundError(msg)
    model: LitModel = LitModel(conf)
    try:
        state = torch_load(stage_2_checkpoint_path, map_location="cpu")
    except Exception as e:
        msg = f"Failed to load checkpoint: {e}"
        raise RuntimeError(msg) from e
    model.load_state_dict(state)
    model.ema_model.eval()
    model.ema_model.to("cuda")
    return model


def _init_configuration_param(
    conf: TrainConfig,
    face_location: bool,
    face_scale: bool,
    mfcc: bool,
) -> TrainConfig:
    conf.face_location = face_location
    conf.face_scale = face_scale
    conf.mfcc = mfcc
    return conf


def init_configuration(
    infer_type: Literal[
        "mfcc_full_control",
        "mfcc_pose_only",
        "hubert_pose_only",
        "hubert_audio_only",
        "hubert_full_control",
    ],
    seed: int,
    decoder_layers: int,
    motion_dim: int,
) -> TrainConfig:
    Info("Initializing configuration... ")
    conf: TrainConfig = ffhq256_autoenc()
    conf.seed = seed
    conf.decoder_layers = decoder_layers
    conf.motion_dim = motion_dim
    conf.infer_type = infer_type
    Info(f"infer_type: {infer_type}")
    match infer_type:
        case "mfcc_full_control":
            return _init_configuration_param(conf, True, True, True)
        case "mfcc_pose_only":
            return _init_configuration_param(conf, False, False, True)
        case "hubert_pose_only":
            return _init_configuration_param(conf, False, False, False)
        case "hubert_audio_only":
            return _init_configuration_param(conf, False, False, False)
        case "hubert_full_control":
            return _init_configuration_param(conf, True, True, False)


def super_resolution(
    tmp_predicted_video_512_path: Path,
    predicted_video_256_path: Path,
    predicted_video_512_path: Path,
):
    Info(f"Saving video at {tmp_predicted_video_512_path}")
    mimsave(
        tmp_predicted_video_512_path,
        enhancer_list(
            predicted_video_256_path,
            bg_upsampler=None,
        ),
        fps=25.0,
    )
    # Merge audio and video
    video_clip = VideoFileClip(tmp_predicted_video_512_path.as_posix())
    audio_clip = AudioFileClip(predicted_video_256_path.as_posix())
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(
        predicted_video_512_path.as_posix(),
        codec="libx264",
        audio_codec="aac",
    )
    tmp_predicted_video_512_path.unlink()
