import requests
from tqdm import tqdm
import os
import consts
import json
import subprocess
import shutil

base_url = "https://api.github.com/repos/"

def remove_directory(dir):
    shutil.rmtree(dir)

def check_link(dir):
    if os.path.islink(dir):
        return os.readlink(dir)    
    else:
        return dir

def edit_desktop_file(path, key, new_value):
    with open(path, 'r') as file:
        lines = file.readlines()
    modified_lines = []

    for line in lines:
        if line.startswith(f"{key}="):
            modified_lines.append(f"{key}={new_value}\n")
        else:
            modified_lines.append(line)

    with open(path, 'w') as file:
        file.writelines(modified_lines)



def get_files(file_name):
    command = f"./{file_name} --appimage-extract"

    subprocess.run(
        command,
        shell=True,
        check=True,
        cwd=consts.APM_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    squashfs_path = os.path.join(consts.APM_PATH, "squashfs-root")

    for i in os.listdir(os.path.join(squashfs_path)):
        if i.endswith(".desktop"):
            desktop_dir = os.path.join(squashfs_path, i)
            desktop_file = os.path.join(squashfs_path, check_link(desktop_dir))

        if i == ".DirIcon":
            icon_dir = os.path.join(squashfs_path, i)
            icon_dir = os.path.join(squashfs_path, check_link(icon_dir))
            icon_dir = os.path.join(squashfs_path, check_link(icon_dir))

            global icon_file
            icon_file = os.path.join(consts.APM_PATH, "icons", os.path.basename(icon_dir))
            shutil.move(icon_dir, icon_file)
        

    # Give execute permissions
    os.chmod(desktop_file, 0o755)

    # Edit .desktop file
    edit_desktop_file(desktop_file, "Exec", os.path.join(consts.APM_PATH, file_name) + " %F")
    edit_desktop_file(desktop_file, "Icon", icon_file)
    # Remove TryExec because otherwise it just like doesn't work
    edit_desktop_file(desktop_file, "TryExec", "")

    global new_dir
    new_dir = os.path.join(consts.HOME, ".local/share/applications")

    shutil.move(desktop_file, new_dir)

    new_dir = os.path.join(new_dir, os.path.basename(desktop_file))
    remove_directory(squashfs_path)


def add_to_registry(name, repo_url, filename, desktop_file, icon):
    with open(consts.REGISTRY_PATH, "r+") as file:
        new_data = {
            name: {"path": filename, "url": repo_url, "desktop_file": desktop_file, "icon": icon}
        }

        file_data = json.load(file)
        file_data = file_data | new_data
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def check_existence(url):
    if requests.head(url).status_code == 200:
        return True
    else:
        return False


def split_github_name(name):
    return name.split("/")


def download_file(url, filename):
    print("Downloading " + url)
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    t = tqdm(total=total_size, unit="B", unit_scale=True)

    with open(filename, "wb") as f:
        for data in response.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    os.chmod(filename, 0o755)
    print("Download complete!")

def remove(input_value):
    registry = json.load(open(consts.REGISTRY_PATH, "r+"))
    app_registry = registry[input_value]

    os.remove(os.path.join(consts.APM_PATH, app_registry["path"]))
    os.remove(app_registry["desktop_file"])
    os.remove(app_registry["icon"])

    registry.pop(input_value, None)

    with open(consts.REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=4)
    print("App removed!")

def install(input_value):
    if "/" in input_value:
        split = split_github_name(input_value)
        owner = split[0]
        repo = split[1]
        repo_url = f"{base_url}{owner}/{repo}"
    else:
        repo = input_value
        repo_url = f"{base_url}{input_value}/{input_value}"
        if check_existence(repo_url):
            print("Repository found!")
        else:
            print(
                "Repository not found! Try inputing the username and repository name."
            )

    assets = requests.get(repo_url + "/releases/latest").json()["assets"]
    appimage_files = [i for i in assets if i["name"].endswith(".AppImage")]
    
    if len(appimage_files) > 1:
        print("Multiple .AppImage files found:")
        for i, file in enumerate(appimage_files):
            print(f"{i+1}. {file['name']}")

        choice = input("Which one would you like to download? (enter the number) ")
        chosen_file = appimage_files[int(choice) - 1]
        url = chosen_file["browser_download_url"]
    elif len(appimage_files) == 0:
        print("No Appimages found")
        return
    else:
        chosen_file = appimage_files[0]
        url = chosen_file["browser_download_url"]

    filename = chosen_file["name"]

    download_file(url, os.path.join(consts.APM_PATH, filename))
    print("Getting icon and .desktop file...")
    get_files(filename)
    add_to_registry(repo, repo_url, filename, new_dir, icon_file)

    print("Successfully installed!")


def list_installed():
    keys = json.load(open(consts.REGISTRY_PATH)).keys()
    for i in keys:
        print(i)
