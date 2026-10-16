# Plex UI cross-platform study → Mediaphile interaction contract

**Research date:** 2026-10-07. **Scope:** public Plex documentation, Plex product/blog pages, current official forum release notes, and public Plex client source reviewed previously. This is behavior/reference research, **not** a hands-on hardware qualification or authorization to reproduce Plex artwork, branding, CSS, or code.

## Owner-approved invariant: ONE LAYOUT ON EVERY PLATFORM

**2026-10-07 live user decision:** Mediaphile must use **one consistent layout** across desktop, mobile, tablet, television, console, and future native wrappers. Platform differences are limited to sizing, input devices, and media decoding capabilities, not rearranging primary navigation or changing the information architecture.

- One **left navigation rail** at every screen width. On narrow screens it becomes a persistent icon-width rail in the *same location*, with identical destinations and accessible names; do not introduce bottom navigation, mobile-only tabs, or a parallel UI.
- One top header and one route/content hierarchy; same Home, Movies, TV Shows, Search, Settings, details, playback.
- Posters, library selection, sorting, filtering, and playback controls remain located within the same content hierarchy; control dimensions may adapt to touch or remote input.
- Responsive CSS can change column counts, spacing, font sizing, and focus/touch targets without changing navigation placement.
- Hardware-native wrappers may change media engine and remote controls, never the layout contract.
- Different Plex layouts are independent **research observations**, not design prescriptions.

## Evidence classes used here

- **O (official documented behavior):** Plex support documentation, launch posts, dated release notes; linked below.
- **R (reasoned Mediaphile design interpretation):** recommended product behavior; not a claim of Plex implementation details.
- **U (unverified device behavior):** would require contemporary in-person testing or screenshots from a particular version/device. In particular, Plex 2025-26 *preview* and production navigation differ. Never treat a preview UI as universal.

## Platform matrix (documented / inferred)

| Surface | Plex UI evidence (O) | Mediaphile design implication (R) | Explicit limitation |
|---|---|---|---|
| Browser Plex Web (Chrome/Firefox/Safari/Edge) | Left source sidebar; top Back/Home/Search/Status/Settings/Players/Account; Home recommendations; media card hover actions; library top controls for filtering, sorting, item type, poster size, grid/list/summary. [1][2] | Persistent desktop sidebar, prominent search, media-first cards; server-side paginated sorting/filtering, keyboard navigation; no cloud/status noise when unavailable | Browser codecs and HLS differ, cannot infer native client playback from Web UI |
| Plex for Windows/macOS/Linux desktop | Web-like navigation with more robust native playback, OS audio/output settings and offline downloads. [3] | Same desktop information architecture; later native wrapper can add hardware decoding, exclusive output/device controls | A web page alone does not provide native mpv-class capabilities |
| Android/iOS phone | Home header with Search/Cast/Watchlist/account, curated rails, **bottom source navigation**, library picker, horizontal Recommended/Browse/Collections/Categories subsections. [4] | Keep the shared left sidebar on narrow screens with icon-width mode, reachable search and library switcher, large tap targets, sticky browse actions | Modern 2026 apps remove Browse Libraries home row and open library picker on Libraries click; not assume older flow [5] |
| iPad/tablet | Mobile information architecture likely scales through layout rather than adopting every TV affordance | Same left-side navigation and information hierarchy; adapt only rail width and content density | No first-hand 2026 iPad audit performed |
| Apple TV/tvOS | TV remote focus model, preplay/details, D-pad, modernized player and seek previews in preview; Aug 2026 preview returns **collapsible left sidebar** [6][7] | The same left focus rail at 10-foot widths, visible/high-contrast focus ring, deterministic focus return, TV-style episode navigation, explicit seek state | Preview != all production builds |
| Android TV / Google TV / NVIDIA Shield | Big-screen sidebar and home rails; Aug/Sep 2026 beta/changes emphasize stable focus, fast library scrolling and player/audio-subtitle behavior [6][8] | Focus retention after asynchronous loads, virtualization in large poster grids, fast directional scrolling | Device decoders, HDR, refresh-rate switching are not browser-equivalent |
| Amazon Fire TV / Fire Stick | Big-screen UI; September 2026 rollout shows side navigation; focus and slower-device scrolling matter [8] | Bound CPU/DOM work, preload visible artwork only, avoid costly animation and jumping focus | Fire TV app update timing is not identical across devices |
| Roku | Roku preview moved primary nav **back to left** in Aug 2026, reversing Nov 2025 top-nav stance; focus/audio accessibility are recurring concerns [9][10][11] | Same permanent left rail, consistent remote focus and quick source switching | Roku requires a separate native client; no browser-on-Roku deliverable implied |
| Smart TV (Samsung/LG supported models) | Listed among big-screen Plex apps using sidebar, recommended/library/collections/playlist/category structure [12] | 10-foot interactions, safe-area, remote Back, memory-aware grids | Exact Tizen/webOS behavior and codec support not independently validated |
| Xbox / PlayStation | Big-screen sidebar interface listed by Plex [12] | Gamepad A/select, B/back, shoulder tab shortcuts could map to existing focus navigation | Actual controller mapping needs each platform runtime |
| Plex HTPC | Listed big-screen client; PC-based playback can expose output/hardware capabilities [12] | Prefer native player wrapper when home theater audio, subtitle, frame rate requirements exceed browsers | Do not overclaim browser-only feature parity |
| Chromecast / AirPlay casting | Mobile UI can choose a target, return to browsing while using phone as remote; Chromecast target streams from server rather than through phone [13] | Later LAN cast receiver/controller protocol with session handoff; browser UI must not promise it before receiver exists | Casting not implemented in Mediaphile v1 |
| Plexamp / Plex Photos / Plex Dash companions | Plex separated music, photos, dashboards from primary movie/TV experience [14] | Keep V1 Movies + Shows focused; reuse design tokens for future first-party companion surfaces | Out of Mediaphile movie/TV V1 scope |

## Detailed screen/behavior inventory

### Home / discovery
- **O:** Personalized Home starts with Continue Watching, then per-library recommendations/recent additions, then optional other sources. TV Home often displays rows rather than a giant undifferentiated grid. [4][12]
- **R:** Mediaphile Home must foreground (1) Continue Watching, (2) Recently Added Movies, (3) TV Shows / Next Up. No fake recommendations, streaming promotions, Live TV, or content advertising.
- **R:** Favorited **local** libraries control available Home rows; no online-source category.

### Library / source navigation
- **O:** Web library toolbar offers All/Unplayed/Duplicates, view type, filter composition, sort ascending/descending, poster-size control, grid/list/summary, and folder browsing [2]. Current mobile library picker explicitly opens when selecting Libraries [5].
- **R:** V1 implement source library selection, All/Unplayed/In Progress/Watched where actual playback state exists, title/year sort, grid/list, pagination; defer duplicate grouping, collections and folders until backend supports them. Never silently limit a 943-movie library to the first 200.
- **R:** Save view preferences locally, not bearer tokens; server-owned filtering must use authenticated principal, not a caller-selected user ID.

### Details / preplay
- **O:** Artwork-rich details and player affordances plus collection associations and cast/credits are expected; Android/iOS refresh introduced expanded artwork and title art [15].
- **R:** Hero identity, local poster/backdrop if actually present, explicit Play/Resume, edition/quality/codec, show → season → episode, provenance evidence panel. Unknown artwork or cast remains absent rather than guessed.
- **R:** Media info remains server-probed fact; source analysis requires its evidence class.

### Player / OSD / controls
- **O:** Contemporary apps provide seek preview, subtitle/audio preferences and increasingly fine focus feedback; playback controls differ between TV/mobile/native platforms [7][8].
- **R:** Unified conceptual state: preparing, playing, paused, buffering, ended, error. TV D-pad shows OSD; Enter toggles; Left/Right seek (not silently skip to another title). Mobile taps show controls; keyboard space toggles playback. Explicit subtitle/audio selection only when server supports selected streams.
- **R:** Direct Play/Remux/Transcode diagnostic belongs in advanced playback info, not as intrusive persistent UI; no autoplay-next without user preference.
- **U:** Chapter thumbnails, skip-intro, trick-play hover previews, HDR/exclusive audio/refresh switching need distinct feature work and media analysis.

### Platform focus and accessibility
- **O:** Sep 2026 release fixes focus jumping from asynchronously loaded detail screens, off-screen grid focus, sluggish scrolling, and missing focused state [8]. Roku release notes separately fix focus restoration and speech feedback [11].
- **R:** Stable focus ID instead of DOM order alone; preserve focus when loading finishes; never focus an invisible item; restore origin on Back; visible focus on TV; native tab and screenreader semantics on desktop; 44×44 CSS-pixel minimum touch affordances on mobile.
- **R:** Client must not assume hover exists on touch; hover actions always accessible from keyboard/touch.

### States / failures
- **R:** Empty library must show setup/scan guidance, not blank tiles. Network loss must offer reconnect without dropping credentials into logs. Background scan should never freeze controls. Codec unsupported should show exact server reason plus alternate source/quality where available.
- **R:** Artwork aspect ratios and placeholder boxes must remain stable while images load; this directly addresses Plex 2026 browse layout-shift fixes [5].
- **R:** No client-facing WAN URL or Internet asset dependency; all styling/assets must come from local bundle/server.

## Immediate implementation delta by repository

**`mediaphile-client`**
1. Enforce the **single shared left-navigation shell** on every viewport. Narrow screens use a vertical icon rail at the same left edge; NEVER introduce a mobile bottom bar or second primary navigation system.
2. Add library picker and per-library browse state. Add All/Unplayed/In Progress/Watched, Grid/List, stable load-more pagination; display per-item state honestly.
3. Add tests for filtering controls, data-focusable navigation and mobile semantics, and e2e alternate library flow. Avoid exact Plex color/artwork cloning.
4. Later: poster artwork served by server, accessibility/grid virtualization, advanced player OSD.

**`mediaphile-server`**
1. Extend `GET /api/v1/items` with authenticated-principal playback-state filters; retain opaque cursor and stable sort.
2. Add `GET /api/v1/users/me/playback` summary only if Home Continue Watching needs non-N+1 state, or explicitly defer until API design.
3. Update OpenAPI and tests together. Do not expose raw DB paths, other users' playback state or a publicly open browse endpoint.
4. Later: collection definitions, artwork serving/caching, sort variants and media extras.

**`mediaphile` (private corpus)**
1. Preserve this source-grounded cross-platform UI research and cross-repo behavior contract as *design evidence*, not reviewed audiovisual facts.
2. Track actual server/client commit and OpenAPI digest once verified; never assert this research document is proof of running devices or source import.
3. Retain corpus provenance rules and keep original ingestion PR #5 and screenplay PR #6 independent/unmerged.

## Validation matrix

- Desktop (Chromium and Firefox): sidebar, keyboard, list/grid, pagination, playback, recoverable no-server view.
- Mobile simulated viewports (375×812, 390×844; touch): **same left rail**, visible library picker, search, header safe-area, no horizontal overflow.
- 10-foot simulated 1920×1080 with keyboard arrows: focus visible, row transitions, back/return from detail/player.
- Narrow tablet 768px and wide desktop 1440px: no navigation overlap or hidden menus.
- Real Roku, tvOS, Fire TV, Android TV, consoles, Tizen/webOS, Chromecast/AirPlay: **not qualified until separate native clients and hardware trials exist**.
- Integration: real Mediaphile Server process with synthetic local movie + authorized user, then browser browse → play → seek/resume; cannot substitute mocked API E2E.

## Sources

[1] https://support.plex.tv/articles/200484203-interface-overview/ (web/desktop UI)
[2] https://support.plex.tv/articles/200392126-using-the-library-view/ (filters, sort, grid/list)
[3] https://support.plex.tv/articles/windows-and-macos-intro-installation/ (desktop)
[4] https://support.plex.tv/articles/navigating-the-mobile-apps/ (mobile)
[5] https://forums.plex.tv/t/plex-for-mobile-tvs-android-mobile-ios-android-tv-tvos-fire-tv/909610/58 (2026-09-28)
[6] https://forums.plex.tv/t/navigation-updates-coming-to-preview-users/941751/1 (2026-08-17 preview)
[7] https://forums.plex.tv/t/release-notes-for-plex-experience-preview-apple-tv/903004
[8] https://forums.plex.tv/t/plex-for-mobile-tvs-android-mobile-ios-android-tv-tvos-fire-tv/909610/56 (2026-09-16)
[9] https://forums.plex.tv/t/plex-for-roku/9463/528 (2026-08-17)
[10] https://forums.plex.tv/t/plex-roku-preview-a-faster-simpler-navigation-experience/933212 (2025-11-05, historical comparison)
[11] https://forums.plex.tv/t/plex-for-roku/9463/490 (2026-01-21)
[12] https://support.plex.tv/articles/navigating-the-big-screen-apps/ (TV/HTPC/console/smart-TV)
[13] https://support.plex.tv/articles/chromecast-airplay-and-casting/ (casting)
[14] https://www.plex.tv/blog/the-future-of-plex-focused-streamlined-and-ready-for-feedback/ (dedicated media apps)
[15] https://www.plex.tv/en-ca/blog/the-new-plex-experience/ (artwork and mobile launch)

*These URLs provide attributable design research, not evidence that Mediaphile currently implements the capabilities listed.*
