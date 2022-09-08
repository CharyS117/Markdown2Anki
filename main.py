from core.md2anki import md2anki

if __name__ == '__main__':
    # the test folder is aim for test
    working_dir = 'test'
    # separator for front and back
    note_sep = '\n\n%\n\n'
    # separator for cards(notes)
    module_sep = '\n\n----\n\n'
    # the folder name for media files where you store your images
    media_folder_name = 'pic'
    md2anki(working_dir, note_sep, module_sep, media_folder_name)