const { Dropbox } = require('dropbox');
const fs = require('fs');
const path = require('path');

class DropboxService {
    constructor() {
        this.dropbox = null;
        this.modelFolder = '/gift_question_models';
    }

    async initialize() {
        try {
            if (!process.env.DROPBOX_ACCESS_TOKEN) {
                throw new Error('DROPBOX_ACCESS_TOKEN nie je nastavený v .env súbore');
            }

            this.dropbox = new Dropbox({
                accessToken: process.env.DROPBOX_ACCESS_TOKEN
            });

            // Vytvoríme priečinok pre modely ak neexistuje
            await this.ensureModelFolder();
            
            console.log('Dropbox služba inicializovaná');
        } catch (error) {
            console.error('Chyba pri inicializácii Dropbox:', error);
            throw error;
        }
    }

    async ensureModelFolder() {
        try {
            try {
                await this.dropbox.filesGetMetadata({ path: this.modelFolder });
            } catch (error) {
                if (error.status === 409) { // Folder už existuje
                    return;
                }
                // Vytvoríme nový priečinok
                await this.dropbox.filesCreateFolder({ path: this.modelFolder });
            }
        } catch (error) {
            console.error('Chyba pri vytváraní priečinka:', error);
            throw error;
        }
    }

    async uploadModel(modelPath) {
        try {
            const modelFiles = ['model.json', 'weights.bin'];
            const uploadPromises = modelFiles.map(async (fileName) => {
                const filePath = path.join(modelPath, fileName);
                const dropboxPath = `${this.modelFolder}/${fileName}`;

                // Načítame súbor
                const fileContent = fs.readFileSync(filePath);
                
                // Nahrajeme na Dropbox
                await this.dropbox.filesUpload({
                    path: dropboxPath,
                    contents: fileContent,
                    mode: { '.tag': 'overwrite' }
                });
            });

            await Promise.all(uploadPromises);
            console.log('Model bol úspešne nahratý na Dropbox');
            return true;
        } catch (error) {
            console.error('Chyba pri nahrávaní modelu:', error);
            return false;
        }
    }

    async downloadModel(modelPath) {
        try {
            const modelFiles = ['model.json', 'weights.bin'];
            const downloadPromises = modelFiles.map(async (fileName) => {
                const dropboxPath = `${this.modelFolder}/${fileName}`;
                const localPath = path.join(modelPath, fileName);

                try {
                    // Stiahneme súbor z Dropboxu
                    const { result } = await this.dropbox.filesDownload({ path: dropboxPath });
                    
                    // Uložíme lokálne
                    fs.writeFileSync(localPath, result.fileBinary);
                } catch (error) {
                    if (error.status === 409) { // Súbor neexistuje
                        return false;
                    }
                    throw error;
                }
            });

            const results = await Promise.all(downloadPromises);
            const allFilesDownloaded = results.every(result => result !== false);

            if (allFilesDownloaded) {
                console.log('Model bol úspešne stiahnutý z Dropboxu');
                return true;
            } else {
                console.log('Niektoré súbory modelu neboli nájdené na Dropboxe');
                return false;
            }
        } catch (error) {
            console.error('Chyba pri sťahovaní modelu:', error);
            return false;
        }
    }
}

module.exports = DropboxService; 