# Android Interview Handbook

A free, interactive interview guide for Android developers. It covers Kotlin, architecture, coroutines and Flow, Jetpack Compose, debugging and performance, coding-round patterns, system design, and how to answer questions about experience gaps.

**Read it online:** https://jaidattar.github.io/android-interview-handbook/

## Contents

1. Kotlin Essentials
2. Android Architecture
3. Coroutines & Flow
4. Jetpack Compose
5. Debugging & Performance
6. Data Structures & Algorithms in Kotlin
7. System Design & Architecture
8. Answering Honestly About Gaps

Each topic has a model answer, the phrases to say out loud, and the traps and follow-ups interviewers use.

## Build locally

The book is generated from the chapter files in `src/`:

```bash
python3 build.py      # writes the website to site/
open site/index.html  # or open it in any browser
```

No dependencies beyond Python 3. Edit a file in `src/`, rebuild, and refresh.

## Structure

- `src/` chapter content (one HTML fragment per chapter)
- `assets/` shared stylesheet and script
- `build.py` chapter list, titles, takeaways, code highlighting, and navigation
- `.github/workflows/pages.yml` builds and publishes to GitHub Pages on each push to `main`

## License

Choose a license before publishing (for example, CC BY-NC 4.0 keeps it free to read while preventing resale).
