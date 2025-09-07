import random
import string


def password_generator(
    length=8, characters=string.ascii_letters + string.digits + string.punctuation
):
    """
    Membuat pssword secara acak

    ```python
    print(password_generator())
    ```
    """

    password = ""
    for _ in range(length):
        password += random.choice(characters)

    return password
