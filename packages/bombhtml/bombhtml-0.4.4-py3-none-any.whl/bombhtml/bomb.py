"""
 Copyright (C) 2025  sophie (itsme@itssophi.ee)

    Double licensed under MIT and GPLv3. See LICENSE_* for more info.
"""

import os
import shutil
import glob
import re
import json
import time
import random
import html

from datetime import datetime, timezone, timedelta

class Build():
    def __init__(self):
        self._source = "./src" 
        self._destination = "./public"
        self.template_prefix = "_._"
        self.regex_placeholder = r"\{\{[^}]*\}\}"
        self.placeholder_elements = ["{", "}"]
        self.no_output = False
        self.pattern_prefix = r"{s{" #the one for doing the thing with templates
        self.pattern_suffix = r"}}"  # filled with data from the json
        self._template_version = "1.0.0"
        self.skip_invalid_placeholders = False
        self.debug_print = False
        self.prefer_1 = True # see where used
        self.templating = True
        self.blog = False
        self.blog_regex = r"\[\[blogposts[^}]*\]\]"
        self.blog_pattern_prefix = "[["
        self.blog_pattern_suffix = "]]"
        self._blog_articles_path = "./blog"
        self._blog_url_path = "/blog/"
        self._blog_template_folder = "./src/_._templates"
        self.blog_date_edited_at_text = " - last edited: "
        self.blog_date_edited_at_text_after = ""
        self.use_unix_epoch = True
        self.timezone_utc_offset_h = 0
        self.timezone_utc_offset_min = 0
        self.use_localtime = False
        self.datetime_double_digits = True
        self.datetime_format = "D.M.Y h:m tz"
        self.blog_preview_char_limit = 500
        self.blog_preview_datetime_format = "D.M.Y"
        self.blog_preview_show_edit = False

    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, sourcee:str):
        self._source = "./" + sourcee.replace("./", "")

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, destinationn:str):
        self._destination = self._property_path_helper(destinationn)

    @property
    def blog_articles_path(self):
        return self._blog_articles_path
    
    @blog_articles_path.setter
    def blog_articles_path(self, blog_articles_pathh:str):
        self._blog_articles_path = self._property_path_helper(blog_articles_pathh)

    @property
    def blog_url_path(self):
        return self._blog_url_path
    
    @blog_url_path.setter
    def blog_url_path(self, blog_url_pathh:str):
        path = "/" + blog_url_pathh.strip("/") + "/"
        if path == "//":
            path = "/"
        self._blog_url_path = path

    @property
    def blog_template_folder(self):
        return self._blog_template_folder
    
    @blog_template_folder.setter
    def blog_template_folder(self, blog_template_folderr:str):
        self._blog_template_folder = self._property_path_helper(blog_template_folderr)

    def _property_path_helper(path:str):
        return "./" + path.strip("/").replace("./", "")

    def start(self):
        if not self.no_output:
            start_time = time.perf_counter() #no point calculating if not shown to user
            print("Building…")

        p = re.compile(self.regex_placeholder)
        
        try:
            shutil.rmtree(self.destination)
        except FileNotFoundError:
            pass #the directory isn't there yet, normal case on first use
        shutil.copytree(self.source, self.destination)

        if self.debug_print:
                print(f"self.prefer_1: {self.prefer_1}")
        if self.prefer_1: #either make all includes first, then the rest
            includes = self._find_includes(self.template_prefix)

            if self.debug_print:
                print(f"\nFound includes: {includes}")
            
            file_paths_wo_includes = self._find_rest_files(includes)

            if self.debug_print:
                print(f"\nFound paths wo includes: {file_paths_wo_includes}")

            # first, it replaces every placholder in the files that should be filled that
            # way, then the rest. This allows faster processing for nested includes as so
            # that the same includes don't get processed twice (in a 1 level nesting).
            self._check_and_replace(includes, p)
            self._check_and_replace(file_paths_wo_includes, p)
        else: #or all at the same time. 
            # Aka either find include files and less regex matching, 
            # or no include file finding and more regex matching
            self._check_and_replace(self._find_all_files(), p)

        if not self.no_output:
            middle_time = time.perf_counter()
            m_execution_time = int((middle_time - start_time)*1000)
            print(f"Placeholer part completed in {m_execution_time}ms")

        
        if self.templating:
        # the templating stuff with the json file to fill data
            blueprints = self._find_blueprints("bombhtml-template")

            for i in blueprints:
                data = self._read_json_file(i)
                if self._template_version != data["version"]:
                    raise ValueError(f"Invalid config version: {data['version']}. Expected: {self._template_version}.")
                path = self.destination +"/" + data["template"].replace("./", "")
                content = data["template-content"]
                new_path = i.replace(".json", "")
                shutil.copyfile(path, new_path)
                for name, value in content.items():
                    with open(new_path, "r") as file_content:
                        new_file_content = file_content.read().replace(self.pattern_prefix + name + self.pattern_suffix, value)
                    with open(new_path, "w") as file_cont:
                        file_cont.write(new_file_content)

                os.remove(i)
        if not self.no_output:
            after_templating_time = time.perf_counter()
            after_templating_execution_time = int((after_templating_time - middle_time)*1000)
            print(f"Templating part completed in {after_templating_execution_time}ms")

        if self.blog:
            if self.debug_print:
                print("starting blog part")
            
            # blogposts - done
            
            dest_dir = self.destination + self.blog_url_path
            if self.blog_url_path != "/":
                os.mkdir(dest_dir)
            blogposts = self._find_folders(self.blog_articles_path)

            with open(self.blog_template_folder + "/blogpost.html", "r") as template:
                blogpost_template = template.read()
            
            if self.debug_print:
                print("replacing placeholders in template")
            
            replaced_templates = self._replace_placeholders(blogpost_template, p)
            if replaced_templates:
                blogpost_template = replaced_templates

            for i in blogposts:
                if self.debug_print:
                    print(f"doing: {i}")
                metadata_path = i + "/metadata.json"

                if not self._is_jsonfile(metadata_path):
                    raise TypeError(f"{metadata_path} couldnt be parsed as json file")
                data = self._read_json_file(metadata_path)

                dest_post_dir = dest_dir + data['id']
                os.mkdir(dest_post_dir)

                blogpost = self._blog_replacing(metadata_path, blogpost_template, self.datetime_format)

                with open(i + "/content.html", "r") as content:
                    blogpost = blogpost.replace(self.blog_pattern_prefix + "content" + self.blog_pattern_suffix, content.read())

                with open(dest_post_dir + "/index.html", "w") as html_file:
                    html_file.write(blogpost)
                
            # indexes
            p_blog = re.compile(self.blog_regex)
            all_files = self._find_all_files()
            self._check_and_replace(all_files, p_blog, True)

        if not self.no_output:
            after_blog_time = time.perf_counter()
            after_blog_time_dur = int((after_blog_time - after_templating_time)*1000)
            print(f"Blog part completed in {after_blog_time_dur}ms")
                
                
                

        self._remove_includes(self.template_prefix)

        if not self.no_output:
            final_time = time.perf_counter()
            tot_execution_time = int((final_time - start_time)*1000)
            print(f"Total completed in {tot_execution_time}ms")

    def _find_includes(self, template_prefix:str):
        includes = []
        for i in self._find_templates(template_prefix):
            if self._is_textfile(i):
                includes.append(i)
            elif os.path.isdir(i):
                for y in self._findall(i):
                    if self._is_textfile(y):
                        includes.append(y)
            else:
                raise FileNotFoundError(f"{i} isn't a text file or directory. Or at least I am unable to read it.")

        return includes

    def _find_rest_files(self, includes):
        file_paths_wo_includes = []
        for i in self._find_all_files():
            if i not in includes:
                file_paths_wo_includes.append(i)
        return file_paths_wo_includes
        

    def _find_all_files(self): #only files no dirs
        file_paths = []
        for i in self._findall(self.destination):
            if self._is_textfile(i):
                file_paths.append(i)

        return file_paths

    def _find_templates(self, template_prefix:str):
        formatted_path = self.destination + "/**/" + template_prefix + "*"
        return glob.glob(formatted_path, recursive=True)

    def _findall(self, directory:str):
        formatted_path = directory + "/**/*"
        return glob.glob (formatted_path, recursive = True)

    def _remove_includes(self, template_prefix):
        for i in self._find_templates(template_prefix):
            if os.path.isdir(i):
                shutil.rmtree(i)
            elif os.path.isfile(i):
                os.remove(i)
            else:
                raise FileNotFoundError(f"FATAL: {i} should have been raised as no text file before but it didn't happen.")

    def _is_textfile(self, path:str):
        if os.path.isfile(path):
            with open(path, "r") as i_file:
                try:
                    i_file.read()
                except:
                    return False
                else:
                    return True
        
        return False

    def _blog_replacing(self, metadata_path:str, template:str, datetime_format:str, show_edited = True):
        data = self._read_json_file(metadata_path)

        dates = []
        if data["date"] == data["last_edit"] or not show_edited:
            if not self.use_unix_epoch:
                data["last_edit"] = ""
            else:
                dates = ["date"]
        else:
            dates = ["date", "last_edit"]
        blogpost = template

        for name, value in data.items():
            if (name == "date" or name == "last_edit") and self.use_unix_epoch:
                continue

            blogpost = blogpost.replace(self.blog_pattern_prefix + name + self.blog_pattern_suffix, value)
        if self.use_unix_epoch:
            if not self.use_localtime:
                tz = timezone(timedelta(hours = self.timezone_utc_offset_h, minutes = self.timezone_utc_offset_min))
            formatted_date = ""
            for x in dates:
                if self.use_localtime:
                    date_and_time = datetime.fromtimestamp(data[x])
                else:
                    date_and_time = datetime.fromtimestamp(data[x], tz = tz)

                if x == "last_edit":
                    formatted_date = formatted_date + self.blog_date_edited_at_text

                intermediate_formatted_date = datetime_format

                intermediate_formatted_date = intermediate_formatted_date.replace("D", self._add_zero(date_and_time.day))
                intermediate_formatted_date = intermediate_formatted_date.replace("M", self._add_zero(date_and_time.month))
                intermediate_formatted_date = intermediate_formatted_date.replace("Y", self._add_zero(date_and_time.year))
                intermediate_formatted_date = intermediate_formatted_date.replace("h", self._add_zero(date_and_time.hour))
                intermediate_formatted_date = intermediate_formatted_date.replace("m", self._add_zero(date_and_time.minute))
                intermediate_formatted_date = intermediate_formatted_date.replace("s", self._add_zero(date_and_time.second))
                intermediate_formatted_date = intermediate_formatted_date.replace("tz", str(tz))

                formatted_date = formatted_date + intermediate_formatted_date
                if x == "last_edit":
                    formatted_date = formatted_date + self.blog_date_edited_at_text_after

            return blogpost.replace(self.blog_pattern_prefix + "date" + self.blog_pattern_suffix, formatted_date)

    def _create_blog_placeholders(self, metadata_path:str):
        with open(self.blog_template_folder + "/selection.html", "r") as s:
            source = s.read()
        snippet = self._blog_replacing(metadata_path, source, self.blog_preview_datetime_format, False)
        
        content_path = metadata_path.replace("metadata.json", "content.html")
        with open (content_path, "r") as cont:
            content_preview = cont.read(self.blog_preview_char_limit)
        content_preview = re.sub(re.compile('<.*?>'), '', content_preview)
        content_preview = html.escape(content_preview) #just in case, shouldnt be needed
        snippet = snippet.replace(self.blog_pattern_prefix + "content_preview" + self.blog_pattern_suffix, content_preview)

        data = self._read_json_file(metadata_path)

        return snippet.replace(self.blog_pattern_prefix + "url" + self.blog_pattern_suffix, self.blog_url_path + data["id"])

    def _blog_replace_placeholders(self, placeholder:str, source:str):
        x = placeholder.replace(" ", "")
        x = x.replace(self.blog_pattern_prefix + "blogposts|", "")
        x = x.replace(self.blog_pattern_suffix, "")
        y = x.split("|")
        all_metadata_files = glob.glob(self.blog_articles_path + "/*/metadata.json")
        # assume every metadata file was already confirmed to be valid json in code before
        match y[0]:
            case "latest":
                all_metadata_files = sorted(all_metadata_files, key = lambda x: int(self._read_json_file(x)["date"]))
                all_metadata_files.reverse()
            case "latest_edit":
                all_metadata_files = sorted(all_metadata_files, key = lambda x: int(self._read_json_file(x)["last_edit"]))
                all_metadata_files.reverse()
            case "alphabetically":
                all_metadata_files = sorted(all_metadata_files, key = lambda x: self._read_json_file(x)["title"])
            case "id":
                for i in all_metadata_files:
                    data = self._read_json_file(i)
                    if data["id"] == y[1]:
                        source = source.replace(placeholder, self._create_blog_placeholders(i))
                        return source
                raise Exception(f"no id {y[1]} found")
            case "random":
                random.shuffle(all_metadata_files)
            case _:
                raise Exception("Invalid blogposts sorting type")
            
        
        snippet = ""
        if y[1] == "all":
            for i in all_metadata_files:
                snippet = snippet + self._create_blog_placeholders(i)
        else:
            for i in range(min(int(y[1]), len(all_metadata_files))):
                snippet = snippet + self._create_blog_placeholders(all_metadata_files[i])
        source = source.replace(placeholder, snippet)
        
        return source

    def _replace_placeholders(self, source:str, p:re.Pattern, is_blog = False):
        regex_matches = p.findall(source)
        if not regex_matches:
            if self.debug_print:
                print("no match")
            return None
        else:
            if self.debug_print:
                print("match")
            for i in regex_matches:
                try:
                    if self.debug_print:
                        print(i)
                    if is_blog:
                        source = self._blog_replace_placeholders(i, source)
                    else:
                        x = i.replace("./", "")
                        for j in self.placeholder_elements:
                            x = x.replace(j, "")
                        with open(self.destination + "/" + x, "r") as filler:
                            filler_str = filler.read()
                            if not p.findall(filler_str):# if there are no placeholders in filler
                                if self.debug_print:
                                    print("executing")
                                source = source.replace(i, filler_str)
                            else: # if there are, do it later.
                                return "error_qerg87abiluvcn" #TODO raise instead

                except Exception as e:
                    if not self.skip_invalid_placeholders:
                        raise TypeError(f"{i} isn't a valid placeholder. This mostly means that the path is wrongly formatted. More info: {e}")
                    print(f"WARN: {i} isn't a valid placeholder. This mostly means that the path is wrongly formatted (whole file skipped). More info: {e}")
            return source

    def _check_and_replace(self, paths:list[str], p:re.Pattern, is_blog = False):
        for path in paths:
            if self.debug_print:
                print(f"\npath: {path}")
            with open(path, "r") as file_r:
                formatted = self._replace_placeholders(file_r.read(), p, is_blog)
            if formatted == "error_qerg87abiluvcn":
                if self.debug_print:
                    print("skipping")
                if not paths[-1] == path:
                    paths.append(path)
                continue
            if formatted:
                with open(path, "w") as file_w:
                    file_w.write(formatted)

    def _is_jsonfile(self, path:str):
        if self._is_textfile(path):
            if path.endswith(".json"):
                with open(path, "r") as json_file:
                    try:
                        json.load(json_file)
                    except:
                        return False
                    else:
                        return True
        
        return False
    
    def _find_jsons(self, file_paths:list[str]):
        jsons = []
        for i in file_paths:
            if self._is_jsonfile(i):
                jsons.append(i)

        return jsons

    def _read_json_file(self, path):
        """
        please validate that provided path is valid json beforehand
        """
        with open(path, "r") as jfile:
            data = json.load(jfile)
        return data

    def _find_blueprints(self, json_type):
        blueprints = []
        jsons = self._find_jsons(self._find_all_files())
        for i in jsons:
            data = self._read_json_file(i)
            if data["type"] == json_type: #the field equals the one we want
                blueprints.append(i)
        return blueprints

    def _find_folders(self, path:str):
        formatted_path = path + "/*"
        return glob.glob(formatted_path)
    
    def _add_zero(self, number:int):
        if self.datetime_double_digits:
            if number < 10:
                return "0" + str(number)
        return str(number)