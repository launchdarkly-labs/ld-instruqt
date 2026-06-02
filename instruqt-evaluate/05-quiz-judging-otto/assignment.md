---
slug: quiz-judging-otto
id: smdty549odhh
type: quiz
title: Quiz — Judging Otto
teaser: A quick check on what you just built — offline evaluations, built-in
  judges, and custom judges.
notes:
- type: text
  contents: Pause and consolidate. The next question is about the relationship
    between Otto's prompt and the brand-voice judge you just wrote.
answers:
- The brand-voice judge calls Otto's variation under the hood and inspects its
  output, so the prompt is implicit.
- Both Otto's prompt AND the judge's grading criteria reference the same
  `brand-voice` snippet, so changing the snippet updates both at once.
- The judge fetches Otto's prompt from the LaunchDarkly SDK at evaluation time
  and inlines it into the grading rubric.
- LaunchDarkly's backend automatically syncs prompt text between a Config and
  any judges attached to it.
solution:
- 1
difficulty: ""
timelimit: 600
enhanced_loading: null
---
You've spent four challenges grading Otto in different ways — offline against a labeled dataset, then live with built-in and custom judges. The custom brand-voice judge in Challenge 03 used a deliberate trick to keep "what Otto does" and "what we measure" from drifting apart.

# One question

What made the brand-voice judge stay in sync with Otto's own definition of "on-brand"?
