# 🇩🇪 Leben in Deutschland Trainer

Interactive web-based trainer for the **Leben in Deutschland** (Einbürgerungstest) question bank.
Practice all 300 general questions + 10 state-specific questions for each of the 16 Bundesländer.

## Features

- **Exam simulation**: 33 timed questions (30 general + 3 state), just like the real test
- **Quick quiz**: 10 random timed questions
- **Learn mode**: All general or state questions with spaced repetition — wrong answers loop back until you get them all right
- **Countdown timer**: Proportional to the real exam (60 min / 33 questions)
- **No peeking**: Answers are hidden during the quiz, revealed in a full review at the end
- **Review screen**: See every question, your answer vs correct answer, filter by wrong only
- **460 questions total**: 300 general + 160 state-specific (10 per Bundesland)

## Installation

```bash
pip install -e .
```

## Usage

```bash
lid-trainer
```

Opens a browser at `http://127.0.0.1:5050`. Select your Bundesland and pick a mode.

```bash
lid-trainer --state Bayern
lid-trainer --port 8080
```

## Question Source

Questions are extracted from the official BAMF *Gesamtfragenkatalog zum Test „Leben in Deutschland"* (Stand: 07.05.2025).
Correct answers verified against the [ebtest.org open-source database](https://github.com/flexsurfer/einburgerungstest).
Images (coat of arms, maps, flags) sourced from the same project under MIT license.

## License

MIT
