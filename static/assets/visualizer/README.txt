Place the mask image file here named `lips_mask_clean.png`.
This file is used by the bee swarm voice visualizer to create particle animations.
Recommended specs:
- Dimensions: 800x600 (transparent background)
- Solid opaque lips silhouette in white or #ffe08a (will be thresholded)
- Keep edges soft for better sampling variance.
If you replace with a different filename, update `maskUrl` in the visualizer initialization options inside templates `quiz.html`, `speed_round_quiz.html`, and `magical_quiz.html`.
