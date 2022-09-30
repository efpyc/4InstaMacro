# -*- coding:utf-8 -*-

from utils import *

if __name__ == '__main__':
    logo()
    api = MultiTool()
    print(" ")
    par(0, "Auto Like + Comment by Hashtag.")
    par(1, "Follower increase (Auto Like + Comment + Follow)")
    print(" ")
    ask = int(question("Service: "))
    print(" ")
    if ask == 0:
        tags_input = question("Tag(s): ")
        custom_comment = question("Custom Comment: ")
        print(" ")
        tags = list(
            map(lambda text: text.replace(" ", ""), tags_input.split(",") if "," in tags_input else tags_input.split()))
        if len(tags) > 1:
            for tag in tags:
                api.tag_automation(tag, comment_text=custom_comment if not custom_comment == "" else "Awesome post dude.")
        else:
            api.tag_automation(tags[0], comment_text=custom_comment if not custom_comment == "" else "Awesome post dude.")
    elif ask == 1:
        tags_input = question("Tag(s): ")
        custom_comment = question("Custom Comment: ")
        print(" ")
        tags = list(
            map(lambda text: text.replace(" ", ""), tags_input.split(",") if "," in tags_input else tags_input.split()))
        if len(tags) > 1:
            for tag in tags:
                api.follower_increase(tag, custom_comment if not custom_comment == "" else "Awesome post dude, i liked your page can you follow me back ?")
        else:
            api.follower_increase(tags[0], custom_comment if not custom_comment == "" else "Awesome post dude, i liked your page can you follow me back ?")