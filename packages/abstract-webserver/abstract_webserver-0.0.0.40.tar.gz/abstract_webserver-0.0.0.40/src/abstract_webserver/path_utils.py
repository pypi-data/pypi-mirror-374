import glob,os,json
from abstract_utilities import *
from pathlib import Path
from io import BytesIO
from abstract_utilities.path_utils import get_files
from .serverManager import *
def get_server_mgr(src_dir=None,domain=None,imgs_dir=None,fb_id=None,directory=None):
    server_mgr = serverManager(src_dir=src_dir,domain=domain,imgs_dir=imgs_dir,fb_id=fb_id,directory=directory)
    return server_mgr
def get_abs_path():
    return os.path.abspath(__file__)
def get_abs_dir():
    abs_path = get_abs_path()
    return os.path.dirname(abs_path)
def get_sections_dir():
    return 'collect_media/sections'
def get_src_directory():
    return get_server_mgr().src_dir
def get_base_directory():
    return os.path.dirname(get_src_directory())
def get_imgs_directory():
    return get_server_mgr().imgs_dir
def get_main_directory():
    return get_server_mgr().imgs_dir
def get_json_directory():
    server_mgr = get_server_mgr()
    return server_mgr.json_dir
def get_json_directories():
    return get_dir_paths(get_json_directory())
def get_directory_links():
    server_mgr = get_server_mgr()
    return server_mgr.directory_links
def get_dir_paths(directory):
    json_dirs = [os.path.join(directory,item) for item in os.listdir(directory)]
    json_dirs = [json_dir for json_dir in json_dirs if os.path.isdir(json_dir)]
    return json_dirs
def get_data(file_path):
    return safe_read_from_json(file_path)
def consolidate_media(file_path):
    data = safe_read_from_json(file_path)
    data = get_new_media(data)
    safe_dump_to_file(data,file_path)
    return data
def get_json_data(file_path):
    json_contents = safe_read_from_json(file_path)
    if not json_contents:
        return 
    return json_contents
def get_all_json_paths(directory):
    json_paths = glob.glob(os.path.join(directory, '**', '*.json'), recursive=True)
    return json_paths
def combine_media(media,media_2):
    for key,value in media.items():
        media[key] = check_value(value) or check_value(media_2.get(key))
    return media
def find_all_files_with_substring(substr, directory=None):
    base_dir = Path(directory) if directory else Path.cwd()
    return [path for path in base_dir.rglob('*') if os.path.isfile(str(path)) and substr in os.path.basename(str(path))]

def create_source_dirs():
    json_directories = get_json_directories()
    for json_directory in json_directories:
        basename = os.path.basename(json_directory)
        filename,ext = os.path.splitext(basename)
        source_dir = os.path.join(get_sections_dir(),filename)
        os.makedirs(source_dir,exist_ok=True)
        all_medias = get_all_medias(json_directory)
        all_keywords = get_all_keywords(json_directory)
        sources_json = os.path.join(source_dir,'sources.json')
        if not os.path.isfile(sources_json):
            safe_dump_to_file([],sources_json)
        sources_data =safe_read_from_json(sources_json)
        images_json = os.path.join(source_dir,'images.json')
        if not os.path.isfile(sources_json):
            safe_dump_to_file([],images_json)    
        images_data =safe_read_from_json(images_json)
        keywords_json = os.path.join(source_dir,'keywords.json')
        if not os.path.isfile(keywords_json):
            safe_dump_to_file([],keywords_json)
        images_data,sources_data = consolidate_medias(all_medias,images=images_data,others=sources_data)
        safe_dump_to_file(sources_data,sources_json)
        safe_dump_to_file(images_data,images_json)
def get_dir_link(obj_path,directory_links=None,get_urls=False):
    best_route = None
    directory_links = directory_links  or get_directory_links()
    paths = []
    key = 'link'
    swap = 'directory'
    if get_urls:
        key = 'directory'
        swap = 'link'
        if obj_path.startswith('http'):
            return obj_path
    else:
        if os.path.exists(obj_path):
            return obj_path
        
    for typ,values in directory_links.items():
        obj_str = values.get(key)
        obj_str = str(obj_str)
        if obj_str in obj_path:
            if best_route == None or not is_directory_in_paths(best_route.get(key),obj_str):
                best_route = values
    if best_route:
        obj_link = obj_path.replace(best_route.get(key),best_route.get(swap))
        return obj_link
def get_dir_links(obj_paths,directory_links=None,get_urls=True):
    return [get_dir_link(obj_path,directory_links,get_urls=get_urls) for obj_path in make_list(obj_paths)] 

def get_json_partial(partial_path,json_dir = None):
    json_dir = json_dir or get_json_directory()
    return os.path.join(json_dir,partial_path)
    
def get_path_from_directories_js(key,directory_links=None):
    directory_links = directory_links or get_directory_links()
    value = directory_links.get(key.upper())
    if value and isinstance(value,dict):
        value = value.get("directory")
    return value
def get_link_from_directories_js(key,directory_links=None):
    directory_links = directory_links or get_directory_links()
    value = directory_links.get(key.upper())
    if value and isinstance(value,dict):
        value = value.get("link")
    return value

def get_directory(directory,main_dir=None):
    main_dir = main_dir or get_main_directory()
    if directory:
        temp_path = is_path(directory)
        if temp_path:
            return temp_path
        temp_path = get_path_from_directories_js(directory)
        if temp_path:
            return temp_path
        temp_path = is_path(main_dir,directory)
        if temp_path:
            return temp_path
        temp_path = is_path(main_dir,directory)
        if temp_path:
            return temp_path

def is_folder_in_path(file_path,folder_name=None):
    if folder_name == None:
        return False
    dirname = os.path.dirname(file_path)
    folder_name_lower = folder_name.lower()
    dirnames = [dirname.lower() for dirname in dirname.split('/') if dirname]
    if folder_name_lower in dirnames:
        return True
    return False
def if_string_ls_in_string(string_list,string):
    string_list = make_list(string_list)
    for string_ls in string_list:
        if string_ls not in string:
            return False
    return True
def is_string_in_file_path(file_path,string=None):
    if string == None:
        return False
    string_list = [stri.lower() for stri in make_list(string)]
    paths = [path.lower() for path in file_path.split('/') if path and if_string_ls_in_string(string_list,path.lower())]
    if paths:
        return True
    return False
def if_get_dirnames(file_path,get_dirnames=False):
    if get_dirnames:
        file_path = os.path.dirname(file_path)
    return file_path
def get_path_item_from_text(root_directory,specific_strings=None,exclude_folder=None,ext=None,recursive=True,get_urls=False,get_dirnames=True):
    ext = eatAll(ext or 'pdf','.')
    root_directory = get_directory(root_directory)
    matching_files = glob.glob(os.path.join(root_directory, '**', f'*.{ext}'), recursive=recursive)
    # Filter by including specific_string and excluding any path containing exclude_folder
    if matching_files:
        if specific_strings and exclude_folder:
            matching_files = [if_get_dirnames(file,get_dirnames=get_dirnames) for file in matching_files if is_string_in_file_path(file,string=specific_strings) and not is_folder_in_path(file,folder_name=exclude_folder)]
        elif specific_strings:
            matching_files = [if_get_dirnames(file,get_dirnames=get_dirnames) for file in matching_files if is_string_in_file_path(file,string=specific_strings)]
        elif exclude_folder:
            matching_files = [if_get_dirnames(file,get_dirnames=get_dirnames) for file in matching_files if not is_folder_in_path(file,folder_name=exclude_folder)]
    matching_files = get_dir_links(matching_files,get_urls=get_urls)
    return matching_files
