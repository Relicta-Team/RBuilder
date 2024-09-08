from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
import win32clipboard

SESSION_OBJ = None

# Create a custom key binding
bindings = KeyBindings()

@bindings.add(Keys.Tab)
def _(event):
	# Submit the prompt when Shift+Enter is pressed
	event.app.exit(result=event.app.current_buffer.text)

#copypaste event
@bindings.add('c-v')
def paste(event):
	win32clipboard.OpenClipboard()
	clipboard = win32clipboard.GetClipboardData()
	win32clipboard.CloseClipboard()
	event.app.current_buffer.insert_text(clipboard.replace('\t',' '*4))

def createSession():
	global SESSION_OBJ
	session = PromptSession('',completer=None,key_bindings=bindings)
	SESSION_OBJ = session
	return session

def _multiline_input(prompt):
	if not SESSION_OBJ:
		createSession()
	line = SESSION_OBJ.prompt(prompt, multiline=True)
	return line