import dropbox
import os
from pathlib import Path

class DropboxService:
    def __init__(self):
        self.dropbox = None
        self.model_folder = '/gift_question_models'
        
    async def initialize(self):
        try:
            if not os.getenv('DROPBOX_ACCESS_TOKEN'):
                raise ValueError('DROPBOX_ACCESS_TOKEN nie je nastavený v .env súbore')

            self.dropbox = dropbox.Dropbox(os.getenv('DROPBOX_ACCESS_TOKEN'))
            await self.ensure_model_folder()
            print('Dropbox služba inicializovaná')
        except Exception as e:
            print(f'Chyba pri inicializácii Dropbox: {str(e)}')
            raise

    async def ensure_model_folder(self):
        try:
            try:
                self.dropbox.files_get_metadata(self.model_folder)
            except dropbox.exceptions.ApiError:
                self.dropbox.files_create_folder(self.model_folder)
        except Exception as e:
            print(f'Chyba pri vytváraní priečinka: {str(e)}')
            raise

    async def upload_model(self, model_path):
        try:
            model_files = ['model.json', 'weights.bin']
            for file_name in model_files:
                file_path = Path(model_path) / file_name
                dropbox_path = f"{self.model_folder}/{file_name}"
                
                with open(file_path, 'rb') as f:
                    self.dropbox.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

            print('Model bol úspešne nahratý na Dropbox')
            return True
        except Exception as e:
            print(f'Chyba pri nahrávaní modelu: {str(e)}')
            return False

    async def download_model(self, model_path):
        try:
            model_files = ['model.json', 'weights.bin']
            all_files_downloaded = True

            for file_name in model_files:
                dropbox_path = f"{self.model_folder}/{file_name}"
                local_path = Path(model_path) / file_name

                try:
                    _, res = self.dropbox.files_download(dropbox_path)
                    with open(local_path, 'wb') as f:
                        f.write(res.content)
                except dropbox.exceptions.ApiError:
                    all_files_downloaded = False
                    break

            if all_files_downloaded:
                print('Model bol úspešne stiahnutý z Dropboxu')
                return True
            else:
                print('Niektoré súbory modelu neboli nájdené na Dropboxe')
                return False
        except Exception as e:
            print(f'Chyba pri sťahovaní modelu: {str(e)}')
            return False 