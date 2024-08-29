# Kitsune Tails: Super Kitsune Bros

An attempt at a faithful recreation of [1-1](https://en.wikipedia.org/wiki/World_1-1) and 1-2 of [Super Mario Bros](https://en.wikipedia.org/wiki/Super_Mario_Bros) in [Kitsune Tails](https://kitsunegames.com/kitsunetails/).

![Screenshot](tools/screenshot.jpg)

## Installation

1. [Download](https://github.com/RobLoach/SuperKitsuneBros/releases) the latest release
2. Extract it to your `KitsuneTails/levels` folder, usually available at one of the following...
    ```
    AppData\Roaming\KitsuneTails\levels
    $XDG_DATA_HOME/KitsuneTails/levels
    ~/Library/Application Support/KitsuneTails/levels
    ~/.local/share/KitsuneTails/levels
    ~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/KitsuneTails/levels
    ```

    The result should appear like `KitsuneTails/levels/SuperKitsuneBros/level.json`
  
3. Launch Kitsune Tails
4. Select Mods
5. Choose SuperKitsuneBros

## Development

1. Have [Node.js](https://nodejs.org/en) installed
1. Clone project to your levels dir (from above)
    ``` sh
    git clone https://github.com/RobLoach/SuperKitsuneBros.git ~/.local/share/KitsuneTails/levels
    ```
1. For Steam installed Kitsune, run...
    ```
    npm it
    ```
    > Note that there have been reported issues with the Flatpak-install of Steam
1. For non-Steam install (itch, etc), run...
    ```
    npm i
    npm t /WHEREEVER/KITSUNE/IS/INSTALLED
    ```
1. Open `SuperKitsuneBros.tiled-project` with [Tiled](https://www.mapeditor.org/)
1. See the newly created `deps` directory for example levels from Kitsume as well as the modding documentation

## File Descriptions

| Filename | Description |
| -------- | ----------- |
| bg-*.json | Background
| level-*.json | A map used in Super Kitsune Bros
| level.json | The opening welcome screen for the game
| music-*.ogg | Music for the game |
| tileset.png | Additional decoration tileset from the original game
| SuperKitsuneBros.tiled-project | Tiled project file
| tools | Various tools to aid development

## Resources

- https://nesmaps.com/maps/SuperMarioBrothers/SuperMarioBrothers.html
- https://downloads.khinsider.com/game-soundtracks/album/super-mario-bros
- https://fontstruct.com/fontstructions/show/1332355/arcade-classic-2-19

## License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
