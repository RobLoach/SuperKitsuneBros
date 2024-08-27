// this will setup tiled to work correctly

import { cp, readFile, writeFile } from 'fs/promises'
import { getGamePath } from 'steam-game-path'
import { glob } from 'glob'

// get the location of installed game-files
function getKitsuneGameDir () {
  const { game } = getGamePath(1325260)
  if (!game?.path) {
    throw new Error('Could not find Kitsune Tails install-dir')
  }
  return game.path
}

const kitsuneInstallDir = getKitsuneGameDir()

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
