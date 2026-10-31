# Style guide

Bramble's Snack Heist looks like a mid-century national-park screenprint: flat shapes, a small fixed set of inks, keylines printed slightly off-register, and paper grain over everything. This page is the bar every new area, prop and character has to clear.

## Inks

Every color in the world comes from eleven inks. Use `K.<ink>`, `K.mix(a, b, k)` or `kA(ink, alpha)`. Never write a hex or `rgb()` value in world art: the whole ink set shifts with the hour (night, dawn, morning, day, golden, dusk), and a hard-coded color will look wrong at most times of day.

| Ink | Used for |
| --- | --- |
| `paper` | Signs, highlights, smoke, steam, mist, birch bark |
| `sun` | Lit windows, lamps, fire, the things worth grabbing |
| `leaf`, `moss`, `pine` | Grass, foliage, the forest floor (light to dark) |
| `earth`, `bark` | Paths, wood, buildings (light to dark) |
| `rust` | Roofs, warning signs, flags, rust on old metal |
| `water`, `deep` | Lake, creek, pond, the shadow side of cool things |
| `ink` | Keylines, shadows, the darkest darks |

- `K.mix` only takes the eleven base inks. The derived colors (`skinL`, `skinD`, `mossD`, `leafM`, `stone`, `stoneD`, `sand`, `path`) can be used directly but can't be mixed.
- **Accent budget:** `rust` and `sun` are for things that matter: snacks, lights, landmark tops, warnings. Scenery stays in greens, browns and blues so the accents read.

## Value: what the eye goes to first

1. Characters, snacks and hiding spots: highest contrast, always keylined.
2. Buildings and landmarks: strong silhouettes, keylined.
3. Trees and props: mid contrast.
4. The ground: lowest contrast. Scatter (ferns, mushrooms, grass tufts, sawdust) has no keyline.

Check a new piece at 9 am, dusk (7:36 pm) and night (10:30 pm). If it disappears at night or shouts at noon, adjust its inks, not its outline.

## Shapes and lines

- Flat fills. Gradients only for light: glows, darkness, mist.
- Keylines with `keyed(c, build, fill, ink, width)`: the fill, then the ink line nudged (+1.6, +1.1) like a second plate printed a hair off. Width 1.2–1.6 for props, 1.8–2.2 for buildings, never above 2.4.
- Slightly rounded corners (`rrect` radius 1–4). Nothing perfectly sharp, nothing blobby.
- One to three details per prop (a plank seam, a rivet, a label). Detail is a story, not texture.

## Light and shadow

- The sun crosses east to west; `SUN.dx` runs from about -0.7 (morning) to +0.7 (evening). Every grounded object gets one `shadow()` ellipse at its base, which leans with the sun automatically.
- Volumes get two tones: the side facing the sun in the base ink, the other side mixed toward `ink` or `bark` (see the tent faces and `drawTree`'s `lit`).
- After dark, windows, lamps and fires switch to `sun` and add an entry to `lights[]` for their glow. Nothing else gets brighter at night.

## Motion

- Anything alive moves a little: trees sway, flags flap, water ripples, smoke drifts. Offset the phase by world position (`time * 1.1 + x * .021`) so neighbors never move in step.
- Ambient motion stays small (1–3 px). **Beacons** (smoke columns, flags, mist, circling birds) are the exception: they're meant to be seen from a screen away, and they go in `BEACONS` so the gap check counts them.
- Plants react to whatever brushes past them (see `bend` on bushes and ferns) and spring back; small plants are springier.

## Areas

Each place has its own tint inside the palette, one beacon you can see from far off, one prop that tells you what happened there, and its own instrument in the music.

| Area | Tint | Beacon | History prop | Instrument |
| --- | --- | --- | --- | --- |
| Bramble's Den | deep moss | – | Claw-scratched boulder | low hum |
| Fire Lookout | – | Pennant on the cab | Fire-scarred snag | – |
| Apple Meadow | warm leaf | – | Old fence line | – |
| Campground | – | Campfire smoke at night | Initials carved in a picnic table | – |
| Snack Shack | – | – | Faded menu board | – |
| Ranger Station | – | Chimney smoke | Fire danger dial | – |
| Sunset Point | water | – | Memorial bench plaque | – |
| Amphitheater | – | Projector beam at showtime | – | – |
| RV Row | sun | Grill smoke | Abandoned rusty trailer | – |
| Beaver Pond | cool water | Fireflies at dusk | Drowned fence posts | water-drop bells |
| Old Mill | rust | Swallows round the stack | The mill itself | slow banjo |
| Whisper Falls | deep, mossy | Mist plume | Old gauging station | airy pad |
| North Shore | water | Herons over the rookery | – | – |
| West Woods | pine | Homestead chimney | Cabin ruin | – |

## Checklist for anything new

1. Colors come only from the inks, and it reads at 9 am, dusk and night.
2. Keylined if you can use it, hide in it, or walk into it.
3. A `shadow()` at its base.
4. A silhouette you can tell apart from its neighbors when the shot is shrunk to half size.
5. Something that moves, if it's alive or a landmark.
6. One story detail: wear, a sign, a personal object.
7. Its collision matches what's drawn, and trees are kept off it (`clearAt`).
8. It doesn't hide a landmark from the trail (`tests/run.sh gaps`).
9. Shots compared before and after (`tests/run.sh shots HEAD`), and the day simulation still passes.

## Type and interface

Titles and signs use Alfa Slab One; body text uses Zilla Slab. Signs are `paper` lettering on `bark` or `pine` boards. Panels are paper cards with an ink border and a hard offset shadow (`4px 4px 0`), never a blur.
