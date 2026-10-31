# Bramble's Snack Heist

An original cozy stealth game in one file, `index.html`: no build step, no image or sound files (everything is drawn and synthesized in code), only Google Fonts loaded from outside. It began as "a game like Sneaky Sasquatch" but is its own design; keep it that way.

## Before changing anything visual

Read `STYLE.md`. Every new area or asset should be finished to that bar before moving on: fewer, finished additions beat several quick ones.

## Checking your work

```bash
tests/run.sh shots HEAD   # render 42 shots of this version and the last commit, then open tests/out/report.html
tests/run.sh sim          # a full day for every camper on three seeds: late, stuck, piled up, through walls or water
tests/run.sh gaps         # trail stretches and patches of woods with no landmark in view
tests/run.sh audio        # render the music and ambience offline at each place: levels as heard, how much of the tune
                          # the water covers, low end, notes in key, plus a spectrogram per place in tests/out/audio
```

Nobody on the project can rely on hearing the mix, so check audio changes with `tests/run.sh audio` and keep it free of flags.

`index.html?test` plays a seeded game that never saves. Test hooks live in the "test mode" section near the end of the script.

## Code map

- **Inks:** `K` (current hour), `KR` (RGB), `DAYK` (fixed noon, for the minimap); `K.mix(a, b, k)` takes base inks only.
- **World:** `addSprite`, `solidRect` / `solidCircle` (`los: false` lets campers see past it), `clearAt` keeps trees off a spot, `GLADES`, `ZONES`, `PATHS`, `AREAS`, `BEACONS`. Draw functions are registered in the `DRAW` map by `kind`.
- **Campers:** `mkNPC(name, look, stats, schedule)`; a schedule is a list of `{from, to, ...post(x, y, face, opts)}`, `wander` or `patrol` tasks.
- **Sound:** `buildMixer` sets up the buses (base tune on `musicBus`, place instruments on `areaBus`, both into `musicOut`; ambience on `ambBus`). Place instruments are in `AREA_TUNES` / `areaNotes`; water loudness by position is `waterLevel`.
- **Feel:** tunable numbers for screen shake, grab pause, squash and plant bending live in `FEEL`.
- **Saves:** key `bramble-snack-heist-v1`. New save fields need a safe default in `applySave` so older saves still load.

## Shipping

Commit after each working change and push to `origin main` (public repo egwoo/brambles-snack-heist). The playable build is the claude.ai artifact https://claude.ai/artifact/LzcD8CavMyirikGQJJhBJF: publish `index.html` with that `url` so the link stays the same.
