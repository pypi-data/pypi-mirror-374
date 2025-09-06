from abstract_math import *
from PIL import Image
import requests
import os
from io import BytesIO
from abstract_utilities import *
from .directory_processor import *
def get_image_info_from_path(file_path):
    # Convert string path to Path object
    path = Path(file_path)
    
    # Get file size in bytes
    byte_size = path.stat().st_size
    byte_size = divide_it(byte_size,1000)
    # Get image dimensions
    with Image.open(file_path) as img:
        width, height = img.size
    
    return {
        'kbyte_size': byte_size,
        'width': width,
        'height': height
    }
def get_image_info_from_url(url):
    # Fetch the image from the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request fails
    
    # Get byte size from the content
    kbyte_size = divide_it(len(response.content),1000)
    # Open the image from the bytes data
    img_bytes = io.BytesIO(response.content)
    with Image.open(img_bytes) as img:
        width, height = img.size
    
    return {
        'kbyte_size': kbyte_size ,
        'width': width,
        'height': height
    }
def if_isnumber(file_path):
    dirname = os.path.dirname(file_path)
    og_dirname = dirname
    basename = os.path.basename(file_path)
    filename,ext = os.path.splitext(basename)
    file_name = basename
    while True:
        if is_number(filename):
            filename = os.path.basename(dirname)
            dirname =  os.path.dirname(dirname)
            file_name = f"{filename}_{file_name}"
        else:
            return os.path.join(og_dirname,file_name)
def get_image_path_from_url(url):
    dimensions={}
    file_path = None
    if 'imgs/' in url:
        og_file_path = os.path.join(get_imgs_dir(),url.split('imgs/')[-1])
    else:
        og_file_path = url.split('thedailydialectics.com')[-1]
        path_parts = [path for path in os.path.split('/')[0] if path]
        basename = os.path.basename(og_file_path)
        filename,ext = os.path.splitext(basename)
        
        file_path = find_all_files_with_substring(filename, directory=get_imgs_dir())
    file_path = file_path or og_file_path
    
    if not os.path.isfile(og_file_path):
        dirname = os.path.dirname(og_file_path)
        basename = os.path.basename(og_file_path)
        filename,ext = os.path.splitext(basename)
        if os.path.isdir(dirname):
            for filename in os.listdir(dirname):
                filename_comp,ext_comp = os.path.splitext(basename)
                if filename == filename_comp:
                    
                    file_path = os.path.join(dirname,basename)
                    return file_path
    if os.path.isfile(file_path):
        return file_path
def get_image_info(media,file_path=None,url=None):
    if file_path== None:
        url = url or media.get('href') or media.get('url') or media.get('thumbnail')
        file_path = get_image_path_from_url(url)
    dimensions={}
    file_path = file_path or get_image_path_from_url(url)
    if file_path:
        dimensions = get_image_info_from_path(file_path)
    else:
        dimensions = get_image_info_from_url(url)
    prev_file_path = file_path
    file_path = if_isnumber(prev_file_path)
    basename = os.path.basename(file_path)
    filename,ext = os.path.splitext(basename)
    if not ext in image_exts:
        return 
    url = f'https://thedailydialectics.com/imgs{file_path.split("imgs")[-1]}'
    alt = media.get('alt') or filename or basename
    description = media.get('description') or filename
    caption = media.get('caption') or description or filename
    shutil.copy(prev_file_path,file_path)
    title = media.get('title') or alt or filename
    keywords = ','.join(media.get('keywords') or []).replace('True','') or ','.join(filename.replace('-','_').split('_'))
    image_info = {
        "alt": alt,
        "caption": caption,
        "keywords_str":keywords ,
        "filename": filename,
        "file_path":file_path,
        "ext": ext,
        "title": title,
        "dimensions": {
            "width": dimensions.get('width'),
            "height": dimensions.get('height'),
        },
        "file_size": dimensions.get('kbyte_size'),
        "license": "CC BY-SA 4.0",
        "attribution": "Created by thedailydialectics for educational purposes",
        "longdesc": description,
        "schema": {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "name": title,
            "description": description,
            "url": url,
            "contentUrl": url,
            "width": dimensions.get('width'),
            "height": dimensions.get('height'),
            "license": "https://creativecommons.org/licenses/by-sa/4.0/",
            "creator": {
                "@type": "Organization",
                "name": "thedailydialectics"
            },
            "datePublished": "2025-03-30"
        },
        "social_meta": {
            "og:image": url,
            "og:image:alt": alt,
            "twitter:card": "summary_large_image",
            "twitter:image": url
        }
    }
    return image_info
def get_image_json(image_info, section=None):
    """
    Copy or download an image to a section directory and save its metadata as JSON.
    
    Args:
        image_info (dict): Dictionary with image metadata (url, filename, etc.).
        section (str, optional): Subdirectory under imgs (e.g., "sommerfeld-goubau").
    """
    try:
        # Base directory for images
        section_dir = get_imgs_dir()  # e.g., '/var/www/thedailydialectics/public/imgs'
        if section:
            section_dir = os.path.join(section_dir, section)
            os.makedirs(section_dir, exist_ok=True)
        
        # Get URL and original file path
        url = image_info.get('url')
        og_file_path = get_image_path_from_url(url) if url else None
        
        # Determine basename, filename, and extension
        basename = image_info.get('basename') or (os.path.basename(og_file_path) if og_file_path else os.path.basename(url))
        filename = image_info.get('filename') or os.path.splitext(basename)[0]
        ext = image_info.get('ext') or os.path.splitext(basename)[-1]
        
        # Contextualize numeric filenames
        filename = if_isnumber(og_file_path)
        
        # Create image directory and file path
        image_dir = os.path.join(section_dir, filename)
        os.makedirs(image_dir, exist_ok=True)
        
        basename = f"{filename}{ext}"
        image_file_path = os.path.join(image_dir, basename)
        
        # Copy or download the image
        if og_file_path and os.path.isfile(og_file_path) and not os.path.isfile(image_file_path):
            shutil.copy(og_file_path, image_file_path)
            print(f"Copied: {og_file_path} -> {image_file_path}")
        elif url and not os.path.isfile(image_file_path):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(image_file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {url} -> {image_file_path}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}: {e}")
                return
        
        # Generate and save image info JSON
        image_info_path = os.path.join(image_dir, 'info.json')
        image_info = get_image_info(image_info, image_file_path, url) or image_info
        safe_dump_to_file(image_info, image_info_path)
        
        # Process the directory (resize to WebP)
        process_directory(image_dir)
        return image_dir
    except Exception as e:
        print(f"Failed to process {image_info.get('url', 'unknown URL')}: {e}")
    
