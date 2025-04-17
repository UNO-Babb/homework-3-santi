#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, redirect, url_for
import random
import os

app = Flask(__name__)

BOARD_SIZE = 20

# Symbols
TREASURE = 'T'
TRAP = 'X'
MYSTERY = '?'

# Default player data
players = {
    'Player 1': {'position': 0, 'score': 0},
    'Player 2': {'position': 0, 'score': 0}
}

current_turn = 'Player 1'
board_events = {}  # tile_number: event_symbol

# Read saved game state from file
def load_game():
    global current_turn, players, board_events
    if not os.path.exists('events.txt'):
        return

    with open('events.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("Turn:"):
                current_turn = line.split(":")[1].strip()
            elif ':' in line:
                space, value = line.split(":")
                space = int(space.strip())
                value = value.strip()
                if value in ["Player 1", "Player 2"]:
                    players[value]['position'] = space
                elif value in [TREASURE, TRAP, MYSTERY]:
                    board_events[space] = value

def save_game():
    with open('events.txt', 'w') as f:
        f.write(f"Turn: {current_turn}\n")
        for name, data in players.items():
            f.write(f"{data['position']}: {name}\n")
        for space, event in board_events.items():
            f.write(f"{space}: {event}\n")

def roll_dice():
    return random.randint(1, 6)

def apply_event(player, position):
    event = board_events.get(position)
    if event == TREASURE:
        players[player]['score'] += 2
    elif event == TRAP:
        players[player]['score'] -= 2
    elif event == MYSTERY:
        change = random.randint(1, 3)
        if random.choice([True, False]):
            players[player]['score'] += change
        else:
            players[player]['score'] -= change

def push_back_player(loser_player):
    if players[loser_player]['position'] > 0:
        players[loser_player]['position'] -= 1
        # Check if pushback causes another collision
        for other, data in players.items():
            if other != loser_player and data['position'] == players[loser_player]['position']:
                push_back_player(other)

@app.route("/")
def index():
    return render_template("index.html", board_size=BOARD_SIZE, players=players, turn=current_turn, events=board_events)

@app.route("/roll")
def roll():
    global current_turn
    dice = roll_dice()
    players[current_turn]['position'] += dice

    # Check for landing on another player
    for other, data in players.items():
        if other != current_turn and data['position'] == players[current_turn]['position']:
            push_back_player(other)

    apply_event(current_turn, players[current_turn]['position'])

    # Check win condition
    if players[current_turn]['position'] > BOARD_SIZE:
        winner = current_turn
        save_game()
        return redirect(url_for('win', winner=winner))

    # Switch turn
    current_turn = 'Player 2' if current_turn == 'Player 1' else 'Player 1'
    save_game()
    return redirect(url_for('index'))

@app.route("/win/<winner>")
def win(winner):
    return f"<h1>{winner} wins!</h1><a href='/'>Restart</a>"

if __name__ == '__main__':
    load_game()
    app.run(debug=True)
