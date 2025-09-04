#!/usr/bin/env python3
import random
import json
import os
import sys  

movies = {
    "The Lion King": {"emoji": "👑🦁🐾", "hint": "A young lion becomes king in the African savanna."},
    "Titanic": {"emoji": "🚢💔❤️", "hint": "A tragic love story aboard a doomed ship."},
    "Jurassic Park": {"emoji": "🦖🌴🧑‍🔬", "hint": "Dinosaurs escape on an island theme park."},
    "Frozen": {"emoji": "❄️👭⛄", "hint": "Two sisters save their kingdom with ice magic."},
    "Spider-Man": {"emoji": "🕷️🧑‍🦱🏙️", "hint": "A teen gains web-slinging powers in New York."},
    "The Matrix": {"emoji": "🕶️💊🖥️", "hint": "A hacker discovers a simulated reality."},
    "Star Wars": {"emoji": "⚔️🚀🌌", "hint": "Epic space saga with lightsabers and the Force."},
    "Harry Potter": {"emoji": "🧙‍♂️⚡️🪄", "hint": "A young wizard attends a magical school."},
    "The Avengers": {"emoji": "🦸‍♂️🛡️⚡", "hint": "Superheroes team up to save Earth."},
    "Pirates of the Caribbean": {"emoji": "🏴‍☠️⚓🗺️", "hint": "A pirate seeks cursed treasure."},
    "The Dark Knight": {"emoji": "🦇🃏🌃", "hint": "A vigilante faces a chaotic villain in Gotham."},
    "Finding Nemo": {"emoji": "🐠🌊🐟", "hint": "A clownfish searches for his lost son."},
    "The Incredibles": {"emoji": "🦸‍♀️🦸‍♂️👨‍👩‍👧‍👦", "hint": "A superhero family saves the world."},
    "Toy Story": {"emoji": "🤠🚀🧸", "hint": "Toys come to life and go on adventures."},
    "The Wizard of Oz": {"emoji": "🧙‍♀️🌪️👠", "hint": "A girl travels a magical road in ruby slippers."},
    "Jaws": {"emoji": "🦈🌊🚤", "hint": "A giant shark terrorizes a beach town."},
    "The Godfather": {"emoji": "🍝🔫🎩", "hint": "A mafia family navigates power and betrayal."},
    "Back to the Future": {"emoji": "🚗⏰⚡️", "hint": "A teen time-travels in a DeLorean."},
    "Indiana Jones": {"emoji": "🪓🗿🤠", "hint": "An archaeologist hunts ancient relics."},
    "E.T.": {"emoji": "👽🚲🌙", "hint": "A boy befriends an alien stranded on Earth."},
    "The Shawshank Redemption": {"emoji": "🔒🏃‍♂️🪓", "hint": "A prisoner plans a daring escape."},
    "Forrest Gump": {"emoji": "🏃‍♂️🍫🪶", "hint": "A man runs through life’s unexpected events."},
    "The Lord of the Rings": {"emoji": "💍🧙‍♂️🗡️", "hint": "A quest to destroy a powerful ring."},
    "Avatar": {"emoji": "🦋🌍👽", "hint": "A human connects with an alien world."},
    "Gladiator": {"emoji": "🗡️🛡️🏟️", "hint": "A Roman general seeks revenge in the arena."},
    "The Silence of the Lambs": {"emoji": "🦋🔪🧠", "hint": "An FBI agent consults a cannibalistic killer."},
    "Coco": {"emoji": "🎸💀🌸", "hint": "A boy explores the Land of the Dead."},
    "Up": {"emoji": "🎈🏠👴", "hint": "An old man flies his house with balloons."},
    "Moana": {"emoji": "🌊⛵🐔", "hint": "A Polynesian girl sails to save her island."},
    "Zootopia": {"emoji": "🐰🦊🚔", "hint": "A rabbit cop solves a mystery in a city of animals."},
    "Inside Out": {"emoji": "😊😢😣", "hint": "Emotions guide a girl’s mind."},
    "La La Land": {"emoji": "🎹💃🌟", "hint": "A musician and actress chase dreams in L.A."},
    "Mad Max": {"emoji": "🚗🔥🏜️", "hint": "A warrior races through a post-apocalyptic desert."},
    "The Breakfast Club": {"emoji": "👨‍🎓👩‍🎤📚", "hint": "Teens bond during detention."},
    "Grease": {"emoji": "💃🕺🚗", "hint": "A 1950s romance with greasers and dancers."},
    "Shrek": {"emoji": "🧌👸🐴", "hint": "An ogre rescues a princess with a twist."},
    "Kung Fu Panda": {"emoji": "🐼🥋🍜", "hint": "A panda learns martial arts."},
    "Aladdin": {"emoji": "🧞‍♂️🪔👸", "hint": "A street rat finds a magic lamp."},
    "Beauty and the Beast": {"emoji": "🌹👸🐗", "hint": "A girl falls for a cursed prince."},
    "The Little Mermaid": {"emoji": "🧜‍♀️🌊👑", "hint": "A mermaid dreams of life on land."},
    "Mulan": {"emoji": "🗡️👩‍🎤🐉", "hint": "A woman disguises as a man to fight."},
    "Brave": {"emoji": "🏹👩‍🦰🐻", "hint": "A Scottish princess defies tradition."},
    "The Jungle Book": {"emoji": "🐻🐒🌴", "hint": "A boy is raised by jungle animals."},
    "Cinderella": {"emoji": "👠🎃👸", "hint": "A girl attends a ball with a glass slipper."},
    "Snow White": {"emoji": "🍎👸🪞", "hint": "A princess is poisoned by an apple."},
    "Sleeping Beauty": {"emoji": "💤👸🪡", "hint": "A princess falls into a cursed sleep."},
    "Pocahontas": {"emoji": "🌳👩‍🦰🦝", "hint": "A Native American woman connects with nature."},
    "Ratatouille": {"emoji": "🐀🍽️👨‍🍳", "hint": "A rat becomes a chef in Paris."},
    "Monsters Inc": {"emoji": "👁️‍🗨️😱👧", "hint": "Monsters scare kids for energy."},
    "Wall-E": {"emoji": "🤖🗑️🌱", "hint": "A robot cleans a deserted Earth."},
    "Despicable Me": {"emoji": "👨‍🔬💛👧", "hint": "A villain adopts three girls."},
    "Minions": {"emoji": "💛👓🍌", "hint": "Yellow creatures cause chaos."},
    "The Karate Kid": {"emoji": "🥋👦🧑‍🏫", "hint": "A boy learns karate to face bullies."},
    "Ghostbusters": {"emoji": "👻🚫🚗", "hint": "A team hunts ghosts in New York."},
    "Die Hard": {"emoji": "🔫🏢🎄", "hint": "A cop fights terrorists on Christmas."},
    "The Terminator": {"emoji": "🤖🔫🕶️", "hint": "A cyborg hunts a future leader."},
    "Home Alone": {"emoji": "🏠👦🦁", "hint": "A boy defends his house from burglars."},
    "The Princess Bride": {"emoji": "🤺❤️👸", "hint": "A swashbuckling tale of true love."},
    "Men in Black": {"emoji": "👽🕶️🚀", "hint": "Agents monitor aliens on Earth."},
    "The Hunger Games": {"emoji": "🏹🔥👧", "hint": "A girl fights in a dystopian contest."},
    "Twilight": {"emoji": "🧛‍♂️💔🌲", "hint": "A teen loves a vampire."},
    "Inception": {"emoji": "🌀💤🧠", "hint": "Thieves infiltrate dreams."},
    "Fight Club": {"emoji": "👊🧼💥", "hint": "A man starts an underground fight club."},
    "Pulp Fiction": {"emoji": "🔫🍔💼", "hint": "Crime stories intertwine in L.A."},
    "The Grand Budapest Hotel": {"emoji": "🏨🧳🎨", "hint": "A concierge navigates a quirky hotel."},
    "Moonlight": {"emoji": "🌙👦❤️", "hint": "A young man grows up in Miami."},
    "Parasite": {"emoji": "🏠🪨🍽️", "hint": "A poor family infiltrates a rich household."},
    "Get Out": {"emoji": "🧠🔑😱", "hint": "A man uncovers a sinister plot."},
    "Black Panther": {"emoji": "🐆👑🛡️", "hint": "A king protects his advanced nation."},
    "Wonder Woman": {"emoji": "🗡️🛡️👸", "hint": "An Amazon warrior fights in war."},
    "Captain Marvel": {"emoji": "✈️🌟👩", "hint": "A pilot gains cosmic powers."},
    "Deadpool": {"emoji": "🗡️😂🔫", "hint": "A wisecracking mercenary seeks revenge."},
    "Guardians of the Galaxy": {"emoji": "🚀🎶🌌", "hint": "Misfits save the universe with music."},
    "Jumanji": {"emoji": "🎲🌴🦒", "hint": "A board game traps players in a jungle."},
    "The Goonies": {"emoji": "💰🗺️🏴‍☠️", "hint": "Kids hunt for pirate treasure."},
    "The Sandlot": {"emoji": "⚾🐶🏞️", "hint": "Kids play baseball and face a beast."},
    "Clueless": {"emoji": "👗📱👧", "hint": "A rich teen navigates high school."},
    "Mean Girls": {"emoji": "👩‍🎤📓💖", "hint": "A teen faces high school cliques."},
    "Legally Blonde": {"emoji": "👩‍⚖️💼🐶", "hint": "A blonde excels at law school."},
    "Pitch Perfect": {"emoji": "🎤👩‍🎓🎶", "hint": "College singers compete in a cappella."},
    "The Fault in Our Stars": {"emoji": "🌟💔📖", "hint": "Teens with cancer fall in love."},
    "Dune": {"emoji": "🏜️🪐⚔️", "hint": "A young hero rises on a desert planet."},
    "Blade Runner": {"emoji": "🤖🌃🔫", "hint": "A detective hunts rogue androids."},
    "Interstellar": {"emoji": "🚀🌌⏰", "hint": "Astronauts seek a new home for humanity."},
    "Gravity": {"emoji": "🚀🌍😱", "hint": "An astronaut fights to survive in space."},
    "The Martian": {"emoji": "🚀🪐🥔", "hint": "A stranded astronaut grows potatoes."},
    "Star Trek": {"emoji": "🚀🖖🌌", "hint": "A crew explores space with logic."},
    "The Empire Strikes Back": {"emoji": "⚔️❄️🚀", "hint": "Rebels battle on an icy planet."},
    "Return of the Jedi": {"emoji": "⚔️🌳🚀", "hint": "A final stand against an empire."},
    "Rogue One": {"emoji": "🌌🛡️💥", "hint": "Rebels steal plans for a superweapon."},
    "Skyfall": {"emoji": "🔫🕶️🏙️", "hint": "A spy defends his agency."},
    "Casino Royale": {"emoji": "🃏🔫🍸", "hint": "A spy plays high-stakes poker."},
    "The Bourne Identity": {"emoji": "🔫🕵️‍♂️🗺️", "hint": "An amnesiac spy uncovers his past."},
    "Mission Impossible": {"emoji": "🕵️‍♂️💣✈️", "hint": "A spy tackles impossible missions."},
    "John Wick": {"emoji": "🔫🐶🎩", "hint": "A hitman seeks revenge for his dog."},
    "The Fast and the Furious": {"emoji": "🚗💨🏁", "hint": "Street racers pull off heists."},
    "Transformers": {"emoji": "🤖🚗💥", "hint": "Robots disguise as vehicles."},
    "Pacific Rim": {"emoji": "🤖🦖🌊", "hint": "Giant robots fight sea monsters."}
}

correct_responses = ["✅ Correct!", "🎉 You got it!", "🔥 Nice!", "👏 Well done!"]
wrong_responses = ["❌ Nope!", "😢 Wrong!", "🙃 Not quite!", "💔 Incorrect!"]

save_file = os.path.expanduser("~/.emoji_movie_quiz_score")


def load_high_score():
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            return json.load(f).get("high_score", 0)
    return 0


def save_high_score(score):
    with open(save_file, "w") as f:
        json.dump({"high_score": score}, f)


def main():
    score = 0
    lives = 3
    high_score = load_high_score()

    print("🎬 Welcome to Emoji Movie Quiz! Type 'quit' to exit.")
    print(f"🏆 Current High Score: {high_score}\n")

    while lives > 0:
        movie, data = random.choice(list(movies.items()))
        emoji_hint = data["emoji"]
        hint = data["hint"]

        print(f"\nGuess the movie: {emoji_hint} (Lives: {lives}, Score: {score})")

        for attempt in range(2):
            guess = input("Your guess: ").strip()
            if guess.lower() == "quit":
                lives = 0
                break
            elif guess.lower() == movie.lower():
                print(random.choice(correct_responses), "+1 point")
                score += 1
                break
            else:
                if attempt == 0:
                    print(f"{random.choice(wrong_responses)} Hint: {hint}")
                else:
                    print(f"{random.choice(wrong_responses)} The answer was: {movie}")
                    lives -= 1

    if score > high_score:
        save_high_score(score)
        print(f"\n🏆 New High Score! You scored {score}")
    else:
        print(f"\nGame Over! Final Score: {score}. High Score: {high_score}")


if __name__ == "__main__":
    main()