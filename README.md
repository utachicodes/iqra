# IQRA - DMSA Quranic Letter Wheel

Iqra is an interactive Islamic game built with Pygame. The game helps players practice Quranic recitation by randomly selecting an Arabic letter and challenging them to recite an Ayah that starts with the chosen letter.

## Features

- **Arabic Letter Wheel**: A spinning wheel containing all Arabic letters.
- **Multiplayer Mode**: Two players can participate and take turns.
- **Scoring System**: Players earn points by correctly reciting verses.
- **Beautiful UI**: Uses a custom Arabic font and smooth animations.
- **Easy Controls**: Simple button clicks for spinning and scoring.

## Installation

### Prerequisites
- Python 3.x
- Pygame library
- `arabic-reshaper` and `python-bidi` for proper Arabic text rendering

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/utachicodes/iqra.git
   cd dmsa-quranic-wheel
   ```
2. Install dependencies:
   ```bash
   pip install pygame arabic-reshaper python-bidi
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## How to Play
1. **Enter Player Names**: The game starts by asking for two player names.
2. **Spin the Wheel**: Click the **SPIN** button to randomly select an Arabic letter.
3. **Recite a Verse**: The selected player must recite a Quranic Ayah that starts with the chosen letter.
4. **Score Points**:
   - Click **✓ Correct** if the answer is correct (gain 1 point).
   - Click **✗ Wrong** if incorrect (no points awarded).
5. **Win the Game**: The first player to reach 5 points wins!


## Dependencies
- [Pygame](https://www.pygame.org/)
- [Arabic Reshaper](https://github.com/mpcabd/python-arabic-reshaper)
- [python-bidi](https://github.com/MeirKriheli/python-bidi)

## Contributing
If you'd like to improve this game, feel free to fork the repository and submit a pull request.

## License
This project is open-source and available under the MIT License.



