# CSC 4850 Final Project — Submission Checklist

Our presentation day: **Monday, November 30** (presentation order 1–7).

## Deadlines

| Date | What | Who submits | Status |
|---|---|---|---|
| Mon **Nov 30**, before class | **Slides** (one upload per team) | one teammate for the team | draft deck ready to edit → [presentation/GrievAIance_Final_Presentation.pptx](presentation/GrievAIance_Final_Presentation.pptx) (plan and notes: [PRESENTATION_GUIDE.md](presentation/PRESENTATION_GUIDE.md)) |
| Mon **Nov 30**, class | **Present**: 10 min ± 1, then 2–3 min Q&A | all three | rehearse twice before |
| Wed **Dec 2**, class | Attend the other presentations (required) | everyone | — |
| Thu **Dec 3**, 11:59 pm | **Final report**, IEEE conference format | **each student separately** | draft ready → [final_report/final_report.pdf](final_report/final_report.pdf) |
| Thu **Dec 3**, 11:59 pm | **Confidential peer evaluation** (form not posted yet) | each student separately | only you can fill it out |
| Mon **Dec 7**, class | Attend the last presentations; **post-test** (no prep needed; up to 20 points added to your lower exam score) | everyone | — |

(The announcement says the last groups present on "December 3" in one place and "December 07" in
another; it doesn't affect us, but attendance on Dec 7 is required either way because of the
post-test.)

## Slides: before Nov 30

- [ ] Put the draft deck in one shared place (OneDrive or Google Drive) so all three of you edit
      the same copy.
- [ ] Rework the draft in your own words and style (AI-generated slides are penalized). Keep it
      high-contrast: white background, dark text, slide numbers.
- [ ] Required content: problem/motivation · methods/algorithms · dataset · results vs. baselines ·
      future directions (all mapped in the guide).
- [ ] Agree on who presents which slides (the guide suggests a three-way split of about 3:20 each).
- [ ] Two timed run-throughs (target 9:30–10:30), then practice the Q&A bank.
- [ ] Submit the slides before class Nov 30; keep a PDF copy on a USB drive.

## Final report: before Dec 3

- [ ] **Check the instructor's upcoming formatting and content announcement** and adjust the draft
      (page limit, required sections, e.g. a team-contribution statement or an appendix). The
      draft is 5.6 pages (the proposal promised 5–7) and already has an ethics paragraph and a
      link to the code.
- [ ] Edit the report together, choosing **one** of the two copies (edits to one don't carry over
      to the other):
      - **Word:** [final_report/final_report.docx](final_report/final_report.docx), the same report
        in IEEE conference style (two columns, Times New Roman, real Word equations). Put it in
        OneDrive or Google Drive so all three of you edit the same copy, and export to PDF to submit.
      - **LaTeX:** upload [final_report_overleaf.zip](final_report_overleaf.zip) to Overleaf (New
        Project → Upload Project) and share the project. Overleaf works in the browser, lets all
        three of you edit at once, and rebuilds the PDF for you.
- [ ] Read the whole draft and revise it in your own words. It's submitted individually, so make
      sure you can explain every part of it.
- [ ] Confirm the author block (all three names, as in the mid-report) is what the instructor
      wants for individual submissions. Student emails are left out because the GitHub repo is
      public; add them to your own submitted copy if you want them (a line like
      `yourid@student.gsu.edu` after `Atlanta, GA, USA\\` in each author block).
- [ ] Rebuild the PDF after edits (Overleaf does it automatically), or run Tectonic locally
      (command below).
- [ ] Submit the PDF by Dec 3, 11:59 pm.

```powershell
& "$env:LOCALAPPDATA\Programs\tectonic\tectonic.exe" report\final_report\final_report.tex
```

## Peer evaluation: before Dec 3

- [ ] Fill out and submit the confidential form when it's posted (individually, with the report).

## Where everything is

| File | What it is |
|---|---|
| `report/final_report/final_report.tex` / `.pdf` | final report, IEEE two-column (IEEEtran) |
| `report/final_report/final_report.docx` | the same report as an editable Word file in IEEE conference style |
| `report/final_report_overleaf.zip` | the same source and figures, ready for Overleaf |
| `report/presentation/GrievAIance_Final_Presentation.pptx` | draft slide deck (16 slides, speaker notes), editable PowerPoint |
| `report/presentation/PRESENTATION_GUIDE.md` | slide plan, speaker notes, timing, design rules, Q&A bank |
| `report/presentation/figures/` | all slide figures (white background), including the demo screenshot |
| `report/presentation/make_slide_figures.py` | regenerates the two slide charts from `results/metrics/` |
