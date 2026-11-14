# Hikage-machi H0 research update

[Watch the published video](https://youtu.be/yEJkuDDHtFI). Editable HyperFrames0.9.42 project, local Kokoro synthetic narration and original scientific graphics. Author:Francisco Angulo de Lafuente, ORCID0009-0001-1634-7063.

The film reports data intake:268,154building objects,2,160withLOD2elements and658bus-stop records. Physical exposure, cooling and energy savings remain unvalidated. It is not a finished application or a final contest submission.

Re-render from this directory with Node22+ and FFmpeg installed:

```bash
npx hyperframes@0.9.42 check
npx hyperframes@0.9.42 render --quality delivery --workers 1 --no-browser-gpu --output rerender.mp4
```

Audio, fonts, figure and GSAP are local assets; no model weights, accounts or paid services are needed to rerender. To regenerate the city plot rather than reuse the provided figure, reproduce H0 from the repository's h0/ instructions. Source audio gain0.707945784 is the -3dB correction for the renderer's mono-to-stereo conversion. Final MP4 audio was finished with video stream copying; AUDIO_FINISHING.json records the change.

Code and original text:MIT. City graphic:Takamatsu City / MLIT PLATEAU and Kotoden Bus, CC BY4.0, processed by Francisco Angulo de Lafuente into extent-centre/stop plots. Kokoro model:Apache-2.0; kokoro-onnx:MIT. Fonts and GSAP retain their own licence notices. No person was cloned; no soundtrack is included. See NOTICE.md and the font licence in assets/fonts/.

QA.json and RENDER_VERIFICATION.json distinguish technical checks, direct frame inspection, the limited independent text review and the absence of subjective listening. CAPTION_RECEIPT.json documents four terminology/name corrections against the narration input and word-level ASR timing. The original review finding about missing visible synthetic-voice disclosure was fixed and verified in all scenes.
