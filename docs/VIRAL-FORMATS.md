# Viral ski reel formats

Instagram scan, 19 Oct 2026. Views are as shown on the profile Reels grid that day.

| Reel | Account | Views | Format |
|---|---|---|---|
| C6Y5B6iCh53 | redbullsnow | 39.5M | Spectator phone clip, a skier passes centimetres away. One line on top, lowercase bold: "as close as it gets 😳" |
| DIWKOR4NKkQ | redbullsnow | 17.5M | Drone follows the rider into a halfpipe. Top line "all in for the shot". The caption is a mini dialogue: "Nico: can you hit me with your drone? Drone pilot: ..." |
| DePFdHRNPnQ | redbullsnow | 17.4M | First-person POV from smart glasses: "POV: You're opening the winter season Red Bull style" |
| DeO82FMIPPv | nadinemoore | ~3K likes, small account | Raw ski-touring clips, white serif text in the middle, one line per clip: "Still going." / "Be the person people look at and say:" / punchline |
| Ddy4czwCxxQ | blackcrows_skis | 122K (account average ~20K) | 360/POV straight down a couloir, ski tips in frame, no text |

The account average is 60–400K views, so the outliers are 50–100× higher. They all share these traits:

1. **One short line of text in the first second**, lowercase, at the top or in the middle. It never explains anything. It names a feeling ("as close as it gets", "still going").
2. **A raw, first-person feel**: phone, POV, drone-follow. Polished edits are not what goes viral.
3. **7–15 seconds**, built around one moment, with no logo and no CTA in the video.
4. **The caption carries the joke or the story** (dialogue, "POV: ..."), and the video carries the feeling.
5. **People tag a friend**: it is about identity ("that's you"), not about the product.

## What Wildr has (Drive «Wildr video»)

- HoverAir drone follow (HOVER_2025122x, 40–220 MB) gives the "all in for the shot" format.
- iPhone POV and tree runs (IMG_45xx/47xx/48xx/87xx).
- Thien's 360/GoPro files (20260122_17xxxx, 0.5–3.7 GB, raw, need reframing) give the couloir/POV format.
- Guest clips from WhatsApp (VID-2026xxxx-WAxxxx, compressed). These suit "front row" and laughs, not image quality.

Renderer: `scripts/reel.py` (video segments + text times). Add a serif centre style for the "Still going" format.
