CHEMSCAN AR - CSC 633 Course Project

WHAT IT DOES
A warehouse worker points a camera at a printed product label. The app recognizes the label
with image tracking, puts a colored QC status badge on the label itself (green Released,
yellow On Hold, red Expired), and shows that lot's details in a large, high-contrast panel
at the bottom: QC status, expiration/retest date, lot number, and storage.
The panel stays on screen when the label leaves the camera, and clears when you tap
"Scan Next" or show a different label.
All products and data are fictional (food and pharmaceutical ingredients).

BUILT WITH
HTML, CSS, JavaScript, A-Frame 1.5.0, and MindAR 1.2.5 (image tracking), loaded from CDN.
No build step and no backend.

FILES
index.html      The page and the AR scene (one target entity per label)
app.js          Loads products.json, colors the AR badges, shows/clears the details panel
style.css       Dark, large-text styling
products.json   The 3 lot records (ERP-style). Array order = target index 0, 1, 2
targets.mind    The 3 labels compiled for MindAR, in the same order as products.json
labels/         The 3 label images to print
tools/          make_labels.py (draws the labels), compile-targets.html (rebuilds targets.mind)

HOW TO RUN
1. Extract the folder.
2. Start a local server in the folder. Either:
   - VS Code: right-click index.html, "Open with Live Server", or
   - Command line: python -m http.server 8000, then open http://localhost:8000
   (Opening index.html directly as a file will not work; it needs a server.)
3. Allow camera access when the browser asks.
4. Hold a label up to the camera.

The camera only works on localhost or HTTPS. To use it on a phone, host the folder on
an HTTPS site such as GitHub Pages.

PRINTING THE LABELS
Print the PNGs in labels/ at about 4 x 3 inches, on plain white paper.
Matte paper and even lighting work best. Glare makes tracking harder.
Showing a label on a second screen also works for quick testing.

IF YOU CHANGE THE LABELS
Run python tools/make_labels.py, then open tools/compile-targets.html through the local
server, click Compile, and save the downloaded targets.mind next to index.html.
Keep the label order the same as products.json.
