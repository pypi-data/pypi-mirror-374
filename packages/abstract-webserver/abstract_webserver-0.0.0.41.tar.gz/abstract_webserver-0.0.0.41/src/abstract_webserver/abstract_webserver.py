last_url = 'http://www.emediapress.com/go.php?offer=qiman&pid=36'
def get_consolidated_data(datas,all_keywords,consolidated_path,last_url_found = False):
    for j,data in enumerate(datas):
        og_data = data.copy()
        types = data.get('type')
        if types != 'image':
            url = data.get('url')
            if last_url_found == False and url == last_url:
                last_url_found=True
            if last_url_found == True:
                if "thedailydialectics" not in url:
                    if 'youtube' in url:
                        try:
                            if 'channel' not in url:
                                youtube_info = get_youtube_info(url)
                                print(youtube_info)
                        except:
                            print(f"bad youtube url {url}")
                    else:
                        try:
                            soup = soupManager(url).soup
                            try:
                                url_pieces = url_mgr.url_to_pieces(url)
                                protocol = url_pieces[0]
                                domain = url_pieces[1]
                                domain = f"{protocol}://{domain}"
                            except:
                                print(f"no url domain for {url}")
                            i=0
                            titles = get_phrase(soup,'title')
                            for title in titles:
                                i+=1
                                if i ==2:
                                    break
                            titles = titles[:i]
                            keywords = create_keys(titles) or []
                            icon = get_phrase(soup,'icon')
                            icon+=make_list(get_phrase(soup,'image') or [])
                            icon = get_only_type(icon,'image')
                            icons = [f"{domain}{ico}" if ico.startswith('/') else ico for ico in icon if ico]
                            description2 = get_phrase(soup,'description')
                            description = analyze_text_for_keywords(soup, all_keywords, 5)
                            js_meta = {"domain":domain,"url":url,"title":titles,"keywords":keywords,"image":icons,"description":description,"description2":description2}
                            combine_media(data,js_meta)
                            datas[j] = combine_media(datas[j],og_data)
                            safe_dump_to_file(datas,consolidated_path)
                        except:
                            add_to_gone_list(url)
    return datas,last_url_found
last_url_found = False
def get_media_from_source_dirs(get_urls=False):
    for section_dir in get_dir_paths(get_sections_dir()):
        section = os.path.basename(section_dir)
        images_path = os.path.join(section_dir,'images.json')
        images_datas = safe_read_from_json(images_path)
        for image_data in images_datas:
            get_image_json(image_data,section=section)
        if get_urls:
            if 'space' not in section_dir:
                sources_path = os.path.join(section_dir,'sources.json')
                keywords_path = os.path.join(section_dir,'keywords.json')
                sources_data = safe_read_from_json(sources_path)
                keywords = safe_read_from_json(keywords_path)
                sources_data,last_url_found = get_consolidated_data(sources_data,keywords,sources_path,last_url_found)
