from bs4 import BeautifulSoup
import argparse
import ast
import html
import os
import requests
import sys
import time

base_url = "https://nhentai.net"
login_url = "https://nhentai.net/login/"
fav_url = "https://nhentai.net/favorites/"

base_path = os.path.dirname(os.path.realpath(__file__))
tag_path = base_path + "/old_tags.txt"
fav_path = base_path + "/old_favs.txt"
bio_path = base_path + "/old_bio.txt"

#0 = old, 1 = new
user_paths = ["", ""]
usernames = ["", ""]

#deprecated as of who knew when
def login(username, password, age):
    session = requests.Session()
    res = session.get(login_url)
    soup = BeautifulSoup(res.content, "html.parser")
    token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

    #referer header is very important in CSRF situations for this site
    res = session.post(login_url, data = {
        "csrfmiddlewaretoken": token,
        "username_or_email": username,
        "password": password,
        "next": ""
    }, headers = { "referer": login_url })
    #only redirects to base url on successful login
    if res.url == (base_url + "/"):
        print("Logged into " + username + " successfully")
        if (age >= 0):
            user_paths[age] = get_account_path(session)
            usernames[age] = username
        return session
    else:
        print("Login for " + username + " failed...")
        sys.exit(0)
#end_login

def login_session(sessionid, age):
    session = requests.Session()
    sess_cookie = requests.cookies.create_cookie(domain="nhentai.net",name="sessionid",value=sessionid)
    session.cookies.set_cookie(sess_cookie)

    res = session.get(base_url)
    soup = BeautifulSoup(res.content, "html.parser")

    sign_in_btn = soup.find("li", {"class": "menu-sign-in"})
    if sign_in_btn == None:
        print("Login session updated successfully")
        if (age >= 0):
            set_account_info(session, age)
        return session
    else:
        print("Imported session is invalid")
        sys.exit(0)
#end_login_session

def set_account_info(session, age):
    res = session.get(base_url)
    soup = BeautifulSoup(res.content, "html.parser")
    menu = soup.find("ul", {"class": "menu right"})

    items = list(menu.children)
    user_path = items[1].next_element.attrs["href"]
    username = user_path[user_path.rindex("/")+1:]

    user_paths[age] = user_path
    usernames[age] = username
#end_get_account_info

def favorite(session, mango_url):
    res = session.get(mango_url)
    soup = BeautifulSoup(res.content, "html.parser")

    fav = soup.find("span", {"class": "text"}).text.lower()
    html = res.text
    tk_start = html.index("csrf_token: \"")
    #13 to account for the csrf_token: "
    html = html[tk_start+13:]
    token = html[:html.index("\"")]

    mango_id = mango_url.split("/")[-2]
    post_url = base_url + "/api/gallery/" + mango_id + "/" + fav

    res = session.post(post_url, headers = {
        "referer": mango_url,
        "x-csrftoken": token,
        "x-requested-with": "XMLHttpRequest"
    }) 

    if res.ok:
        fav = soup.find("span", { "class": "text" }).text
        return mango_url + " has been " + ("favorited" if fav == "Favorite" else "unfavorited")
#end_favorite

def get_old_favorites(old_session):
    res = old_session.get(fav_url)
    soup = BeautifulSoup(res.content, "html.parser")
    pagination = soup.find("section", {"class": "pagination"})

    #only 1 page of favorites
    if pagination == None:
        export_old_favorites(old_session, 1, 1)

    else:
        first = soup.find("a", {"class": "current"}).attrs["href"].split("=")[1]
        last = soup.find("a", {"class": "last"}).attrs["href"].split("=")[1]
        export_old_favorites(old_session, int(first), int(last))
#end_get_old_favorites

def export_old_favorites(old_session, first, last):
    #clears the file if it already exists
    open(fav_path, "w").close()
    for pg in range(first, last + 1):
        fav_pg = fav_url + "?page=" + str(pg)
        res = old_session.get(fav_pg)
        soup = BeautifulSoup(res.content, "html.parser")
        favorites = soup.find_all("a", {"class": "cover"})
        for i in range(0, len(favorites)):
            print("Retrieving page " + str(pg) + " index " + str(i) + "...", end = "\r")
            with open(fav_path, "a") as f:
                f.write(base_url + favorites[i].attrs["href"] + "\n")
                f.close()
        res.close()
    print("\nFavorites successfully exported!")
#end_export_old_favorites

def import_favorites(new_session):
    with open(fav_path, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            line = lines[::-1][i].strip()
            line = line.strip()
            s = favorite(new_session, line)
            print(s + " (" + str(i + 1) + "/" + str(len(lines)) + ")     ", end = "\r")
    print("\nFavorites successfully imported!")
#end_import_favorites

def export_old_tags(old_session):
    blacklist_url = base_url + user_paths[0] + "/blacklist"
    res = old_session.get(blacklist_url)

    search_str = "window._blacklist_tags = JSON.parse(\""
    tags = res.text[res.text.index(search_str) + len(search_str):]
    tags = tags[:tags.index("\")")]
    tags = tags.encode().decode("unicode-escape")

    with open(tag_path, "w") as f:
        f.write(tags)
        f.close()
        print("Tags exported successfully!")
#end_export_old_tags

def import_old_tags(new_session):
    blacklist_url = base_url + user_paths[1] + "/blacklist"

    res = new_session.get(blacklist_url)
    #shifts start to "csrf_token" to isolate the token initialisation
    token = res.text[res.text.index("csrf_token:"):]
    #shift end to first instance of "," and removes the initialisation variable to get only the token value
    token_str = token[0:token.index(",")].replace("csrf_token:", "").strip()
    #replaces the "" in the initialisation process
    token_str = token_str.replace("\"", "")

    with open(tag_path, "r") as f:
        tag_str = f.read()
        tags = ast.literal_eval(tag_str)
        added_tags = generate_added_tags(tags)

        res = new_session.post(blacklist_url, json = {
            "added": added_tags,
            "removed": []
        }, headers = {
            "x-requested-with": "XMLHttpRequest",
            "x-csrftoken": token_str,
            "referer": blacklist_url
        })
        if res.ok:
            print("Tags successfully imported!")
        else:
            print("Tags failed to import. Reason: " + res.reason)
#end_import_old_tags

def generate_added_tags(tags):
    return [{"id": tag["id"], "name": tag["name"], "type": tag["type"]} for tag in tags]
#end_generate_added_tags

def export_bio(old_session):
    bio_url = base_url + user_paths[0] + "/edit"

    res = old_session.get(bio_url)
    soup = BeautifulSoup(res.content, "html.parser")

    about = soup.find("input", {"id": "id_about"}).attrs["value"]
    fav_tags = soup.find("input", {"id": "id_favorite_tags"}).attrs["value"]
    themes = soup.find("select", {"id": "id_theme"}).find_all("option")

    for theme in themes:
        if "selected" in theme.attrs:
            f = open(bio_path, "w")
            f.write(about + "\n" + fav_tags + "\n" + theme.attrs["value"])
            f.close()
            print("Bio successfully exported!")
#end_export_bio

def import_bio(new_session):
    bio_url = base_url + user_paths[1] + "/edit"

    res = new_session.get(bio_url)
    soup = BeautifulSoup(res.content, "html.parser")
    token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

    with open(bio_path, "r") as f:
        old_bio = f.readlines()

        res = new_session.post(bio_url, data = {
            "csrfmiddlewaretoken": token,
            "username": usernames[1],
            "about": old_bio[0],
            "favorite_tags": old_bio[1],
            "theme": old_bio[2],
        }, headers = { "referer": bio_url })

        if res.ok:
            print("Bio successfully imported!")
        else:
            print("Bio failed to be imported. Reason: " + res.reason)
#end_import_bio

def query(s):
    query_input = input(s + " (Y/n): ").strip().lower()
    if query_input in ["", "y", "yes"]:
        return True
    elif query_input in ["n", "no"]:
        return False
    else:
        print("Invalid input.")
        query(s)

def export_nh():
    old_sessionid = input("Please enter your old account's login session: ")
    old_session = login_session(old_sessionid, 0)
    if query("Do you wish to export your blacklisted tags?"):
        export_old_tags(old_session)
    if query("Do you wish to export your account bio?"):
        export_bio(old_session)
    if query("Do you wish to export your favorited hentei mangoes?"):
        get_old_favorites(old_session)
#end_export_nh

def import_nh():
    new_sessionid = input("Please enter your new account's login session: ")
    new_session = login_session(new_sessionid, 1)
    if query("Do you wish to import your old blacklisted tags?"):
        import_old_tags(new_session)
    if query("Do you wish to import your old account bio?"):
        import_bio(new_session)
    if query("Do you wish to import your old favourited hentei mangoes?"):
        import_favorites(new_session)
#end_import_nh

parser = argparse.ArgumentParser(description = "Account exporter/importer for nhentai")

parser.add_argument("-e", "--export", action = "store_true", dest = "export_acc", default = False)
parser.add_argument("-i", "--import", action = "store_true", dest = "import_acc", default = False)

results = parser.parse_args()

if __name__ == "__main__":
    if results.export_acc:
        export_nh()
    elif results.import_acc:
        import_nh()
    elif not results.export_acc and not results.import_acc:
        export_nh()
        print("")
        import_nh()