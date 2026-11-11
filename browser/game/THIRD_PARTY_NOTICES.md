# Third-party notices

Original game code is MPL-2.0 (`LICENSE`).

## Owner-authorized artwork

The unchanged runner PNG, owl/wolf/sheep PNGs and their provenance are reused at the owner's explicit request from:

- https://github.com/kaansavukduran/fire-axolotl-extension at `c440c352f3b97f1efccbec871fd96d6ed5a6a6ed`.
- Its original donor https://github.com/kaansavukduran/fire-axolotl at `ad76813936a4b933780e1a4c712452a6b21d014b`.

The donor records original AI-generated, user-authorized artwork under MPL-2.0 to the extent licensable. Individual artwork records are preserved in `assets/RUNNER-PROVENANCE.json` and `assets/CHARACTERS-PROVENANCE.json`. This game does not include GPL browser extension components or third-party browser engines. No claim of exclusive copyright in AI-generated output, transfer of mascot ownership, or third-party endorsement is made.

The packaged PNG hashes match the donor. Display pixelation of companions happens in a shader; the source images are unchanged. Aion is Kaan's personal mascot. No Chrome dinosaur assets or code and no built-in ChatGPT Pet artwork are included.

## Font

Lexend, SIL Open Font License 1.1. The unchanged local font and its license are included in `assets/Lexend.ttf` and `assets/LEXEND-OFL.txt`. The font is bundled and requires no network request. Upstream: https://github.com/google/fonts/tree/main/ofl/lexend .

## Engine

Godot Engine 4.6.3, MIT license, https://godotengine.org/license/ . Native and web exports embed the Godot runtime and its third-party components. Full engine copyright/license notices: https://github.com/godotengine/godot/blob/4.6.3-stable/COPYRIGHT.txt and https://github.com/godotengine/godot/blob/4.6.3-stable/LICENSE.txt . A copy is included as `assets/GODOT-COPYRIGHT.txt` and `assets/GODOT-LICENSE.txt` in this source and game resources.

Original procedural scenery and synthesized game sounds are part of this project's MPL-2.0 source. No downloaded audio or paid asset pack is used.

## Companion runner atlas (0.2.0)

`assets/companions-runner.png` is a newly generated owner-authorized derivative of the existing wolf/sheep/owl identities, with Aion as the pixel-art style reference. Six columns × six rows contain sequential right-facing running, jumping and gliding poses. It is not the old idle sheet translated across the screen. The generated PNG is unchanged; runtime source rectangles, registered baselines and alpha discard handle alignment/transparency. Provenance and SHA-256: `assets/COMPANION-RUNNER-PROVENANCE.json`. Same MPL-2.0 artwork terms and AI-output limitations apply.

## Full companion sheets (0.3.0)

`assets/owl-runner.png`, `assets/wolf-runner.png` and `assets/sheep-runner.png` are newly generated, owner-authorized derivatives of the same existing character identities with Aion's runner as the pixel-art style reference. Each contains 48 frames: idle, run, jump, freeze, fire/smoke, species-specific ash, ability and landing. Original generated PNG bytes are preserved; atlas rectangles and alpha-discard rendering handle grid spacing/transparency. Provenance, row boundaries, baselines and SHA-256 are in `assets/FULL-RUNNER-PROVENANCE.json`. The same MPL-2.0 artwork terms and AI-output limitations above apply.

## Companion action atlas (0.4.0)

`assets/companion-actions.png` is an original owner-authorized imagegen output using the three 0.3 character sheets as identity/style references. Its 18 frames provide wolf dash, owl updraft wingstroke and sheep jump/landing. Original PNG bytes are unchanged; atlas regions, baselines, scale and SHA-256 are recorded in `assets/ACTION-PROVENANCE.json`. The same MPL-2.0 artwork terms and AI-output limitations above apply. Wind paths are original game code, not baked lines in the image.

## Adventure atlases (0.5.0)

`assets/adventure-combat.png`, `assets/adventure-enemies.png` and `assets/adventure-items.png` are original owner-authorized imagegen outputs: 48 character melee/crouch frames, 36 crow/gnome frames, and 18 item/branch frames. The established Aion/companion identities were used as references. PNG bytes are preserved unchanged; runtime atlas regions, baselines, body heights and alpha discard register the generated grids. Sizes, row boundaries and SHA-256 are in `assets/ADVENTURE-PROVENANCE.json`. Same MPL-2.0 artwork terms and AI-output limitations above apply. Mushroom and gnome artwork is original; no Mario/Nintendo assets or code are used. The alpha shader now avoids multiplying the already sampled texture color a second time.

## Sprite registration (0.6.0)

No new or altered PNG artwork. `assets/SPRITE-REGISTRATION.json` records largest connected opacity-component bounds for the existing original runner, action and combat frames. `packaging/register_sprites.py` reads alpha values and emits only metadata; it never rewrites image bytes. Runtime registration normalizes moving poses and keeps following sheep smaller. Source atlas hashes are recorded alongside these bounds. Czech game text is a new translation for this project, not a third-party asset.

## Evolution atlases (0.7.0)

`assets/evolution-strikes.png`, `evolution-rolls.png`, `evolution-celebrants.png`, and `evolution-barriers.png` are original owner-authorized imagegen outputs. The established mascots are identity/style references; no third-party anime character is copied. They contain 48 alternating strike, 28 roll, 64 fully clothed adult celebration/approach/hug, and 24 overhead-barrier frames: 164 total. The roll atlas actually has seven columns, explicitly registered as such; gameplay loops its five tucked middle poses. Celebrant rows have unequal spacing and explicit boundaries. PNG bytes remain unchanged. `assets/EVOLUTION-PROVENANCE.json` records dimensions, actual frame boundaries, opacity bounds/anchors and SHA-256 hashes. Opacity analysis only generates metadata; runtime crops and uniform scaling render the sprites. Same MPL-2.0 artwork terms and AI-output limitations above apply. Confetti, hearts, wind and smooth spatial color waves are original game code.

## Frontier atlases and runtime frame isolation (0.8.0)

`assets/frontier-heroes.png`, `frontier-boss.png`, and `frontier-parkour.png` are original owner-authorized imagegen outputs, 24 + 36 + 24 = 84 frames. Existing mascot identities/style are referenced. Ash Warden is an original ceramic/brass reactor robot, with no borrowed Sonic/Eggman art or code. The fire plant is original and no Mario artwork/code is used. PNG bytes remain unchanged. `packaging/register_frontier.py` reads alpha components and emits metadata only; regeneration uses Pillow, NumPy and SciPy. `assets/FRONTIER-PROVENANCE.json` records all source hashes, real grid/row boundaries, main-silhouette spans and manually calibrated anatomical reference spans, including old hero atlases. `scripts/frame_bank.gd` copies these spans into separate padded in-memory textures for rendering, preventing cross-frame sampling and discarding unrelated components. Body lean/wing extent no longer drives head scaling. The same MPL-2.0 artwork terms and AI-output limitations above apply. New biome scenery, chase logic and particle effects are original project code.

## Motion atlases (0.9.0)

Ten new AI-generated original PNG sheets contain 997 physically drawn frames. `assets/MOTION-PROVENANCE.json` records original output identity, SHA-256, actual gutters, silhouette spans and common sheet scales. `packaging/register_motion.py` reads alpha without modifying PNGs. The eleven-column world sheet is registered honestly as eleven, without duplicated padding. Hero/art source originals and all historical notices remain. Static ground objects use the prior parkour sheet; active animated poses use the new registry. New future animation sheets require at least ten actual drawn columns; static props are exempt.

## Encounters (0.10.0)

Three new original AI-generated PNGs / 300 drawn frames: 12×8 weapon poses, 12×9 bosses, 12×8 physical defeats. `assets/ENCOUNTERS-PROVENANCE.json` records original output identities, SHA-256, real gutters, silhouette spans, common per-character pair scales and measured muzzle anchors. `packaging/register_encounters.py` reads original alpha; no source PNG is rewritten. The final weapon atlas corrects the preliminary Aion identity to its cyan-tipped gills/blue eyes; only the final atlas is shipped. Historical motion sheets remain.

## 0.11 canonical hero animation artwork

Five new original AI-assisted PNG outputs are included unchanged as canonical-aion/owl/sheep/wolf/rolls.png. The owner explicitly requested fidelity to the four existing character designs. Authorized Drive turnaround references and accepted original runner references are identified in assets/CANONICAL-PROVENANCE.json, which also records source hashes and actual per-row frame boundaries. Runtime crops use silhouette spans, a shared scale per character and anatomical origins; no source PNG is retouched. The dedicated compact roll atlas has eight visually reviewed clockwise angles per hero. Prior artwork remains for provenance and historical fallback.

## 0.12 mobility and contact animations

Two unchanged original AI-assisted PNG outputs, agility-wolf.png and agility-owl.png, add64 drawn poses. Original owner turnaround and accepted canonical references are recorded in AGILITY-PROVENANCE.json along with hashes, silhouette spans and reviewed near-eye registrations. Wolf gallop, bite, claw and sprint bite; owl calm glide, two forward wing attacks and airborne beak. No source PNG is retouched; contact-only claw lines are original runtime drawing. Aion/sheep artwork remains unchanged.
