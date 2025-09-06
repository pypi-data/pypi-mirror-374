from abstract_webtools import *
from abstract_ocr import download_pdf
from io import BytesIO
def get_content(soup, tag, attr_name, attr_values, content_key):
    """Extract content from a BeautifulSoup object based on tag and attributes."""
    if not soup:
        return None
    # Ensure attr_values is a list or single value
    attr_values = make_list(attr_values)
    for value in attr_values:
        # Find all tags matching the criteria
        elements = soup.find_all(tag, {attr_name: value})
        for element in elements:
            content = element.get(content_key)
            if content:
                return content
    return None
def analyze_text_for_keywords(soup: str, keywords: List[str], lines_per_section: int = 5):
    keywords = break_down_keywords(keywords)
    text = soup.text
    lines=[]
    # Split into individual lines
    if text:
        lines = text.replace('.','.\n').replace('\n\n','\n').split('\n')
        if not lines:
            return "", 0
    # Group lines into sections
    sections = []
    for i in range(0, len(lines), lines_per_section):
        section = '\n'.join(lines[i:i + lines_per_section])
        sections.append(section)

    def count_keywords(section: str) -> int:
        section_lower = section.lower()
        return sum(section_lower.count(kw) for kw in keywords)
    max_count = 0
    max_section_index = 0
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        count = count_keywords(section)
        if count > max_count:
            max_count = count
            max_section_index = i

    if max_count == 0:
        return "", 0
    section_text = sections[max_section_index].strip()
    return section_text
def break_down_keyword(keyword):
    all_key_words = [keyword]
    if '-' in keyword:
        all_key_words.append(keyword.replace('-',''))
        all_key_words+=keyword.split('-')
    return all_key_words
def break_down_keywords(keywords):
    all_key_words=[]
    keywords = keywords or []
    if isinstance(keywords,str):
        keywords = [eatAll(keyword,[' ']) for keyword in keywords.splir(',') if keyword]
    for keyword in keywords:
        keyword_breakdown = break_down_keyword(keyword)
        keyword_break = make_list(keyword_breakdown)
        all_key_words+=keyword_break
    all_key_words = list(set(make_list(all_key_words)))
    return all_key_words
def create_keys(titles):
    keywords = []
    for title in titles:
        keywords+=title.split(' ')
    keywords = list(set(keywords))
    all_valid = list('abcdefghijklmnopqrstuvwxyz1234567890'+'abcdefghijklmnopqrstuvwxyz'.upper())
    invalid = ['and','the','of','at']
    all_new_words = []
    for word in keywords:
        chars = ''
        for char in word:
            if char not in all_valid:
                char = ' '
            chars+=char
        chars_spl = chars.split(' ')
        chars = [char for char in chars_spl if char and char.lower() not in invalid] 
        all_new_words+=chars
    return all_new_words
def url_in_sources(media,sources):
    url = media.get('url')
    for i,source in enumerate(sources):
        source_url = source.get('url')
        if url == source_url:
            for key,value in media.items():
                sources[i][key] = source.get(key,value) or value
            return sources
    sources.append(media)
    return sources
def get_all_keywords(directory):
    list_dir = os.listdir(directory)
    all_jsons = get_all_json_paths(directory)
    all_keywords = []
    for file_path in all_jsons:
        if not file_path.endswith('sources.json') and not file_path.endswith('images.json'):
            json_data = get_json_data(file_path)
            keywords = json_data.get('keywords') or json_data.get('keywords_str') or []
            if isinstance(keywords,str):
                keywords = [eatAll(keyword,[' ','\n','\t','#',',']) for keyword in keywords.split(',') if keyword]
            all_keywords+=keywords
    return all_keywords
def get_phrase(soup,string):
    soup = soup.find_all('head')
    text = str(soup)
    targets = []
    string_lower = string.lower()
    lines = text.replace('\n',' ').replace('> <','><').split('><')
    for line in lines:
        line_lower = line.lower()
        if string_lower in line_lower:
            target_text = ''
            if '>' in line_lower:
                target_text = line.split('>')[1].split('<')[0]
            elif '=' in line_lower:
                target_text = line.split(string)[0].split('=')[1].split(' ')
                target_text = ' '.join(target_text[:-1])
            if target_text:
                target_text = eatAll(target_text,[' ','\t','\n','',"'",'"'])
                targets.append(target_text)
    return list(set(targets))
def get_youtube_info(url):
    info = downloadvideo(url)
    return info
