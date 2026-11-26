---
name: add-music
description: Add a music track to the mod - download it safely, convert it to a music-*.ogg, make it loop or play once, set it on a map and credit the source. Use when asked to use a song, jingle or soundtrack URL as a level's background music.
---

# Add music

1. **Download into its own empty folder**, never the repo:
   ```sh
   mkdir -p /tmp/dlmusic && curl -sL -o /tmp/dlmusic/track.mp3 "<url>" && file /tmp/dlmusic/track.mp3
   ```
   Check it really is audio and note the length with `ffprobe -v error -show_entries format=duration`.

2. **Convert** to Ogg Vorbis like the other tracks (44.1 kHz stereo, 64 kbps), named `music-<name>.ogg` in the repo root:
   ```sh
   ffmpeg -v error -y -i /tmp/dlmusic/track.mp3 -c:a libvorbis -b:a 64k -ar 44100 -ac 2 music-<name>.ogg
   ```
   - **Loops** (level themes): the game repeats the file, so trim any silence at the end or the loop stutters.
   - **Plays once** (jingles like `music-pipe.ogg`): the maps have no "don't loop" setting, so this mod pads the jingle with silence to 10 minutes: add `-af apad -t 600`.

3. **Use it** on the map: set the map property `music` to `music-<name>` (no extension). For converted levels set it in the generator with `L.prop('music', 'music-<name>')` so rebuilds keep it; for hand-made maps edit the property.

4. **Credit** the source URL in the README's Resources list.

5. `npm run lint` checks every `music-*` the maps name exists. The release zip includes every `music-*.ogg` in the root.
