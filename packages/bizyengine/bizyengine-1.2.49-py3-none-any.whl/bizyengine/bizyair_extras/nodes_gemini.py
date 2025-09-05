import base64
import io
import json
import re

import numpy as np
import torch
from comfy_api_nodes.apinode_utils import tensor_to_base64_string
from PIL import Image, ImageOps

from bizyengine.core import BizyAirBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS


# Tensor to PIL
def tensor_to_pil(image):
    return Image.fromarray(
        np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8)
    )


def image_to_base64(pil_image, pnginfo=None):
    # 创建一个BytesIO对象，用于临时存储图像数据
    image_data = io.BytesIO()

    # 将图像保存到BytesIO对象中，格式为PNG
    pil_image.save(image_data, format="PNG", pnginfo=pnginfo)

    # 将BytesIO对象的内容转换为字节串
    image_data_bytes = image_data.getvalue()

    # 将图像数据编码为Base64字符串
    encoded_image = "data:image/png;base64," + base64.b64encode(
        image_data_bytes
    ).decode("utf-8")

    return encoded_image


def base64_to_image(base64_string):
    # 去除前缀
    base64_list = base64_string.split(",", 1)
    if len(base64_list) == 2:
        prefix, base64_data = base64_list
    else:
        base64_data = base64_list[0]

    # 从base64字符串中解码图像数据
    image_data = base64.b64decode(base64_data)

    # 创建一个内存流对象
    image_stream = io.BytesIO(image_data)

    # 使用PIL的Image模块打开图像数据
    image = Image.open(image_stream)

    return image


class NanoBanana(BizyAirBaseNode):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "temperature": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "top_p": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "max_tokens": ("INT", {"default": 8192, "min": 1, "max": 8192}),
            },
            "optional": {
                "image": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    OUTPUT_NODE = False
    CATEGORY = "☁️BizyAir/External APIs/Gemini"

    def execute(self, prompt, temperature, top_p, seed, max_tokens, **kwargs):
        url = f"{BIZYAIR_SERVER_ADDRESS}/proxy_inference/VertexAI/gemini-2.5-flash-image-preview"
        extra_data = pop_api_key_and_prompt_id(kwargs)
        parts = [{"text": prompt}]
        for _, img in enumerate(
            [
                kwargs.get("image", None),
                kwargs.get("image2", None),
                kwargs.get("image3", None),
                kwargs.get("image4", None),
                kwargs.get("image5", None),
            ],
            1,
        ):
            if img is not None:
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": tensor_to_base64_string(img),
                        }
                    }
                )
        data = {
            "contents": {
                "parts": parts,
                "role": "user",
            },
            "generationConfig": {
                "seed": seed,
                "responseModalities": ["TEXT", "IMAGE"],
                "temperature": temperature,
                "topP": top_p,
                "maxOutputTokens": max_tokens,
            },
        }
        json_payload = json.dumps(data).encode("utf-8")
        headers = client.headers(api_key=extra_data["api_key"])
        headers["X-BIZYAIR-PROMPT-ID"] = extra_data[
            "prompt_id"
        ]  # 额外参数vertexai会拒绝，所以用请求头传
        resp = client.send_request(
            url=url,
            data=json_payload,
            headers=headers,
        )
        # 解析base64图片
        b64_data = None
        for part in resp["candidates"][0]["content"]["parts"]:
            if part.get("inlineData", None):
                b64_data = part["inlineData"]["data"]
                break
        if b64_data:
            i = base64_to_image(b64_data)
            # 下面代码参考LoadImage
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            return (image,)
        else:
            raise ValueError("No image found in response")
