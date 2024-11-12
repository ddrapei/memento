#!/usr/bin/env python3

import json
import time
import os
import random
import sys
import csv
from datetime import datetime
import shutil
import signal


RESIZE_HAPPENED = False
CURRENT_DISPLAY = "main"


def handle_resize(signum, frame):
    """Signal handler for terminal resize"""
    global RESIZE_HAPPENED
    RESIZE_HAPPENED = True


# Set up signal handler
signal.signal(signal.SIGWINCH, handle_resize)


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def get_terminal_size():
    """Get current terminal size"""
    return shutil.get_terminal_size()


def redraw_screen(words, current_state=None):
    """Redraw the entire screen based on current state"""
    clear_screen()
    terminal_width = get_terminal_size().columns
    type_out_text(ascii_art, delay=0)  # No delay for redraw
    print_menu_header("MEMENTO")

    options = [
        "Add Word",
        "View Words",
        "Quiz Yourself",
        "Delete Word",
        "Export Word List to CSV",
        "Import Word List from CSV",
        "View Statistics",
        "Exit"
    ]

    for i, option in enumerate(options, 1):
        print(Colors.colorize(f"    {i}. {option}", Colors.CYAN))

def display_main_menu():
    """Display the main menu options"""
    options = [
        "Add Word",
        "View Words",
        "Quiz Yourself",
        "Delete Word",
        "Export Word List to CSV",
        "Import Word List from CSV",
        "View Statistics",
        "Exit"
    ]

# Color constants
class Colors:
    # Basic colors
    GREEN = "\033[32m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    CYAN = "\x1b[38;5;163m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    # Style modifiers
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def colorize(text, color, bold=False, underline=False):
        """Utility method to apply color and style to text"""
        style = ""
        if bold:
            style += Colors.BOLD
        if underline:
            style += Colors.UNDERLINE
        return f"{style}{color}{text}{Colors.RESET}"


# The ASCII art to display
ascii_art = [
    "      _---~~(~~-_.        ",
    "    _{        )   )       ",
    "  ,   ) -~~- ( ,-' )_     ",
    " (  `-,_..`., )-- '_,)    ",
    "( ` _)  (  -~( -_ `,  }   ",
    " (_-  _  ~_-~~~~`,  ,' )  ",
    "  `~ -^(    __;-,((()))   ",
    "        ~~~~ {_ -_(())    ",
    "               `\\  }     ",
    "                 { }      "
]

def get_terminal_width():
    try:
        # Get the terminal size
        terminal_width, _ = shutil.get_terminal_size()
        return terminal_width
    except:
        return 50


def type_out_text(text_lines, delay=0.005):
    """Display ASCII art with optional animation delay"""
    terminal_width = get_terminal_size().columns

    # Calculate the maximum line width in the ASCII art
    max_line_width = max(len(line) for line in text_lines)

    # Calculate left padding to center the art
    left_padding = (terminal_width - max_line_width) // 2
    left_padding = max(0, left_padding)  # Ensure padding is not negative

    sys.stdout.write(Colors.CYAN)
    for line in text_lines:
        # Print padding first
        sys.stdout.write(" " * left_padding)
        # Then print each character in the line
        if delay > 0:
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            sys.stdout.write("\n")
        else:
            # If delay is 0, print the whole line at once
            sys.stdout.write(line + "\n")
    sys.stdout.write(Colors.RESET)
    sys.stdout.flush()

def load_words():
    try:
        with open("data/words.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_stats():
    try:
        with open("data/stats.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "total_quizzes": 0,
            "words_learned": 0,
            "quiz_results": [],
            "last_quiz_date": None
        }


def save_words(words):
    os.makedirs("data", exist_ok=True)
    with open("data/words.json", "w") as f:
        json.dump(words, f)


def save_stats(stats):
    os.makedirs("data", exist_ok=True)
    with open("data/stats.json", "w") as f:
        json.dump(stats, f)


def print_menu_header(text):
    """Print a stylized header for menus and sections"""
    try:
        terminal_width, _ = get_terminal_size()
        separator = "═" * (terminal_width - 4)

        print(f"\n{Colors.colorize(separator.center(terminal_width), Colors.BLUE)}")
        print(Colors.colorize(text.center(terminal_width), Colors.YELLOW, bold=True))
        print(Colors.colorize(separator.center(terminal_width), Colors.BLUE))
    except:
        # Fallback: simple header if centering fails
        print(f"\n{Colors.BLUE}{'═' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}{text}{Colors.RESET}")
        print(f"{Colors.BLUE}{'═' * 50}{Colors.RESET}")

def center_text(text, width=None):
    """Center align any text based on terminal width"""
    if width is None:
        width = shutil.get_terminal_size().columns
    return text.center(width)

def update_stats(correct_count, total_words, words_attempted):
    stats = load_stats()
    stats["total_quizzes"] += 1
    stats["words_learned"] = max(stats["words_learned"], correct_count)

    quiz_result = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": correct_count,
        "total": total_words,
        "percentage": (correct_count / total_words) * 100 if total_words > 0 else 0,
        "words_attempted": words_attempted
    }
    stats["quiz_results"].append(quiz_result)
    stats["last_quiz_date"] = quiz_result["date"]

    save_stats(stats)


def view_stats():
    stats = load_stats()

    if stats["total_quizzes"] == 0:
        print(Colors.colorize("\nNo quiz statistics available yet. Take a quiz first!", Colors.YELLOW))
        return

    print_menu_header("Quiz Statistics")

    print(Colors.colorize(f"Total quizzes taken: {stats['total_quizzes']}", Colors.CYAN))
    print(Colors.colorize(f"Words learned: {stats['words_learned']}", Colors.CYAN))

    if stats["quiz_results"]:
        total_percentage = sum(result["percentage"] for result in stats["quiz_results"])
        avg_percentage = total_percentage / len(stats["quiz_results"])
        print(Colors.colorize(f"Average score: {avg_percentage:.1f}%", Colors.MAGENTA))

    if stats["last_quiz_date"]:
        print(Colors.colorize(f"Last quiz taken: {stats['last_quiz_date']}", Colors.BLUE))

    if len(stats["quiz_results"]) >= 2:
        first_quiz = stats["quiz_results"][0]["percentage"]
        last_quiz = stats["quiz_results"][-1]["percentage"]
        improvement = last_quiz - first_quiz
        color = Colors.GREEN if improvement >= 0 else Colors.RED
        print(Colors.colorize(f"Improvement since first quiz: {improvement:+.1f}%", color))

    print(Colors.colorize("\nRecent quiz results:", Colors.YELLOW, bold=True))
    for result in stats["quiz_results"][-5:]:
        percentage = result['percentage']
        if percentage >= 80:
            color = Colors.GREEN
        elif percentage >= 60:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        print(Colors.colorize(
            f"{result['date']}: {result['score']}/{result['total']} ({percentage:.1f}%)",
            color
        ))


def add_word(words):
    print_menu_header("Add New Words")
    while True:
        word = input(Colors.colorize("Enter the word (or type 'main' to return to the main menu): ", Colors.CYAN))
        if word.lower() == 'main':
            break
        definition = input(Colors.colorize(f"Enter the definition for '{word}': ", Colors.CYAN))
        words[word] = definition
        print(Colors.colorize(f"'{word}' added successfully!", Colors.GREEN))
        continue_adding = input(Colors.colorize(
            "Do you want to add another word? (yes to continue, 'main' to return to the menu): ",
            Colors.YELLOW
        ))
        if continue_adding.lower() == 'main':
            break
    save_words(words)


def view_words(words):
    print_menu_header("Word List")
    if not words:
        print(center_text(Colors.colorize("No words available.", Colors.YELLOW)))
        return

    terminal_width = shutil.get_terminal_size().columns
    for i, (word, definition) in enumerate(words.items(), 1):
        color = Colors.CYAN if i % 2 == 0 else Colors.WHITE
        entry = f"{i}. {word}: {definition}"
        print(center_text(Colors.colorize(entry, color, bold=True), terminal_width))


def delete_word(words):
    print_menu_header("Delete Word")
    if not words:
        print(Colors.colorize("No words available to delete.", Colors.YELLOW))
        return

    word_to_delete = input(Colors.colorize("Enter the word you want to delete: ", Colors.CYAN))
    if word_to_delete in words:
        del words[word_to_delete]
        print(Colors.colorize(f"'{word_to_delete}' has been deleted.", Colors.GREEN))
        save_words(words)
    else:
        print(Colors.colorize(f"'{word_to_delete}' not found in the list.", Colors.RED))


def print_progress(current, total):
    progress = (current / total) * 100
    bar_length = 50
    filled_length = int(progress // 2)

    # Create a multicolored progress bar
    bar = ""
    for i in range(bar_length):
        if i < filled_length:
            if i < bar_length * 0.33:  # First third is red
                bar += Colors.RED + "█"
            elif i < bar_length * 0.66:  # Middle third is yellow
                bar += Colors.YELLOW + "█"
            else:  # Last third is green
                bar += Colors.GREEN + "█"
        else:
            bar += Colors.WHITE + "─"

    words_done = current
    words_left = total - current
    print(f"\n[{bar}{Colors.RESET}] {Colors.CYAN}{progress:.1f}%{Colors.RESET}")
    print(Colors.colorize(f"Progress: {words_done}/{total} words done, {words_left} left", Colors.BLUE))
    sys.stdout.flush()


def highlight_mistakes(user_answer, correct_word):
    result = ""
    for i, char in enumerate(user_answer):
        if i < len(correct_word):
            # Convert both to lowercase for comparison
            if char.lower() == correct_word[i].lower():
                # If it matches, keep the original case
                result += Colors.colorize(char, Colors.GREEN)
            else:
                # If it doesn't match, make it uppercase
                result += Colors.colorize(char.upper(), Colors.RED, bold=True)
        else:
            # If the user's answer is longer than the correct word,
            # make the extra characters uppercase
            result += Colors.colorize(char.upper(), Colors.RED, bold=True)

    return result


def quiz(words):
    if not words:
        print(Colors.colorize("No words available to quiz. Add some words first.", Colors.YELLOW))
        return

    print_menu_header("Vocabulary Quiz")

    # Get the number of words the user wants to include in the quiz
    while True:
        try:
            user_input = input(
                Colors.colorize("Enter the number of words to include in the quiz (default is 15): ", Colors.CYAN))
            # If user just pressed Enter, use default value
            if user_input.strip() == "":
                quiz_size = 15
                break

            quiz_size = int(user_input)
            if quiz_size <= 0:
                print(Colors.colorize("Please enter a positive number.", Colors.RED))
                continue
            break
        except ValueError:
            print(Colors.colorize("Invalid input. Please enter a number.", Colors.RED))

    word_definitions = list(words.items())
    # Make sure quiz_size doesn't exceed the number of available words
    quiz_size = min(quiz_size, len(word_definitions))
    random.shuffle(word_definitions)
    incorrect_words = []
    total_words = quiz_size
    correct_count = 0
    words_attempted = set()

    for index, (word, definition) in enumerate(word_definitions[:quiz_size], 1):
        print_progress(index - 1, total_words)
        print(Colors.colorize(f"\nDefinition: '{definition}'", Colors.CYAN))
        answer = input(Colors.colorize("Your answer: ", Colors.YELLOW))

        # Allow the user to cancel the quiz and return to the main menu
        if answer.strip().lower() == 'cancel':
            print(Colors.colorize("\nQuiz canceled. Returning to the main menu.", Colors.YELLOW))
            return

        words_attempted.add(word)

        if answer.strip().lower() == word.lower():
            print(Colors.colorize("✓ Correct!", Colors.GREEN, bold=True))
            correct_count += 1
        else:
            print(Colors.colorize("✗ Incorrect.", Colors.RED, bold=True))
            print(f"Your answer: {highlight_mistakes(answer, word)}")
            print(Colors.colorize(f"Correct word: '{word}'", Colors.GREEN))
            incorrect_words.append((word, definition))

    print_progress(total_words, total_words)
    score_percentage = (correct_count / total_words) * 100

    print("\n" + Colors.colorize("═" * 50, Colors.BLUE))
    print(Colors.colorize("Quiz Complete!", Colors.YELLOW, bold=True))
    print(Colors.colorize(
        f"Score: {correct_count}/{total_words} ({score_percentage:.1f}%)",
        Colors.GREEN if score_percentage >= 70 else Colors.RED,
        bold=True
    ))
    print(Colors.colorize("═" * 50, Colors.BLUE))

    update_stats(correct_count, total_words, list(words_attempted))

    if incorrect_words:
        retry = input(Colors.colorize("\nWould you like to retry the words you got wrong? (yes/no): ", Colors.YELLOW))
        if retry.lower() == 'yes':
            print(Colors.colorize("\nRetrying incorrect words...", Colors.CYAN))
            random.shuffle(incorrect_words)
            quiz(dict(incorrect_words))


def export_words_to_csv(words):
    """Export the current word list to a CSV file."""
    print_menu_header("Export Word List to CSV")

    if not words:
        print(Colors.colorize("No words available to export.", Colors.YELLOW))
        return

    filename = input(Colors.colorize("Enter a filename (without .csv extension): ", Colors.CYAN)) + ".csv"
    file_path = os.path.join("data", filename)

    try:
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Word", "Definition"])
            for word, definition in words.items():
                writer.writerow([word, definition])

        print(Colors.colorize(f"Word list exported to {file_path}", Colors.GREEN))
    except IOError:
        print(Colors.colorize(f"Error writing to {file_path}", Colors.RED))


def import_words_from_csv():
    """Import a word list from a CSV file."""
    print_menu_header("Import Word List from CSV")

    filename = input(Colors.colorize("Enter the filename (including .csv extension): ", Colors.CYAN))
    file_path = os.path.join("data", filename)

    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            imported_words = {row[0]: row[1] for row in reader}

        # Load the existing words, then update with the imported words
        words = load_words()
        words.update(imported_words)
        save_words(words)

        print(Colors.colorize(f"{len(imported_words)} words imported from {file_path}", Colors.GREEN))
    except FileNotFoundError:
        print(Colors.colorize(f"File '{file_path}' not found.", Colors.RED))
    except (IOError, IndexError):
        print(Colors.colorize("Error reading the CSV file. Make sure the format is correct.", Colors.RED))


def main():
    global RESIZE_HAPPENED
    env = os.environ.copy()
    env['TERM'] = 'xterm'

    clear_screen()
    type_out_text(ascii_art)
    words = load_words()
    last_terminal_size = get_terminal_size()

    while True:
        try:
            current_size = get_terminal_size()

            # Check if terminal size has changed
            if RESIZE_HAPPENED or current_size != last_terminal_size:
                redraw_screen(words)
                RESIZE_HAPPENED = False
                last_terminal_size = current_size

            print_menu_header("MEMENTO")
            options = [
                "Add Word",
                "View Words",
                "Quiz Yourself",
                "Delete Word",
                "Export Word List to CSV",
                "Import Word List from CSV",
                "View Statistics",
                "Exit"
            ]

            for i, option in enumerate(options, 1):
                print(Colors.colorize(f"    {i}. {option}", Colors.CYAN))

            choice = input(Colors.colorize("\n    Choose an option: ", Colors.YELLOW))

            clear_screen()

            if choice == "1":
                add_word(words)
                clear_screen()
            elif choice == "2":
                view_words(words)
                input(Colors.colorize("\n    Press Enter to continue...", Colors.YELLOW))
                clear_screen()
            elif choice == "3":
                quiz(words)
                clear_screen()
            elif choice == "4":
                delete_word(words)
                clear_screen()
            elif choice == "5":
                export_words_to_csv(words)
                input(Colors.colorize("\n    Press Enter to continue...", Colors.YELLOW))
                clear_screen()
            elif choice == "6":
                import_words_from_csv()
                input(Colors.colorize("\n    Press Enter to continue...", Colors.YELLOW))
                clear_screen()
            elif choice == "7":
                view_stats()
                input(Colors.colorize("\n    Press Enter to continue...", Colors.YELLOW))
                clear_screen()
            elif choice == "8":
                print(Colors.colorize("\n    Thank you for using the Vocabulary Trainer! Goodbye!", Colors.GREEN))
                break
            else:
                print(Colors.colorize("\n    Invalid choice. Please try again.", Colors.RED))
                time.sleep(1.5)
                clear_screen()

        except KeyboardInterrupt:
            print(Colors.colorize("\n\n    Program terminated by user. Goodbye!", Colors.YELLOW))
            sys.exit(0)
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            input("Press Enter to continue...")
            clear_screen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Colors.colorize("\n\n    Program terminated by user. Goodbye!", Colors.YELLOW))
        sys.exit(0)