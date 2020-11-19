# Host-side config (Linux host receiving commands)
HOST = "10.0.0.10"
PORT = 8240

PLUGIN_PATH = ["plugins"]

# When using the Text action, grammars may request (the default is not to) to
# input the text using the clipboard rather than emulating keypresses. This has
# the advantage of allowing far more rapid entry of a large chunk of text, but
# may cause strange behavior with programs that don't understand middle click
# paste. This is implemented using xsel, meaning that after text entry xsel may
# remain running until the clipboard is cleared (this is necessary because X11
# clipboards are not buffers, they are communication protocols.). I have verified
# that there should only be at most three xsel processes running at a time,
# though they may be quite long-lived, they do not consume substantial resources.
#
# Few programs use the SECONDARY buffer, which is where we back up the PRIMARY
# buffer (middle click paste) during the operation. This buffer is clobbered.
#
# The server should clear the text it entered from the system clipboard after
# entering it, so you do not need to worry about accidentally pasting it
# somewhere else later.

# Currently this is implemented by sending a middle click. unfortunately, not
# many programs will work with this if the mouse is not precisely where you want
# to click. There is no cross when doing environment way of pasting, which means
# this approach would require a great deal of per environment coding to be
# functional. When and if GTK ever fixes its  broken shift+insert behavior, or at
# least enables users to configure it to work properly, this will become
# workable.
ENABLE_XSEL = False

# xdotool delay.  Setting this value greater than zero may help solve some text
# input issues.  Obviously this setting does not apply when ENABLE_XSEL = True.
XDOTOOL_DELAY = 0

# Server log file path
#LOG_FILE = '/path/to/server.log'

# Logger verbosity settings.  See the following for a list of levels:
# https://docs.python.org/2/library/logging.html#levels
#CONSOLE_LOG_LEVEL = 'WARNING'
#FILE_LOG_LEVEL = 'INFO'
SECURITY_TOKEN = 'LQMkD2K6zZVrZUoKckS53kpsVjKUWBna1WPM4d4P1I4='
