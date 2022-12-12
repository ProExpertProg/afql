import re
import sys

from afqlite.afqlite import AFQLite
from prompt_toolkit import PromptSession

from cli.commands import COMMAND_PREFIX, commands

if __name__ == '__main__':
    print("AFQLite CLI Version 0.0.1")

    # Uncomment for multiline
    # print("Press [Meta+Enter] or [Esc] followed by [Enter] to accept input.")
    afql = AFQLite(None)
    session = PromptSession() #(multiline=True, prompt_continuation="   ... > ")
    while True:
        try:
            line = session.prompt('afqlite> ').strip().replace('\n', ' ')
            line = re.sub(' +', ' ', line)
            if line.startswith(COMMAND_PREFIX):
                argv = line[len(COMMAND_PREFIX):].split(' ')

                # find the command
                found = False
                for name in commands:
                    if argv[0] == name:
                        commands[name].run(afql, argv[1:])
                        found = True
                        break

                if not found:
                    print("Unknown command \"%s\". Available commands:" % (argv[0]))
                    commands['help'].run(afql)
                continue

            # handle query
            # TODO

        except KeyboardInterrupt:
            print("Ope! try again")
        except EOFError:
            print("Good day")
            break
