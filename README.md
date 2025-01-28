# Push Down Automata

This project implements a deterministic pushdown automata (PDA) in Python. The automata can be used to simulate the behavior of a PDA on a given input string.

## Project Structure

- `automata.txt`: Contains the definition of the automata including states, alphabet, initial state, final states, rejecting states, and transition functions.
- `automata.py`: Python script that implements the PDA and its simulation.

## Automata Definition

The automata is defined in the `automata.txt` file with the following sections:

- **States**: List of states in the automata.
- **Alphabet**: Input symbols the automata can process.
- **Initial State**: The starting state of the automata.
- **Final States**: States where the automata accepts the input.
- **Rejecting States**: States where the automata rejects the input.
- **Transition Function**: Defines the transitions between states based on input symbols and stack operations.

## Usage

To use the automata, you can run the `automata.py` script. The script reads the automata definition from `automata.txt` and simulates the automata on various input strings.

### Example

```bash
python automata.py
```

The script will print the automata's transitions and the results of the simulation on test cases.

## License

This project is licensed under the MIT License.
