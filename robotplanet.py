import random
import time
import sys

class Weapon:
    def __init__(self, name, damage, accuracy, description, special=None):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.description = description
        self.special = special

    def attack(self):
        if random.random() <= self.accuracy:
            return self.damage
        return 0

class Robot:
    def __init__(self, name, is_player=False):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.is_player = is_player
        self.stunned = False
        self.shield = 0

    def alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        if self.shield > 0:
            blocked = min(self.shield, damage)
            self.shield -= blocked
            damage -= blocked
            print(f"  Shield blocked {blocked} damage!")
        self.hp = max(0, self.hp - damage)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def reset_turn(self):
        self.shield = 0
        if self.stunned:
            self.stunned = False

weapons = [
    Weapon("Laser", 30, 0.80, "High damage, reliable accuracy"),
    Weapon("Rocket", 55, 0.45, "Devastating but often misses"),
    Weapon("Shield", 0, 1.0, "Blocks 35 damage & heals 10 HP", special="defend"),
    Weapon("EMP", 20, 0.70, "Medium damage + stuns enemy next turn", special="stun"),
    Weapon("Minigun", 10, 0.85, "Fires 4 shots per turn (10 dmg each)", special="multi"),
]

def print_header():
    print("=" * 60)
    print("        ROBOTPLANET - Battle Arena")
    print("=" * 60)

def print_weapons():
    print("\nWeapons:")
    print("-" * 40)
    for i, w in enumerate(weapons, 1):
        print(f"  {i}. {w.name:<10} | {w.description}")
    print("-" * 40)

def print_status(player, ai, round_num):
    print(f"\n{'─' * 40}")
    print(f"Round {round_num}")
    print(f"{'─' * 40}")
    p_hp_bar = "█" * (player.hp // 5) + "░" * ((player.max_hp - player.hp) // 5)
    a_hp_bar = "█" * (ai.hp // 5) + "░" * ((ai.max_hp - ai.hp) // 5)
    print(f"  {player.name}: HP [{p_hp_bar}] {player.hp}/{player.max_hp}")
    if player.shield > 0:
        print(f"    (Shield active: {player.shield})")
    print(f"  {ai.name}:    HP [{a_hp_bar}] {ai.hp}/{ai.max_hp}")
    if ai.shield > 0:
        print(f"    (Shield active: {ai.shield})")
    print(f"{'─' * 40}")

def ai_choose_weapon(ai_hp, player_hp):
    if ai_hp <= 25:
        return 2  # Shield - desperate defense
    if player_hp <= 20 and random.random() < 0.7:
        return 1  # Rocket - finish them
    if player_hp > 70:
        return 0  # Laser - consistent damage
    if random.random() < 0.3:
        return 3  # EMP - tactical stun
    return random.randint(0, 4)

def process_multi(player_hits, ai_hits, target, attacker_name):
    total = 0
    for i in range(4):
        hit = random.random() <= 0.85
        if hit:
            dmg = 10
            if target.shield > 0:
                blocked = min(target.shield, dmg)
                target.shield -= blocked
                dmg -= blocked
                if blocked > 0:
                    print(f"  Shot {i+1}: Shield blocked {blocked}!")
            target.hp = max(0, target.hp - dmg)
            total += dmg
            print(f"  Shot {i+1}: Hit for {dmg} damage!")
        else:
            print(f"  Shot {i+1}: Missed!")
        time.sleep(0.3)
        if target.hp <= 0:
            break
    return total

def play_round(player, ai, round_num):
    print_status(player, ai, round_num)

    if player.stunned:
        print(f"\n  {player.name} is STUNNED! Misses a turn!")
        player.stunned = False
        player_choice = None
    else:
        print_weapons()
        while True:
            try:
                choice = int(input("\nChoose your weapon (1-5): "))
                if 1 <= choice <= 5:
                    player_choice = choice - 1
                    break
                print("Invalid choice. Choose 1-5.")
            except ValueError:
                print("Enter a number 1-5.")

    ai_choice = ai_choose_weapon(ai.hp, player.hp)
    w_ai = weapons[ai_choice]
    print(f"\n{ai.name} chooses {w_ai.name}!")

    if player_choice is not None:
        w_player = weapons[player_choice]
        print(f"{player.name} uses {w_player.name}!")
        time.sleep(0.5)

        if w_player.special == "defend":
            player.shield = 35
            player.heal(10)
            print(f"  Shield raised! Blocking 35 damage. +10 HP healed.")
        elif w_player.special == "stun":
            dmg = w_player.attack()
            if dmg > 0:
                player.take_damage(0)
                ai.take_damage(dmg)
                print(f"  Hit for {dmg} damage!")
                ai.stunned = True
                print(f"  {ai.name} is now STUNNED!")
            else:
                print(f"  Missed!")
        elif w_player.special == "multi":
            process_multi(True, False, ai, player.name)

    time.sleep(0.5)

    if ai.alive() and not ai.stunned:
        print(f"\n{ai.name} attacks with {w_ai.name}!")
        time.sleep(0.5)

        if w_ai.special == "defend":
            ai.shield = 35
            ai.heal(10)
            print(f"  Shield raised! Blocking 35 damage. +10 HP healed.")
        elif w_ai.special == "stun":
            dmg = w_ai.attack()
            if dmg > 0:
                player.take_damage(dmg)
                print(f"  Hit for {dmg} damage!")
                player.stunned = True
                print(f"  {player.name} is now STUNNED!")
            else:
                print(f"  Missed!")
        elif w_ai.special == "multi":
            process_multi(False, True, player, ai.name)

    player.stunned = False

def main():
    print_header()
    player_name = input("\nEnter your robot name: ").strip() or "Player"
    ai_names = ["Terminator", "Titan", "Overlord", "Neuralis"]
    ai_name = random.choice(ai_names)

    print(f"\n{player_name} VS {ai_name}")
    print("=" * 60)
    input("Press Enter to start the battle!")

    player = Robot(player_name, is_player=True)
    ai = Robot(ai_name)

    round_num = 1
    while player.alive() and ai.alive():
        play_round(player, ai, round_num)
        round_num += 1
        if player.alive() and ai.alive():
            print("\n" + "=" * 60)
            input("Press Enter for next round...")
            print("\n" * 2)

    print("\n" + "=" * 60)
    print("                     GAME OVER")
    print("=" * 60)
    if player.alive():
        print(f"\n  {player.name} VICTORY!!")
    else:
        print(f"\n  {ai_name} wins...")
    print(f"\n  Battle lasted {round_num - 1} rounds")
    print("=" * 60)
    input("\nPress Enter to exit.")

if __name__ == "__main__":
    main()
