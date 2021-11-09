
# nhentai-exporter

Want to do more with your nhentai account? [shameless-plug-here](https://github.com/Benjababe/NotCafeDownloader)

## Prerequisites

[beautifulsoup4](https://pypi.org/project/beautifulsoup4/) and [requests](https://pypi.org/project/requests/) are required before running the script. Install through the requirements.txt file.

`pip install -r requirements.txt`

## Running the script

The script can be run normally to proceed with the full import and exporting process and it will accept arguments if you specifically want to import or export your account. Use `-e or --export` to export and `-i or --import` to import. The account's blacklisted tags, bio and favourited mangas will be transferred in the process.

You will be required to retrieve the sessionid cookie of your nhentai account's session in a web browser that it is currently logged in to.

When importing however, please make sure that the corresponding files for the category exist. They will be named

- old_tags.txt
- old_bio.txt
- old_favs.txt

## Warnings

It is highly recommended that you do not import into an account that has already been used a fair bit as when importing favourites, any existing favourites in the new account will be removed if it is trying to be imported.
