// checks the maps for broken links, bad data and unreachable levels

import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { inflateSync, gunzipSync } from 'node:zlib'

const GID_MASK = 0x0FFFFFFF
const hasDeps = existsSync('deps/Content')
let errors = 0
const error = (file, msg) => { errors++; console.log(`${file}: ${msg}`) }
const exists = (name, ext) => existsSync(`${name}.${ext}`) || (hasDeps && existsSync(`deps/Content/${name}.${ext}`))

// valid local tile ids for a tileset, or null when unknown (no deps/)
const tilesetCache = {}
function tileIds (ts) {
  if (!ts.source) return { has: id => id < ts.tilecount }
  if (!hasDeps) return null
  if (!(ts.source in tilesetCache)) {
    try {
      const t = JSON.parse(readFileSync(ts.source))
      const ids = new Set((t.tiles || []).map(x => x.id))
      tilesetCache[ts.source] = t.image ? { has: id => id < t.tilecount } : ids
    } catch (e) {
      tilesetCache[ts.source] = null
    }
  }
  return tilesetCache[ts.source]
}

function layerData (l) {
  if (Array.isArray(l.data)) return l.data
  let buf = Buffer.from(l.data, 'base64')
  if (l.compression === 'zlib') buf = inflateSync(buf)
  else if (l.compression === 'gzip') buf = gunzipSync(buf)
  else if (l.compression) throw new Error(`unsupported compression ${l.compression}`)
  const out = []
  for (let i = 0; i + 4 <= buf.length; i += 4) out.push(buf.readUInt32LE(i))
  return out
}

const flatten = layers => layers.flatMap(l => l.type === 'group' ? [l, ...flatten(l.layers || [])] : [l])

const files = readdirSync('.').filter(f => /^(level.*|bg-.*)\.json$/.test(f)).sort()
const graph = {}
const endLevel = new Set()

for (const file of files) {
  let m
  try {
    m = JSON.parse(readFileSync(file))
  } catch (e) {
    error(file, `invalid JSON: ${e.message}`)
    continue
  }
  const name = file.slice(0, -5)
  graph[name] = []
  const tilesets = [...(m.tilesets || [])].sort((a, b) => a.firstgid - b.firstgid)
  const owner = gid => tilesets.findLast(t => t.firstgid <= gid)

  for (const ts of tilesets) {
    if (!ts.source) continue
    if (!ts.source.startsWith('deps/Content/')) error(file, `tileset source "${ts.source}" should start with deps/Content/`)
    else if (hasDeps && !tileIds(ts)) error(file, `tileset ${ts.source} not found`)
  }

  const layers = flatten(m.layers || [])
  const objects = []
  for (const l of layers) {
    if (l.id >= m.nextlayerid) error(file, `layer "${l.name}" id ${l.id} >= nextlayerid ${m.nextlayerid}`)
    if (l.type === 'objectgroup') objects.push(...l.objects)
    if (l.type !== 'tilelayer') continue
    let data
    try {
      data = layerData(l)
    } catch (e) {
      error(file, `layer "${l.name}" data could not be decoded: ${e.message}`)
      continue
    }
    if (data.length !== l.width * l.height) error(file, `layer "${l.name}" has ${data.length} tiles, expected ${l.width}x${l.height}=${l.width * l.height}`)
    data.forEach((raw, i) => {
      const gid = raw & GID_MASK
      if (!gid) return
      const ts = owner(gid)
      const ids = ts && tileIds(ts)
      if (!ts || (ids && !ids.has(gid - ts.firstgid))) error(file, `layer "${l.name}" cell ${i} (${i % l.width},${Math.floor(i / l.width)}) gid ${gid} is outside its tileset`)
    })
  }

  const ids = new Set()
  for (const o of objects) {
    if (ids.has(o.id)) error(file, `duplicate object id ${o.id}`)
    ids.add(o.id)
    if (o.id >= m.nextobjectid) error(file, `object id ${o.id} >= nextobjectid ${m.nextobjectid}`)
    if (o.gid) {
      const gid = o.gid & GID_MASK
      const ts = owner(gid)
      const tids = ts && tileIds(ts)
      if (!ts || (tids && !tids.has(gid - ts.firstgid))) error(file, `object ${o.id} gid ${gid} is outside its tileset`)
    }
  }
  for (const o of objects) {
    for (const p of o.properties || []) {
      if (p.name === 'zoneTo' && p.value) {
        if (!existsSync(`${p.value}.json`)) error(file, `object ${o.id} zoneTo "${p.value}" does not exist`)
        graph[name].push(p.value)
      }
      if (p.name === 'path' && p.value && !ids.has(p.value)) error(file, `object ${o.id} path points at missing object ${p.value}`)
      if (p.name === 'endLevel' && p.value === true) endLevel.add(name)
    }
  }

  for (const p of m.properties || []) {
    if (p.name === 'music' && p.value && (hasDeps || p.value.startsWith('music-')) && !exists(p.value, 'ogg')) error(file, `music "${p.value}" does not exist`)
    if (p.name === 'background' && p.value && hasDeps && !exists(p.value, 'json')) error(file, `background "${p.value}" does not exist`)
  }
}

// follow zoneTo links from level.json
const reachable = new Set(['level'])
const queue = ['level']
while (queue.length) {
  for (const y of graph[queue.shift()] || []) {
    if (!reachable.has(y)) {
      reachable.add(y)
      queue.push(y)
    }
  }
}
for (const name of Object.keys(graph)) {
  if (name.startsWith('level') && !reachable.has(name)) error(`${name}.json`, 'not reachable from level.json through zoneTo')
}

// the main chain is the longest route to an endLevel object, so warp zones are skipped
let chain = []
const walk = path => {
  const x = path.at(-1)
  if (endLevel.has(x) && path.length > chain.length) chain = path
  for (const y of new Set(graph[x])) if (!path.includes(y)) walk([...path, y])
}
walk(['level'])
if (chain.length) console.log(`chain: ${chain.join(' -> ')} (endLevel)`)
else error('level.json', 'no zoneTo route to an endLevel object')

console.log(`${files.length} maps, ${errors} error${errors === 1 ? '' : 's'}${hasDeps ? '' : ' (deps/ not found, skipped game asset checks)'}`)
process.exit(errors ? 1 : 0)
