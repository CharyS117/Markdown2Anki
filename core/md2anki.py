from core.anki import Anki, Note
import re
import os
import mistune
import json


class md2anki:
    def __init__(self, folder, note_sep, module_sep, media_folder, run_on_init=True, **kwargs):
        self.anki = kwargs.get('anki')
        if not self.anki:
            self.anki = Anki()
        self.md_notes = {}
        self.folder = folder
        self.note_sep = note_sep
        self.module_sep = module_sep
        self.media_folder = media_folder
        if run_on_init:
            self.to_anki(folder)

    def parser(self, text):
        # math support
        maths = re.findall('\\$+.[\\s\\S]*?\\$+', text)
        text = re.sub('\\$+.[\\s\\S]*?\\$+', '{}', text)
        for i in range(len(maths)):
            maths[i] = maths[i].replace('\n', '')
            maths[i] = maths[i].replace('&', '&amp;')
            maths[i] = maths[i].replace('<', '&lt;')
            maths[i] = maths[i].replace('>', '&gt;')
            if '$$' in maths[i]:
                maths[i] = re.sub('\\$\\$([\\s\\S]*?)\\$\\$', '\\[\\1\\]', maths[i])
            else:
                maths[i] = re.sub('\\$([\\s\\S]*?)\\$', '\\(\\1\\)', maths[i])
        # md to html
        text = mistune.html(text)
        text = text.format(*maths)
        # delete <p> <pre>
        text = re.sub('<p>([\\s\\S]*?)</p>', '\\1', text)
        text = re.sub('<pre>([\\s\\S]*?)</pre>', '\\1', text)
        # reroute media files
        text = re.sub(f'(<img[\\s\\S]*?){self.media_folder}(/|%2F)([\\s\\S]*?)( /)?>', '\\1\\3>', text)
        # clear newlines
        text = text.strip('\n')
        # special anki auto format
        text = text.replace('&quot;', '"')
        text = text.replace('\n', '<br>')
        return text

    def convert_to_fields(self, path):
        with open(path, 'r') as file:
            raw = file.read()
        notes_raw = raw.split(self.module_sep)
        notes = [{'Front': self.parser(f), 'Back': self.parser(b)} for m in notes_raw for f, b in
                 [m.split(self.note_sep)]]
        return notes

    def load_md(self, md_file, deck):
        fields = self.convert_to_fields(md_file)
        # add deck to front
        for field in fields:
            field['Front'] = f'<div align="left"><font size="1" color="DCDCDC">{deck}</font></div>' + field['Front']
        # load field to Note
        notes = [Note(modelName='Basic', fields=j) for j in fields]
        return notes

    def import_media(self, folder):
        # load record
        if not os.path.exists(os.path.join(folder, 'imported.json')):
            imported = []
            with open(os.path.join(folder, 'imported.json'), 'w') as file:
                json.dump(imported, file)
        else:
            with open(os.path.join(folder, 'imported.json'), 'r') as file:
                imported = json.load(file)
        media_files = [i for i in os.listdir(folder) if not i.startswith('.')]
        media_files.remove('imported.json')
        for file in imported:
            media_files.remove(file)
        for media_file in media_files:
            # check if exists
            if self.anki.exists_media(media_file):
                raise Exception(f'{media_file} already exists in Anki')
            self.anki.store_media_file(os.path.join(folder, media_file))
            # add to imported
            imported.append(media_file)
        # record
        with open(os.path.join(folder, 'imported.json'), 'w') as file:
            json.dump(imported, file)

    def to_anki(self, folder):
        _, folders, files = next(os.walk(folder))
        # import medias
        if self.media_folder in folders:
            folders.remove(self.media_folder)
            self.import_media(os.path.join(folder, self.media_folder))
        # get notes
        for md_file in files:
            if not md_file.endswith('.md'):
                continue
            filename = os.path.splitext(md_file)[0]
            relpath = os.path.relpath(os.path.join(folder, filename), self.folder)
            relpath = os.path.normpath(relpath)
            deck = '::'.join(relpath.split(os.sep))
            notes = self.load_md(os.path.join(folder, md_file), deck)
            # add to anki
            self.anki.sync_to_anki(notes, deck)
        for sub_folder in folders:
            self.to_anki(os.path.join(folder, sub_folder))
