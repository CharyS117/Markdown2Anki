import requests
import json
import os


class AnkiConnect:
    def __init__(self, **kwargs):
        self.port = kwargs.get('port', 8765)
        self.version = kwargs.get('version', 6)

    def request_json(self, action, **params):
        return json.dumps({'action': action, 'params': params, 'version': self.version})

    def invoke(self, action, **params):
        res = requests.post(f'http://localhost:{self.port}', data=self.request_json(action, **params)).json()

        if len(res) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in res:
            raise Exception('response is missing required error field')
        if 'result' not in res:
            raise Exception('response is missing required result field')
        if res['error'] is not None:
            raise Exception(res['error'])
        return res['result']


class Note:
    def __init__(self, **kwargs):
        self.note_id = kwargs.get('noteId')
        self.model_name = kwargs.get('modelName')
        self.tags = kwargs.get('tags')
        self.fields = kwargs.get('fields')

    def compare_content(self, another_note):
        return self.fields == another_note.fields


class Anki(AnkiConnect):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_note(self, deck_name, note: Note):
        params = {'deckName': deck_name, 'modelName': note.model_name, 'fields': note.fields}
        return self.invoke('addNote', note=params)

    def add_notes(self, deck_name, notes: [Note]):
        params = [{'deckName': deck_name, 'modelName': note.model_name, 'fields': note.fields} for note in notes]
        return self.invoke('addNotes', notes=params)

    def can_add_notes(self, deck_name, notes: [Note]):
        params = [{'deckName': deck_name, 'modelName': note.model_name, 'fields': note.fields} for note in notes]
        return self.invoke('canAddNotes', notes=params)

    def notes_info(self, notes_id: [int]) -> [Note]:
        info = self.invoke('notesInfo', notes=notes_id)
        # make json uniform
        for item in info:
            for k, i in item['fields'].items():
                item['fields'][k] = i['value']
        return [Note(**i) for i in info]

    def model_info(self, model_name):
        return self.invoke('modelFieldNames', modelName=model_name)

    def list_notes_by_deck(self, deck_name) -> [Note]:
        ids = self.invoke('findNotes', query=f'deck:{deck_name}')
        return self.notes_info(ids)

    def is_in_deck(self, deck_name, notes: [Note]):
        exists_notes = self.list_notes_by_deck(deck_name)
        result = [any([note.compare_content(i) for i in exists_notes]) for note in notes]
        return result

    def list_deck(self):
        return self.invoke('deckNames')

    def create_deck(self, deck_name):
        return self.invoke('createDeck', deck=deck_name)

    def sync_to_anki(self, notes, deck):
        # check if deck exists
        if deck not in self.list_deck():
            self.create_deck(deck)
        # filter notes already in deck
        check = self.is_in_deck(deck, notes)
        notes = [notes[i] for i in range(len(notes)) if not check[i]]
        # check if able to sync
        check = self.can_add_notes(deck, notes)
        if not all(check):
            print(f'Cannot add following to {deck}')
            for i in range(len(check)):
                if not check[i]:
                    print(notes[i].fields)
            raise ValueError('Check conflict')
        # sync
        self.add_notes(deck, notes)

    def store_media_file(self, file_path):
        return self.invoke('storeMediaFile', filename=os.path.split(file_path)[-1], path=file_path)

    def get_media_files_names(self, filename):
        return self.invoke('getMediaFilesNames', pattern=filename)

    def exists_media(self, filename):
        return bool(self.get_media_files_names(filename))
