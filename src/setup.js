// Iterate through the JSON files, and update the tileset source to the correct location
import { getGamePath } from 'steam-game-path';
import {globby} from 'globby';
import { fileURLToPath } from 'url';
import { dirname, basename, join } from 'path';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));

const steam = getGamePath(1325260);

if (!steam.game) {
    console.error('Kitsune Tails in Steam not found');
    process.exit(1);
}

const paths = await globby([`${__dirname}/../*.json`]);
for (const path of paths) {
    if (path.includes('package.json') || path.includes('package-lock.json') || path.includes('objects.json')) {
        continue;
    }
    const data = JSON.parse(readFileSync(path, 'utf8'));
    for (let tileset of data.tilesets) {
        if (tileset.source) {
            const fileBasename = basename(tileset.source);
            let baseDir = 'Content'
            if (fileBasename === 'objects.json') {
                baseDir = 'docs'
            }
            let newSource = join(steam.game.path, baseDir, fileBasename)
            if (existsSync(newSource)) {
                tileset.source = newSource
            }
            if (fileBasename === 'objects.json') {
                tileset.source = 'objects.json'
            }
        }
    }
    console.log(data);
    writeFileSync(path, JSON.stringify(data, null, 2));
}

//console.log();