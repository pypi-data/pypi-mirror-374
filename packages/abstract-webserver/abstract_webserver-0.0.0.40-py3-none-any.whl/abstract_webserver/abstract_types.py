from abstract_utilities import *
from io import BytesIO
from abstract_utilities.type_utils import get_media_exts
remove=["is_web_link","is_video","is_spreadsheet","is_presentation","is_media","is_image","is_document","is_audio","image"]
obj = {"url":["og_url","original","url","href","URL"],
       "path":["file_path"],
       "title":["title"],
       "description":["description"],
       "keywords":["keywords"],
       "caption":["caption"],
       "alt":["alt"]}

TARGET_WIDTH = 1200
TARGET_HEIGHT = 627
image_exts = get_media_exts(types='image')
def var_clean(obj):
    return eatAll(obj,[' ','"',"'",'“','” ','`'])
def get_only_type(list_objs,types):
    keeps = []
    exts = get_media_exts.get(types)
    for list_obj in list_objs:
        for ext in exts:
            if list_obj.endswith(ext):
                keeps.append(list_obj)
    return keeps
import os
def check_value(value):
    if value in ['True','False','None',None,True,False,'None','True','false',['True'],['False'],['None'],[True],[None],[False]]:
        value = None
    return value
def add_to_gone_list(url):
    return 
    gone_list_path = get_gone_list_path()
    data = safe_read_from_json(gone_list_path)
    if url and url not in data:
        data.append(url)
        safe_dump_to_file(data,gone_list_path)

def get_all_medias(directory):
    list_dir = os.listdir(directory)
    all_jsons = get_all_json_paths(directory)
    all_medias = []
    for file_path in all_jsons:
        if not file_path.endswith('sources.json') and not file_path.endswith('images.json'):
            json_data = get_json_data(file_path)
            all_medias+=json_data.get('media')
    return all_medias
def get_images_others(media,images,others):
    url = media.get('url')
    if url:
        basename= os.path.basename(url)
        filename, ext = os.path.splitext(basename)
        if ext.lower() in image_exts:
            images = url_in_sources(media,images)
        else:
            others = url_in_sources(media,others)
    return images,others
def consolidate_medias(all_medias,images=None,others=None):
    images = images or []
    others=others or []
    for medias in all_medias:
        if isinstance(medias,list):
            for media in medias:    
               images,others = get_images_others(media,images,others)
        else:
            images,others = get_images_others(medias,images,others)
    return images,others
