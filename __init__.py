"""
@author: chrisgoringe
@title: Image Masker
@nickname: Image Masker
@description: Custom node that previews a single image and pause the workflow to allow the user to create a mask
"""

from image_masker import ImageMasker

NODE_CLASS_MAPPINGS = {  "Image Masker" : ImageMasker }
WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "WEB_DIRECTORY"]

IP_VERSION = "0.1"
