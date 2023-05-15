import shutil
import pandas as pd
import os
from pathlib import Path
import string
from bs4 import BeautifulSoup

# This function sorts the dataframe by the order of the sections in the section_order list.
def sort_df_by_section_order(df: pd.DataFrame, section_order: list) -> pd.DataFrame:
    df['section_order'] = df['section'].apply(lambda x: section_order.index(x))
    df = df.sort_values(by='section_order')
    df = df.drop(columns='section_order')
    return df

# Moves the file located at filepath to the session folder. 
def move_file_to_session_folder(filepath: str, 
                                section_name: str,
                                new_name: str, 
                                folder: str=None) -> None:
    if folder is not None:
        folder_path = Path(f'{Path.cwd()}//{folder}')
        folder_path.mkdir(exist_ok=True)
    else:
        folder_path = Path(Path.cwd())

    full_folder_path = Path(f'{folder_path}//{section_name}') 
    full_folder_path.mkdir(exist_ok=True)
   
    # Use Path to get the file name and move the file to the section folder
    file_path = Path(f'{Path.cwd()}//{filepath}')
    new_file_path = Path(f'{full_folder_path}//{new_name}')
    shutil.move(file_path, new_file_path)
    return

# This function cleans a filename by removing all characters that are not
def clean_filename(filename: str) -> str:
    valid_chars: str = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename: str = ''.join(c for c in filename if c in valid_chars)
    return cleaned_filename


if __name__ == "__main__":
    with open("index.html", encoding='UTF-8') as fp:
        index_html = fp.read()

    soup = BeautifulSoup(index_html, 'html.parser')
    a_tags = soup.find_all('a')
    files = pd.DataFrame()
    for a in a_tags:
        section = a.find("div", class_ ='section').contents
        filename  = a.find("div", class_ ='filename').contents
        title = a.find("div", class_ ='title').contents
        author = a.find("div", class_ ='authors').contents
        session = section[0].split(" ", 1)[1]
        files = pd.concat([files, pd.DataFrame({"file":filename,
                                                 "section":section, 
                                                 "title":title, 
                                                 "session":session, 
                                                 "author":author})])
    files.index = files.file
    files = files.drop( "file", axis = 1)

    # not run for abstracts
    section_list = [
    "x",
    ]

    # Loop through the list of sections
    for section in section_list:
        # Print the section
        print(section)
    sort_df = sort_df_by_section_order(files, section_list)
    for file, contents in files.iterrows():
        try: 
            title = clean_filename(contents["title"])
            author = clean_filename(contents["author"].split(',')[0])
            name = f'{author}_{title}.pdf'
            _len = len(name)
            parent_dir = os.path.dirname(os.getcwd())
            if _len > (256 - len(parent_dir) - len(contents["section"]) -20):
                c = 256 - len(parent_dir) -len(contents["section"])- 20 - _len 
                short_title = title[:abs(c)]
                name = f'{author}_{short_title}.pdf'
            move_file_to_session_folder(file, contents['session'].replace("\n", "").strip(), new_name=name)
        except:
            print(name)