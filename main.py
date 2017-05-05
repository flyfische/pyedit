import sys
import termios

orig_termios = termios.tcgetattr(sys.stdin.fileno())

def enable_raw_mode():
	print "enabling raw mode"
	#formatted like this: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
	new = termios.tcgetattr(sys.stdin)
	new[0] &= ~(termios.IXON | termios.ICRNL | termios.BRKINT | termios.ISTRIP | termios.INPCK)
	new[1] &= ~(termios.OPOST)
	new[2] |=  (termios.CS8)
	new[3] &= ~(termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN)
	new[6][termios.VMIN] = 0
	new[6][termios.VTIME] = 1;
	termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, new)

def restore_terminal():
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_termios)

if __name__ == "__main__":
	enable_raw_mode()
	while True:
		char = sys.stdin.read(1)
		print "got: {}\r".format(char)
		if char == 'q':
			break
	restore_terminal()

