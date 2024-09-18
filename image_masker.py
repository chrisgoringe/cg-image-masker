from nodes import PreviewImage, LoadImage
import os, time
from comfy.model_management import InterruptProcessingException

from server import PromptServer
from aiohttp import web

routes = PromptServer.instance.routes
@routes.post('/upload_mask')
async def upload_mask(request):
    post = await request.post()
    ImageMasker.receive_mask(post.get("id"), post.get("message"), post.get('data',None))
    return web.json_response({})

class ImageMasker(PreviewImage, LoadImage):
    @classmethod
    def INPUT_TYPES(s):
        return {"required":{"image": ("IMAGE", {})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},}

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "func"
    OUTPUT_NODE = False
    CATEGORY = "image"

    CANCEL = False
    mask_ready = {}

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("NaN")
    
    @classmethod
    def VALIDATE_INPUTS(s, image):
        return True
    
    @classmethod
    def receive_mask(cls, unique_id, message, data):
        if message=='cancel':
            cls.CANCEL = True
        elif message=='mask_uploaded':
            cls.mask_ready[unique_id] = message

    def func(self, image, unique_id, **kwargs):
        ImageMasker.CANCEL = False

        # save the image (preview image code)
        r = self.save_images(images=image, **kwargs) 

        # send url
        PromptServer.instance.send_sync("image-masker-image", {"id": unique_id, "urls":r['ui']['images']})
        
        # wait to be told it has been uploaded
        while (unique_id not in ImageMasker.mask_ready and not ImageMasker.CANCEL): 
            time.sleep(1)
        if ImageMasker.CANCEL: 
            raise InterruptProcessingException()

        ImageMasker.mask_ready.pop(unique_id)

        # The image file should have been updated...
        return self.load_image(os.path.join(r['ui']['images']['subfolder'], r['ui']['images']['filename']))