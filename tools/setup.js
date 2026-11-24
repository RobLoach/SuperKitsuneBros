// this will setup tiled to work correctly

import { cp, readFile, writeFile, access } from 'node:fs/promises'
import { getGamePath } from 'steam-game-path'
import { glob } from 'glob'

let [,, kitsuneInstallDir] = process.argv

// not user-specifed, find it form Steam
if (!kitsuneInstallDir) {
  kitsuneInstallDir = getGamePath(1325260)?.game?.path
}

if (!kitsuneInstallDir) {
  throw new Error('Could not find Kitsune Tails install-dir, pass it in: npm t /WHEREVER/KITSUNE/IS/INSTALLED')
}
try {
  await access(`${kitsuneInstallDir}/Content`)
} catch (e) {
  throw new Error(`No Kitsune Tails install found at ${kitsuneInstallDir}`)
}

// copy deps
await cp(`${kitsuneInstallDir}/Content/`, 'deps/Content', { recursive: true })
await cp(`${kitsuneInstallDir}/docs/objects`, 'deps/Content/objects', { recursive: true })

// copy dev-manual
await cp(`${kitsuneInstallDir}/docs/Kitsune Tails Map Editing Guide.pdf`, 'deps/Kitsune Tails Map Editing Guide.pdf')

// I needed to clean up the paths in these for them to work in Tiled
for (const file of await glob('deps/**/*.json')) {
  let j
  try {
    j = JSON.parse((await readFile(file, 'utf8')).replace(/^\uFEFF/, ''))
  } catch (e) {
    console.warn(`Skipping ${file}: ${e.message}`)
    continue
  }
  if (!Array.isArray(j.tilesets)) continue
  for (const t of j.tilesets) {
    if (t.source) t.source = t.source.replace(/^(\.\.\/)+/, '')
  }
  await writeFile(file, JSON.stringify(j, null, 2))
}
