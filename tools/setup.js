// this will setup tiled to work correctly

import { cp, readFile, writeFile } from 'fs/promises'
import { getGamePath } from 'steam-game-path'
import { glob } from 'glob'

let [,, kitsuneInstallDir] = process.argv

// not user-specifed, find it form Steam
if (!kitsuneInstallDir) {
  kitsuneInstallDir = getGamePath(1325260)?.game?.path
}

if (!kitsuneInstallDir) {
  throw new Error('Could not find Kitsune Tails install-dir')
}

// copy deps
await cp(`${kitsuneInstallDir}/Content/`, 'deps/Content', { recursive: true })
await cp(`${kitsuneInstallDir}/docs/objects`, 'deps/Content/objects', { recursive: true })

// copy dev-manual
await cp(`${kitsuneInstallDir}/docs/Kitsune Tails Map Editing Guide.pdf`, 'deps/Kitsune Tails Map Editing Guide.pdf')

// I needed to clean up the paths in these for them to work in Tiled
for (const file of await glob('deps/**/*.json')) {
  try {
    const j = JSON.parse(await readFile(file))
    for (const t of j.tilesets) {
      t.source = t.source.replace('../', '')
    }
    writeFile(file, JSON.stringify(j, null, 2))
  } catch (e) {}
}
