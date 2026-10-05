## Font Setup for Presentations

All three fonts must be installed in ~/Library/Fonts/ for presentations to render correctly. pptxgenjs references fonts by name — the .ttf files must be installed at the OS level, not just present in this directory.

### Fonts

| Font | Family Name (in code) | Status | File |
|------|----------------------|--------|------|
| Heading Now Trial 04 | `Heading Now Trial 04` | Installed | ~/Library/Fonts/HeadingNowTrial-04*.ttf |
| IBM Plex Serif | `IBM Plex Serif` | Installed | ~/Library/Fonts/IBMPlexSerif-MediumItalic.ttf |
| Steel City Comic | `Steel City Comic` | Installed | ~/Library/Fonts/scb.ttf |

### If fonts stop working

Copy from this directory to ~/Library/Fonts/:

```bash
cp .claude/skills/youtube-presentation/fonts/IBMPlexSerif-MediumItalic.ttf ~/Library/Fonts/
cp .claude/skills/youtube-presentation/fonts/scb.ttf ~/Library/Fonts/
```

Heading Now Trial has many weights already installed. The presentation uses the "04" series (regular width).