import os


TOKEN = '7c7113d4-126a-4c28-b13c-54cc0fcbcb7e'
print(TOKEN)
os.system(f'jupyter notebook --port 8880 --NotebookApp.token={TOKEN} test.ipynb ')


def get_token():
    print('token in get: ', TOKEN)
    return TOKEN
