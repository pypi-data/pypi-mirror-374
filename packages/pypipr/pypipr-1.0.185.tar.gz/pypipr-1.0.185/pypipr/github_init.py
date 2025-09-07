from .console_run import console_run
from .input_char import input_char


def github_init():
    """
    Menyiapkan folder offline untuk dikoneksikan ke repository
    kosong github.
    Akan langsung di upload dan di taruh di branch main.


    ```py
    github_init()
    ```

    or run in terminal

    ```py
    pypipr github_init
    ```
    """
    u = input("username : ")
    p = input("password : ")
    g = input("github account name : ")
    r = input("repository name : ")

    url = f"https://{u}:{p}@github.com/{g}/{r}.git"
    if input_char(f"Apakah benar {url} ? [y] ") == "y":
        console_run("git init", print_info=False)
        console_run("git add .", print_info=False)
        console_run("git commit -m first_commit", print_info=False)
        console_run("git branch -M main", print_info=False)
        console_run(f"git remote add origin {url}", print_info=False)
        console_run("git push -u origin main", print_info=False)
