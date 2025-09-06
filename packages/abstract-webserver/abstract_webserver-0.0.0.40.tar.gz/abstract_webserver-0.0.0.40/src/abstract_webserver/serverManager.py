from .abstract_types import *
from typing import *
from abstract_utilities import *
import json
from pathlib import Path
def dirname_to_it(string,directory):
    if string in directory:
        while True:
            basename = os.path.basename(directory)
            if string in basename:
                return directory
            prior_dir = directory
            directory = os.path.dirname(directory)
            if directory == prior_dir:
                return
            print(directory)
def is_valid_path(path: Path):
    # Exclude paths that start with the GVFS mount point
    if str(path).startswith("/run/user/1000/gvfs/"):
        return False
    try:
        return path.is_dir()
    except OSError:
        return False
def find_spec_dir(substr='src', directory=None):
    """
    Searches for a directory whose name contains `substr` by first checking
    the given directory and its ancestors. If not found, recursively searches
    within the directory tree.
    """
    base_dir = Path(directory) if directory else Path.cwd()
    
    # Check the base directory and its parents
    for parent in [base_dir] + list(base_dir.parents):
        if substr in parent.name:
            return parent
    
    # If not found, search recursively in the directory tree
    for path in base_dir.rglob('*'):
        if is_valid_path(path) and substr in path.name:
            return path
    return None
def find_src_dir(directory=None,substr=None):
    substr = substr or "src"
    src_dir = find_spec_dir(substr=substr, directory=directory)
    return src_dir

def get_main_dir(directory=None,substr=None):
    src_dir = find_src_dir(directory=directory)
    main_dir = os.path.dirname(src_dir)
    return main_dir

def get_build_dir(directory=None,substr=None):
    substr = substr or 'build'
    main_dir = get_main_dir(directory=directory)
    build_dir = find_spec_dir(substr=substr, directory=main_dir)
    return build_dir

def get_static_dir(directory=None,substr=None):
    substr = substr or 'static'
    main_dir = get_main_dir(directory=directory)
    static_dir = find_spec_dir(substr=substr, directory=main_dir)
    return static_dir

def get_public_dir(directory=None,substr=None):
    substr = substr or "public"
    main_dir = get_main_dir(directory=directory)
    public_dir = find_spec_dir(substr=substr, directory=main_dir)
    return public_dir

def get_pages_dir(directory=None,substr=None):
    substr = substr or 'pages'
    main_dir = get_main_dir(directory=directory)
    pages_dir = find_spec_dir(substr=substr, directory=main_dir)
    return pages_dir

def get_json_dir(directory=None,substr=None):
    substr = substr or 'json_pages'
    src_dir = find_src_dir(directory=None)
    json_dir = find_spec_dir(substr=substr, directory=src_dir)
    return json_dir

def get_contents_dir(directory=None,substr=None):
    substr = substr or 'contents'
    src_dir = find_src_dir(directory=None)
    contents_dir = find_spec_dir(substr=substr, directory=src_dir)
    return contents_dir

def get_imgs_dir(directory=None,substr=None):
    substr = substr or 'imgs'
    public_dir = get_public_dir(directory=directory)
    imgs_dir = find_spec_dir(substr=substr, directory=public_dir)
    return imgs_dir

def get_page_layout_dir(directory=None,substr=None):
    substr = substr or '_page_layouts'
    pages_dir = get_pages_dir(directory=directory)
    page_layout_dir = find_spec_dir(substr=substr, directory=pages_dir)
    return page_layout_dir

def get_domain(directory=None,substr=None):
    directory = get_main_dir(directory=directory)
    domain  = os.path.basename(directory)
    domain,ext = os.path.splitext(domain)
    if not domain.startswith('http'):
        domain = f'https://{domain}'
    domain = f'{domain}{ext or ".com"}'
    return domain



def get_page_layout_path(directory=None,filename=None):
    layout_filename = filename or 'main_layout'
    page_layouts_dir = get_page_layout_dir(directory=directory)
    files = []
    for basename in os.listdir(page_layouts_dir):
        filename,ext = os.path.splitext(basename)
        file_path = os.path.join(page_layouts_dir,basename)
        if os.path.isfile(file_path):
            files.append(file_path)
            if layout_filename == filename:
                return file_path
    if files:
        return files[0]
def get_domain_dirs(function,dir_str=None,directory=None):
    if dir_str and os.path.isdir(dir_str):
        return dir_str
    return function(substr=dir_str, directory=directory)
def make_directory_links(directory,domain=None,directory_links=None):
    domain = domain or get_domain_from_src(directory=directory)
    directory_links = directory_links or {}
    for item in os.listdir(directory):
        if directory_links.get(item) == None:
            dir_path = os.path.join(directory,item)
            if os.path.isdir(dir_path):
                link = os.path.join(domain,item)
                directory_links[item]={"directory":dir_path,"link":link}
    return directory_links

def create_directory_links(public_dir=None,pages_dir=None,json_dir=None,domain=None,main_dir=None,src_dir=None,static_dir=None,contents_dir=None,directory_links=None):
    src_dir = get_domain_dirs(find_src_dir,dir_str=src_dir,directory=main_dir)
    main_dir =get_domain_dirs(get_main_dir,dir_str=main_dir,directory=src_dir)
    static_dir = get_domain_dirs(get_static_dir,dir_str=static_dir,directory=src_dir)
    public_dir = get_domain_dirs(get_public_dir,dir_str=public_dir,directory=main_dir)
    pages_dir = get_domain_dirs(get_pages_dir,dir_str=pages_dir,directory=src_dir)
    json_dir = get_domain_dirs(get_json_dir,dir_str=json_dir,directory=main_dir)
    contents_dir = get_domain_dirs(get_contents_dir,dir_str=contents_dir,directory=src_dir)
    domain = domain or get_domain_dirs(get_domain,dir_str=domain,directory=src_dir)
    directory_links= directory_links or {}
    if pages_dir and directory_links.get("pages") == None:
        directory_links["pages"] = {"directory":pages_dir,"link":domain}
    if json_dir and directory_links.get("directory") == None:
        directory_links["json"] = {"directory":json_dir,"link":domain}
    if contents_dir and directory_links.get("contents") == None:
        directory_links["contents"] = {"directory":contents_dir,"link":domain}
    if public_dir:
        directory_links = make_directory_links(public_dir,domain=domain,directory_links=directory_links)
    if static_dir:
        directory_links = make_directory_links(static_dir,domain=domain,directory_links=directory_links)
    return directory_links

class serverManager(metaclass=SingletonMeta):
    def __init__(self, src_dir=None,main_dir=None,domain=None,static_dir=None,imgs_dir=None,build_dir=None,pages_dir=None,json_dir=None,contents_dir=None,public_dir=None,fb_id=None,directory=None,directory_links=None,page_layout_dir=None,layout_filename=None):
        """Initialize the file directory manager with base paths."""
        self.src_dir = get_domain_dirs(find_src_dir,dir_str=src_dir,directory=src_dir)
        self.main_dir = get_domain_dirs(get_main_dir,dir_str=main_dir,directory=self.src_dir)
        self.build_dir = get_domain_dirs(get_build_dir,dir_str=build_dir,directory=self.src_dir)
        self.static_dir = get_domain_dirs(get_static_dir,dir_str=static_dir,directory=self.src_dir)
        self.public_dir = get_domain_dirs(get_public_dir,dir_str=public_dir,directory=self.src_dir)
        self.imgs_dir = get_domain_dirs(get_imgs_dir,dir_str=imgs_dir,directory=self.src_dir)
        self.pages_dir = get_domain_dirs(get_pages_dir,dir_str=pages_dir,directory=self.src_dir)
        self.json_dir = get_domain_dirs(get_json_dir,dir_str=json_dir,directory=self.src_dir)
        self.contents_dir = get_domain_dirs(get_contents_dir,dir_str=contents_dir,directory=self.src_dir)
        self.page_layout_dir = get_domain_dirs(get_page_layout_dir,dir_str=page_layout_dir,directory=self.src_dir)
        self.domain = domain or get_domain_dirs(get_domain,dir_str=domain,directory=self.src_dir)
        self.fb_id = fb_id
        self.ensure_directories()
        self.directory_links = create_directory_links(
            public_dir=self.public_dir,
            pages_dir=self.pages_dir,
            domain=self.domain,
            main_dir = self.main_dir,
            json_dir = self.json_dir,
            directory_links=directory_links or {}
            )
        self.page_layout_path=None
        if self.page_layout_dir:
            self.page_layout_path=get_page_layout_path(directory=self.page_layout_dir,filename=layout_filename)
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.pages_dir, self.json_dir, self.contents_dir, self.public_dir]:
            if directory:
                os.makedirs(directory, exist_ok=True)

    def join_path(self, *paths: str) -> str:
        """Join multiple path segments into a single path."""
        return os.path.join(*paths)

    def get_file_paths(self, directory: str, filename: str, is_index: bool = False) -> Tuple[str, str, str]:
        """Generate paths for JSON, page, and content files based on directory and filename."""
        json_path = self.join_path(self.json_dir, directory, f"{filename}.json") if directory else self.join_path(self.json_dir, f"{filename}.json")
        pages_path = self.join_path(self.pages_dir, "home", f"{filename}.tsx") if is_index else self.join_path(self.pages_dir, directory, f"{filename}.tsx")
        contents_path = self.join_path(self.contents_dir, directory, f"{filename}.md") if directory else self.join_path(self.contents_dir, f"{filename}.md")
        return json_path, pages_path, contents_path

    def read_json(self, json_path: str) -> dict:
        """Read and parse a JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading {json_path}: {e}")
            return {}

    def write_to_file(self, contents: str, file_path: str) -> None:
        """Write contents to a file, creating directories if needed."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contents)

    def extract_content_to_md(self, json_data: dict, contents_path: str) -> Optional[str]:
        """Extract content from JSON and save it as a Markdown file."""
        content = json_data.get("content")
        if not content:
            print(f"No content found in JSON for {contents_path}")
            return None
        self.write_to_file(content.strip(), contents_path)
        return contents_path

    def update_json(self, json_path: str, content_file: str) -> None:
        """Update JSON to reference the content file instead of embedding content."""
        json_data = self.read_json(json_path)
        if "content" in json_data:
            del json_data["content"]
            relative_content_path = os.path.relpath(content_file, self.src_dir).replace("\\", "/")
            json_data["content_file"] = relative_content_path
            self.write_to_file(json.dumps(json_data, indent=4), json_path)
    def generate_tsx_template(self, filename: str, directory: str, meta: dict, is_index: bool = False,page_layout_filename=None) -> str:
        """Generate TSX template for a page."""
        
        add_imports = ""
        json_path, pages_path, contents_path = self.get_file_paths(directory, filename, is_index=True)
        pdfViewer = meta.get('pdfViewer') or 'false'
        dirname = os.path.basename(directory) if directory else "home"  # Use 'home' for index
        base_name = filename.replace('-', '_')
        page_name = f"Page_{base_name}" if base_name[0].isdigit() else f"{base_name.capitalize()}Page"
        sources_name = f"{page_name}Sources"
        page_layout_path = get_page_layout_path(directory=self.page_layout_dir,filename=page_layout_filename)
        if page_layout_path:
            page_layout = read_from_file(page_layout_path)
            if page_layout:
                tsx_content = page_layout.format(
                    filename=filename,
                    json_path=json_path,
                    pages_path=pages_path,
                    contents_path=contents_path,
                    dirname=dirname,
                    sources_name=sources_name
                )
                return tsx_content

    def process_directory(self, directory: str) -> None:
        """Process all JSON files in a directory."""
        json_directory = self.join_path(self.json_dir, directory)
        if not os.path.isdir(json_directory):
            print(f"Directory not found: {json_directory}")
            return

        for item in os.listdir(json_directory):
            filename, ext = os.path.splitext(item)
            if ext.lower() != ".json":
                continue

            is_index = (directory == "" and filename == "index")  # Check if it's the root index
            json_path, pages_path, contents_path = self.get_file_paths(directory, filename, is_index)
            json_data = self.read_json(json_path)

            # Extract content to Markdown
            content_file = self.extract_content_to_md(json_data, contents_path)
            if content_file:
                self.update_json(json_path, content_file)
    
            # Generate or update TSX page
            tsx_content = self.generate_tsx_template(filename, directory, json_data, is_index)
            self.write_to_file(tsx_content, pages_path)
            print(f"Processed: {json_path} -> {contents_path}, {pages_path}")

    def process_root_index(self) -> None:
        """Process the root index.json file separately."""
        json_path = self.join_path(self.json_dir, "index.json")
        if not os.path.exists(json_path):
            print(f"Root index.json not found: {json_path}")
            return

        filename = "index"
        directory = ""  # Empty directory for root-level index
        json_data = self.read_json(json_path)
        json_path, pages_path, contents_path = self.get_file_paths(directory, filename, is_index=True)

        # Extract content to Markdown
        content_file = self.extract_content_to_md(json_data, contents_path)
        if content_file:
            self.update_json(json_path, content_file)

        # Generate TSX page at /home/index.tsx
        tsx_content = self.generate_tsx_template(filename, directory, json_data, is_index=True)
        self.write_to_file(tsx_content, pages_path)
        print(f"Processed root index: {json_path} -> {contents_path}, {pages_path}")

    def process_all(self) -> None:
        """Process all directories in json_pages and the root index.json."""
        # Process root index.json first
        self.process_root_index()

        # Process all directories
        for directory in os.listdir(self.json_dir):
            if os.path.isdir(self.join_path(self.json_dir, directory)):
                self.process_directory(directory)
