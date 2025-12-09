import fs from 'fs';
import { google } from 'googleapis';

const FILE_ID = '11Z4DmchYtu9UwYGeihIOANzquVmVhFQ_'; // ID real do arquivo do Google Drive
const SERVICE_ACCOUNT_FILE = 'service_account.json';

async function downloadEnv() {
  const auth = new google.auth.GoogleAuth({
    keyFile: SERVICE_ACCOUNT_FILE,
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });

  const drive = google.drive({ version: 'v3', auth });
  const dest = fs.createWriteStream('.env');

  const res = await drive.files.get(
    { fileId: FILE_ID, alt: 'media' },
    { responseType: 'stream' }
  );

  await new Promise((resolve, reject) => {
    res.data
      .on('end', () => {
        console.log('Download do .env concluído.');
        resolve();
      })
      .on('error', (err) => {
        console.error('Erro ao baixar .env:', err);
        reject(err);
      })
      .pipe(dest);
  });
}

downloadEnv();
