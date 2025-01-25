from collections import defaultdict
from itertools import permutations
import re
from pprint import pprint

STACK_END = ">"
INPUT_END = "<"


class TransitionFunctionValue:
    def __init__(self, next_state: str, symbol_to_push: list[str]):
        self.next_state = next_state
        self.symbols_to_push = symbol_to_push

    def __str__(self):
        return f"(next_state={self.next_state}, symbols_to_push={self.symbols_to_push})"

    def __repr__(self):
        return self.__str__()


class TransitionFunctionInput:
    def __init__(self, input_symbol: str, stack_top: str):
        self.input_symbol = input_symbol
        self.stack_top = stack_top

    def __hash__(self):
        return hash((self.input_symbol, self.stack_top))

    def __eq__(self, other):
        return (
            self.input_symbol == other.input_symbol
            and self.stack_top == other.stack_top
        )

    def __str__(self):
        return f"(input={self.input_symbol}, stack={self.stack_top})"

    def __repr__(self):
        return self.__str__()


class Automata:
    def __init__(
        self,
        states: list[str],
        alphabet: tuple[str],
        transitions: dict[TransitionFunctionInput, TransitionFunctionValue],
        initial_state: str,
        final_states: list[str],
        rejecting_states: list[str],
    ):
        """This class represents a deterministic pushdown automata.

        Args:
            states (list[str]): list of states
            alphabet (tuple[str]): input alphabet
            transitions (dict[TransitionFucntionInput, TransitionFunctionValue]): transition function defined as map where key is the current state and value is another map where key is the input symbol and value is another map where key is the top of the stack and value is the next state and the symbol to push to the stack
            initial_state (str | None, optional): Initial state of the automata
            final_states (list[TransitionFunctionInput] | None, optional): List of accepting state of the automata
            rejecting_states (list[TransitionFunctionInput] | None, optional): List of rejecting state of the automata
        """
        if initial_state is None:
            initial_state = states[0]
        if final_states is None:
            final_states = [states[-1]]

        self.__state = initial_state
        self.__stack = []
        self.__stack.append(STACK_END)
        self.__transitions = transitions
        self.__states = states
        self.__alphabet = alphabet
        self.__final_states = final_states
        self.__rejecting_states = rejecting_states
        self.initial_state = initial_state

    def simulate(self, input_string, debug: bool = False) -> bool:
        """Simulate the automata on the given input string.

        Args:
            input_string (str): input string

        Returns:
            bool: True if the input string is accepted by the automata, False otherwise
        """
        for symbol in input_string:
            if symbol not in self.__alphabet:
                if debug:
                    print(f"Symbol {symbol} not in alphabet")
                return False

            transition_input = TransitionFunctionInput(symbol, self.__stack.pop())
            if debug:
                print(transition_input)
            if transition_input in self.__transitions[self.__state]:
                transition_value = self.__transitions[self.__state][transition_input]
                self.__state = transition_value.next_state
                for symbol in transition_value.symbols_to_push:
                    self.__stack.append(symbol)
                if self.__state in self.__rejecting_states:
                    if debug:
                        print("Rejecting state")
                    return False
                elif self.__state in self.__final_states:
                    if debug:
                        print("Accepting state")
                    return True
            else:

                if debug:
                    print(
                        f"Transition {transition_input} not found in state {self.__state}"
                    )
                return False
        if self.__state in self.__final_states or self.__stack[-1] == STACK_END:
            return True
        return False

    def __transition_function_to_string(self, transition_function: dict) -> str:
        """
        Convert the transition function dictionary into a formatted string matching the input file format.
        """
        result = ["\n"]
        for state, transitions in transition_function.items():
            result.append(f"    {state}:")
            for transition_input, transition_value in transitions.items():
                input_symbol = transition_input.input_symbol
                stack_top = transition_input.stack_top
                next_state = transition_value.next_state
                stack_action = ", ".join(transition_value.symbols_to_push)
                result.append(
                    f"        ({input_symbol}, {stack_top}) -> {next_state} [{stack_action}]"
                )
        return "\n".join(result)

    def __str__(self):
        return f"State: {self.__state}, Stack: {self.__stack}. Transitions: {self.__transition_function_to_string(self.__transitions)}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def create_from_file(file: str):
        with open(file, "r") as file:
            lines = file.readlines()

        states = []
        alphabet = []
        initial_state = None
        final_states = []
        rejecting_states = []
        transition_function = defaultdict(dict)

        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            if line.startswith("states:"):
                states = line.split(":")[1].strip().split(", ")
            elif line.startswith("alphabet:"):
                alphabet = line.split(":")[1].strip().split(", ")
            elif line.startswith("initial_state:"):
                initial_state = line.split(":")[1].strip()
            elif line.startswith("final_states:"):
                final_states = line.split(":")[1].strip().split(", ")
            elif line.startswith("rejecting_states:"):
                rejecting_states = line.split(":")[1].strip().split(", ")
            elif line.startswith("transition_function:"):
                current_state = None
            elif re.match(r"^\w+:$", line):  # State header in transition function
                current_state = line[:-1]
                if current_state not in states:
                    raise ValueError(f"State {current_state} not in states {states}")
            elif current_state and "->" in line:
                match = re.match(r"\((.+), (.+)\) -> (\w+) \[(.*)\]", line)
                if match:
                    input_symbol, stack_top, next_state, stack_action = match.groups()
                    if stack_top == "STACK_END":
                        stack_top = STACK_END
                    elif stack_top == "INPUT_END":
                        stack_top = INPUT_END
                    stack_action = stack_action.split(", ") if stack_action else []
                    if stack_action:
                        stack_action = list(
                            map(
                                lambda x: (
                                    STACK_END
                                    if x.strip() == "STACK_END"
                                    else (
                                        INPUT_END
                                        if x.strip() == "INPUT_END"
                                        else x.strip()
                                    )
                                ),
                                stack_action,
                            )
                        )
                    transition_function[current_state][
                        TransitionFunctionInput(input_symbol, stack_top)
                    ] = TransitionFunctionValue(next_state, stack_action)

        return Automata(
            states,
            tuple(alphabet),
            dict(transition_function),
            initial_state,
            final_states,
            rejecting_states,
        )


if __name__ == "__main__":
    transition_function = {
        "q0": {
            TransitionFunctionInput("0", STACK_END): TransitionFunctionValue(
                "q1", [">", "0"]
            ),
            TransitionFunctionInput("0", "0"): TransitionFunctionValue(
                "q1", ["0", "0"]
            ),
            TransitionFunctionInput("0", "1"): TransitionFunctionValue("q1", []),
            TransitionFunctionInput("1", STACK_END): TransitionFunctionValue(
                "q0", [">", "1"]
            ),
            TransitionFunctionInput("1", "0"): TransitionFunctionValue("q0", []),
            TransitionFunctionInput("1", "1"): TransitionFunctionValue(
                "q0", ["1", "1"]
            ),
            TransitionFunctionInput(INPUT_END, STACK_END): TransitionFunctionValue(
                "qA", [">"]
            ),
            TransitionFunctionInput(INPUT_END, "0"): TransitionFunctionValue("qR", []),
            TransitionFunctionInput(INPUT_END, "1"): TransitionFunctionValue("qR", []),
        },
        "q1": {
            TransitionFunctionInput("0", STACK_END): TransitionFunctionValue(
                "q0", [">"]
            ),
            TransitionFunctionInput("0", "0"): TransitionFunctionValue("q0", ["0"]),
            TransitionFunctionInput("0", "1"): TransitionFunctionValue("q0", ["1"]),
            TransitionFunctionInput("1", STACK_END): TransitionFunctionValue(
                "q1", [STACK_END, "1"]
            ),
            TransitionFunctionInput("1", "0"): TransitionFunctionValue("q1", []),
            TransitionFunctionInput("1", "1"): TransitionFunctionValue(
                "q1", ["1", "1"]
            ),
            TransitionFunctionInput(INPUT_END, STACK_END): TransitionFunctionValue(
                "qR", [">"]
            ),
            TransitionFunctionInput(INPUT_END, "0"): TransitionFunctionValue(
                "qR", ["0"]
            ),
            TransitionFunctionInput(INPUT_END, "1"): TransitionFunctionValue(
                "qR", ["1"]
            ),
        },
    }
    states = ["q0", "q1", "qR", "qA"]
    alphabet = ("0", "1", "<")
    initial_state = "q0"
    final_states = ["qA"]
    rejecting_states = ["qR"]
    automata = Automata(
        states,
        alphabet,
        transition_function,
        initial_state,
        final_states,
        rejecting_states,
    )
    automata = Automata.create_from_file("automata.txt")
    print(automata)
    test_cases = list(permutations(["1", "1", "0", "0", "0", "0", "1", "0", "0"]))
    passed = True
    for test_case in test_cases:
        input_string = "".join(test_case)
        answer = input_string.count("1") * 2 == input_string.count("0")
        result = automata.simulate(input_string)
        if result != answer:
            print(f"Test case {input_string} failed")
            print(f"Expected: {answer}, Got: {result}")
            passed = False
    if passed:
        print("All test cases passed")
