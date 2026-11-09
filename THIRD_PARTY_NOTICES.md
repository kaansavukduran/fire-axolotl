# Üçüncü taraf bildirimleri / Third-party notices

## Linux AppImage runtime and packaging

Linux installer inputs and hashes are pinned in `linux-packaging.json`. AppImage type2 runtime commit `fedfad51acc2860b2916a1eef32ba4a500ff31ef` is MIT licensed and statically links libfuse (LGPL), squashfuse (BSD), musl (MIT), zstd (BSD), zlib and mimalloc (MIT). Runtime/library notices are included under `usr/share/doc/fire-axolotl-preview/licenses` in the Linux packages. The separate AppImage support-source archive contains runtime source, the pinned libfuse 3.15.0 source and patch/build/link scripts, squashfuse source, and permissive-library source/support material. The runtime can be rebuilt and relinked against a modified libfuse. The appimagetool build tool is not embedded in the browser payload.

AppImage runtime ve kitaplıklarının lisansları korunur; statik LGPL bileşeninin kaynağı ile yeniden derleme/bağlama betikleri ayrı destek kaynak arşivinde sunulur. Paketleme imzalı otomatik güncelleme altyapısı anlamına gelmez.

## Mozilla Firefox / Gecko

Upstream: https://archive.mozilla.org/pub/firefox/releases/153.6.0esr/source/firefox-153.6.0esr.source.tar.xz

Mozilla source code is primarily under Mozilla Public License 2.0, with additional component licenses. The complete pinned source retains its `LICENSE`, `browser/LICENSE`, `about:license` resources, copyright headers and third-party notices. This overlay does not relicense those components or remove the source notices. Modified files remain available with the overlay and exact upstream source reference.

Firefox and Mozilla are trademarks of the Mozilla Foundation. Fire Axolotl is not officially associated with Mozilla or its products. Upstream branding filenames retained for build compatibility do not grant permission to use the Firefox logo as this product's identity.

## Lexend

Source: https://github.com/google/fonts/tree/main/ofl/lexend

Copyright 2018 The Lexend Project Authors. SIL Open Font License 1.1, including its reserved-font-name provisions. Original font file and full license are included in `browser/extension/fonts/`. The font was not renamed or modified. Turkish glyph support was verified from the font's cmap table.

## OpenDyslexic

Unmodified OpenDyslexic Regular and Bold font files from author repository snapshot `1824da5c0e41dc3e13ffc7f3a636dcaf695d61b7`: https://github.com/antijingoist/opendyslexic/tree/1824da5c0e41dc3e13ffc7f3a636dcaf695d61b7

Copyright Abbie Gonzalez, Reserved Font Name OpenDyslexic. SIL Open Font License 1.1; the full notice is included as `browser/extension/fonts/OpenDyslexic-OFL.txt`. The author's current project home is https://opendyslexic.org/ and source host is https://forge.hackers.town/antijingoist/opendyslexic. This project uses the recorded author-published snapshot, not a claim to the newest font release. Both included font files were verified for Çç Ğğ Iı İi Öö Şş Üü. File hashes are in `fonts/SOURCES.json`. No medical efficacy claim is made.

## Aion artwork

The project owner confirmed that the Aion character reference sheets were generated with ChatGPT. The Fire Axolotl icon was generated from those user-supplied references in this development session, rather than downloaded from a third-party asset library. Generated output may be non-exclusive and copyright protection varies by jurisdiction. No guarantee of exclusivity, trademark registration or non-infringement is made.

The project source license applies to the repository's original Aion artwork to the extent the project owner holds licensable rights. It grants no Mozilla or OpenAI trademark rights. See `branding/PROVENANCE.md`.

## Existing extension names

Bitwarden, DeepL, DuckDuckGo, Enhancer for YouTube, Firefox Multi-Account Containers, Global Speed, Netflix 1080p UA, Search by Image, Temporary Containers, uBlock Origin, Dark Reader and QR Code identify existing tools from a user-supplied screenshot. Their code, icons and store screenshots have not been copied into the repository. Mentioning them does not imply affiliation or endorsement.

## uBlock Origin

uBlock Origin 1.76.0, Copyright Raymond Hill and contributors, GPL-3.0-or-later. The unmodified official signed Firefox package is fetched and hash-verified at build time, separately from the MPL-licensed Aion companion. `components.json` pins its package, source, submodules and uAssets revisions. The native distribution includes complete corresponding source and retained component/list/library/font notices in `distribution/sources/`. See [COMPONENTS.md](docs/COMPONENTS.md) for reproduction and network/permission details. Its authors do not endorse Fire Axolotl.

## Companion artwork

The owner explicitly authorized using their existing custom Aion ChatGPT Pet and generating matching cartoon companions for this browser. The Aion PNG is unchanged; the lamb, wolf and owl frames were generated from the owner's character references, then registered and encoded without drawing procedural bodies. Source/packaged hashes and transformations are in `browser/extension/characters/PROVENANCE.json`. Built-in ChatGPT pet artwork such as Dot is not bundled. The artwork licensing limits described above also apply to these generated frames.

Future reused components require a recorded source version, license compatibility review, retained notices and appropriate source availability. Free download alone does not establish redistribution rights.
