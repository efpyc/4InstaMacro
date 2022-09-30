# -*- coding:utf-8 -*-

import random, os, json, codecs, time
from colorama import Fore, Style
from instagram_private_api import Client
from instagram_private_api import ClientCookieExpiredError, ClientLoginRequiredError

pwd = os.getcwd()
log_file = os.path.join(pwd, "log.json")
cookie_file = "cookie.json"
login_file = "login.txt"
base_log_data = json.dumps({
    "media_ids": [],
    "posts": [],
})

class MultiTool:
    def __init__(self):
        datas = get_login()
        check_log_file()
        self.user_name = datas['username']
        self.passwd = datas['password']
        self.login()

    def login(self):
        try:
            if not os.path.exists(os.path.join(pwd, cookie_file)):
                info("Cookie file was not found.")
                with open(os.path.join(pwd, cookie_file), "w", encoding="utf-8") as f:
                    f.write("{}")
                self.api = Client(auto_patch=True, authenticate=True, username=self.user_name, password=self.passwd, on_login=lambda x: self.dump_cookies(x))
                info(f"Welcome {self.user_name} !")
            else:
                with open(os.path.join(pwd, cookie_file)) as file:
                    cookies = json.load(file, object_hook=self.load_serialized)
                self.api = Client(username=self.user_name, password=self.passwd, settings=cookies, on_login=lambda x: self.dump_cookies(x))
                info(f"Welcome {self.user_name} !")
        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            error(e, err="ClientCookieExpiredError/ClientLoginRequiredError")
            self.api = Client(auto_patch=True, authenticate=True, username=self.user_name, password=self.passwd,
                              on_login=lambda x: self.dump_cookies(x))
        except Exception as e:
            error(e, err="UNKNOWN ERROR")

    def serialize(self, pyobj):
        if isinstance(pyobj, bytes):
            return {
                "__class__": "bytes",
                "__value__": codecs.encode(pyobj, "base64").decode()
            }
        raise TypeError(repr(pyobj) + "is not JSON serializable !!!")

    def follower_increase(self, tag, custom_comment):
        results = self.api.feed_tag(tag, Client.generate_uuid())
        ranked_items = []
        ids = get_ids()
        temp_list = [item for item in results.get('ranked_items', [])]
        for x in temp_list:
            if not x['caption']['media_id'] in ids:
                ranked_items.append(x)
        print(
            Style.BRIGHT + Fore.GREEN + f"Total {Fore.RESET + Fore.LIGHTMAGENTA_EX + str(len(ranked_items)) + Fore.RESET + Fore.GREEN} posts on '{Fore.RESET + Fore.RED + tag + Fore.RESET + Fore.GREEN}'." + Style.RESET_ALL)
        for ritem in ranked_items:
            code = ritem['code']
            media_id = ritem['caption']['media_id']
            print(f"[OWNER DATAS] {ritem}")
            owner = {
                "username": ritem['user']['username'],
                "full_name": ritem['user']['full_name'],
            }
            print(Style.BRIGHT + Fore.CYAN + owner['username'] + Fore.RESET + Fore.YELLOW + " | " + owner[
                'full_name'] + Fore.RESET + Fore.LIGHTBLUE_EX + " | " + str(media_id) + Style.RESET_ALL)
            try:
                self.api.post_like(media_id=media_id, module_name='feed_tag')
                time.sleep(random_delay(1, 2))
                #self.api.friendships_create()
                #time.sleep(random_delay(1, 1.5))
                self.api.post_comment(media_id=media_id, comment_text=custom_comment)
                time.sleep(random_delay())
                log_post(media_id, code)
            except Exception as e:
                print(Style.BRIGHT + Fore.WHITE + "[EXCEPTION] " + Fore.RESET + Fore.RED + str(e) + Style.RESET_ALL)

    def load_serialized(self, _json):
        if '__class__' in _json and _json['__class__'] == 'bytes':
            return codecs.decode(_json['__value__'].encode(), 'base64')
        return _json

    def dump_cookies(self, _api, _cookie_file=cookie_file):
        settings = _api.settings
        with open(_cookie_file, "w") as file:
            json.dump(settings, file, default=self.serialize)

    def tag_automation(self, tag, like=True, comment=True, comment_text="Awesome post dude !"):
        results = self.api.feed_tag(tag, Client.generate_uuid())
        ranked_items = []
        ids = get_ids()
        temp_list = [item for item in results.get('ranked_items', [])]
        for x in temp_list:
            if not x['caption']['media_id'] in ids:
                ranked_items.append(x)
        print(
            Style.BRIGHT + Fore.GREEN + f"Total {Fore.RESET + Fore.LIGHTMAGENTA_EX + str(len(ranked_items)) + Fore.RESET + Fore.GREEN} posts on '{Fore.RESET + Fore.RED + tag + Fore.RESET + Fore.GREEN}'." + Style.RESET_ALL)
        for ritem in ranked_items:
            code = ritem['code']
            media_id = ritem['caption']['media_id']
            owner = {
                "username": ritem['user']['username'],
                "full_name": ritem['user']['full_name'],
            }
            print(Style.BRIGHT + Fore.CYAN + owner['username'] + Fore.RESET + Fore.YELLOW + " | " + owner[
                'full_name'] + Fore.RESET + Fore.LIGHTBLUE_EX + " | " + str(media_id) + Style.RESET_ALL)
            try:
                if like:
                    self.api.post_like(media_id=media_id, module_name='feed_tag')
                    time.sleep(random_delay(1, 2))
                if comment:
                    self.api.post_comment(media_id=media_id, comment_text=comment_text)
                time.sleep(random_delay())
                log_post(media_id, code)
            except Exception as e:
                print(Style.BRIGHT + Fore.WHITE + "[EXCEPTION] " + Fore.RESET + Fore.RED + str(e) + Style.RESET_ALL)

def random_delay(start : float = 1, end : float = 5):
    return random.uniform(start, end)

def info(msg, text="INFO"):
    print(Style.BRIGHT + Fore.GREEN + "[" + Fore.RESET + Fore.WHITE + text + Fore.RESET + Fore.GREEN + "] " + Fore.RESET + Fore.WHITE + str(msg) + Style.RESET_ALL)

def error(msg, err="ERROR"):
    print(Style.BRIGHT + Fore.RED + "[" + Fore.RESET + Fore.WHITE + err + Fore.RESET + Fore.RED + "] " + Fore.RESET + Fore.WHITE + str(msg) + Style.RESET_ALL)

def question(msg, text="?"):
    x = input(Style.BRIGHT + Fore.LIGHTCYAN_EX + "[" + Fore.RESET + Fore.WHITE + text + Fore.RESET + Fore.LIGHTCYAN_EX + "] " + Fore.RESET + Fore.WHITE + str(msg) + Style.RESET_ALL)
    return x

def check_log_file(filename = log_file):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(base_log_data)
    else:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
        if not "{" in content and not "}" in content:
            with open(filename, "w", encoding="utf-8") as nfile:
                nfile.write(base_log_data)

def get_login():
    if not os.path.exists(os.path.join(pwd, login_file)):
        with open(os.path.join(pwd, login_file), "w", encoding="utf-8") as ff:
            pass
    with open(os.path.join(pwd, login_file), "r+", encoding="utf-8") as f:
        datas = f.readlines()
        if len(datas) > 0:
            user_name = datas[0].strip()
            password = datas[1].strip()
        else:
            user_name = question("Username: ")
            password = question("Password: ")
            f.write(f"{user_name}\n{password}")
    return {"username": user_name, "password": password}

def get_url(code):
    return "https://www.instagram.com/p/"+str(code)

def log_post(media_id, code):
    url = get_url(code)
    with open(log_file, "r", encoding="utf-8") as fdata:
        data = json.load(fdata)
    with open(log_file, "w", encoding="utf-8") as file:
        ids, posts = data['media_ids'], data['posts']
        if not media_id in ids:
            ids.append(media_id)
        if not url in posts:
            posts.append(url)
        data['media_ids'] = ids
        data['posts'] = posts
        file.write(json.dumps(data, indent=3))

def get_ids():
    with open(log_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data['media_ids']

def par(num : int, text : str):
    print(f"{Style.BRIGHT + Fore.MAGENTA}[ {Fore.RESET + Fore.WHITE + str(num) + Fore.RESET + Fore.MAGENTA} ] {Fore.RESET + Fore.WHITE + text}")

def logo():
    print("""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⣼⠿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⣼⣿⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠀⠀⠀⠀⠀⠀⠘⠛⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣤⣤⣤⣤⣤⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
""")