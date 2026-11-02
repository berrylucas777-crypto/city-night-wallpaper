---
name: city-night-wallpaper
description: Find real Pexels city nightscape photographs, rotate cities and atmospheres, and set a screen-sized macOS desktop wallpaper. Use when asked to change city wallpaper or configure recurring city wallpaper changes; no AI-generated images.
---

# City night wallpaper

Use real photographs from Pexels only. Prefer high-resolution landscape cityscapes from elevated viewpoints: dense lights, skyscrapers, neon, light trails and cinematic Spider-Man-like atmosphere. Rotate New York, Toronto, London, Paris, Tokyo, Hong Kong, with Shanghai, Dubai, Singapore, Chicago and Seoul as alternatives. Honor the user's city preferences.

The helper is `wallpaper.py` relative to this skill. Run it with Python 3; no Python packages or Pexels API key are required. Automatic desktop application supports macOS only and uses the main display's resolution for all currently exposed desktops. Inactive Spaces may need separate application. On other operating systems explain this limit before attempting application.

1. Run `python3 <helper> screen` and `python3 <helper> history`. Choose a city different from recent entries and vary weather/time atmosphere. If the host automation has its own memory, read that too.
2. Search the web or browse Pexels for that city, including “night”, “blue hour”, “aerial”, or “dusk”. Open each promising photo's actual Pexels page. Confirm city, photographer, original dimensions and photographic provenance (camera/capture metadata when available). Never infer a city solely from an image filename. If provenance is doubtful, choose another photograph.
3. Download a preview from the photo's Pexels CDN and visually inspect it with the host's image viewer. Exclude watermarks, overlays, prominent text/logos, implausible details, heavy reflections, blur, distortion, and severe crop. The helper does not authenticate photography or make aesthetic decisions. `--reviewed` records your review; it is not an AI detector.
4. Prefer originals at least as large as the screen and with a close landscape aspect ratio. The helper downloads a center crop at exact screen dimensions; choose a different photo if this would remove essential subjects or more than roughly 15% of the image area. Do not generate, outpaint or AI-retouch imagery.
5. Once the user has requested a wallpaper change, run:

   ```sh
   python3 <helper> apply 'https://www.pexels.com/photo/PHOTO-SLUG-ID/' \
     --city 'Tokyo' --mood 'rainy neon night' \
     --photographer 'Name from source page' --reviewed
   ```

   For a preview without applying, add `--download-only`. Inspect that exact downloaded file before applying if crop suitability is uncertain. Successful applications are verified by delayed system readback and saved to history. If permission is denied or verification fails, report it honestly and do not claim success. Do not automatically retry a failed mutation indefinitely.
6. Briefly report city, atmosphere, photographer, Pexels page link and whether application succeeded. Do not publish or redistribute downloaded photographs as part of the tool.

For recurring requests, use the host application's scheduling mechanism only when requested. Save the full selection and application workflow in the scheduled prompt; do not schedule a blind fixed-photo CLI call. This skill alone does not create a background scheduler. Never claim a schedule exists without creating and verifying it.
