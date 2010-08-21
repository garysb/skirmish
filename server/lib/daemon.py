# Convert the main thread into a daemon
# vim: set ts=8 sw=8 sts=8 list nu:
import os

class Daemon
	# Default daemon parameters.
	umask					= 0
	workdir					= "/"
	maxfd					= 1024
	redir					= '/dev/null'

	def __init__(self):
		"""Detach a process from the controlling terminal and run it in the
		background as a daemon.
		"""

		# The standard I/O file descriptors are redirected to /dev/null by default.
		if (hasattr(os, "devnull")):
			self.redir			= os.devnull
		else:
			self.redir			= "/dev/null"

		try:
			# Fork a child process so the parent can exit.  This returns control to
			# the command-line or shell.  It also guarantees that the child will not
			# be a process group leader, since the child receives a new process ID
			# and inherits the parent's process group ID.  This step is required
			# to insure that the next call to os.setsid is successful.
			pid			= os.fork()
		except OSError as e:
			raise Exception("{0} [{1}]".format(e.strerror, e.errno))

		if (pid == 0):
			# To become the session leader of this new session and the process group
			# leader of the new process group, we call os.setsid().  The process is
			# also guaranteed not to have a controlling terminal.
			os.setsid()

			# Is ignoring SIGHUP necessary?
			#
			# It's often suggested that the SIGHUP signal should be ignored before
			# the second fork to avoid premature termination of the process.  The
			# reason is that when the first child terminates, all processes, e.g.
			# the second child, in the orphaned group will be sent a SIGHUP.
			#
			# "However, as part of the session management system, there are exactly
			# two cases where SIGHUP is sent on the death of a process:
			#
			#   1) When the process that dies is the session leader of a session that
			#      is attached to a terminal device, SIGHUP is sent to all processes
			#      in the foreground process group of that terminal device.
			#   2) When the death of a process causes a process group to become
			#      orphaned, and one or more processes in the orphaned group are
			#      stopped, then SIGHUP and SIGCONT are sent to all members of the
			#      orphaned group." [2]
			#
			# The first case can be ignored since the child is guaranteed not to have
			# a controlling terminal.  The second case isn't so easy to dismiss.
			# The process group is orphaned when the first child terminates and
			# POSIX.1 requires that every STOPPED process in an orphaned process
			# group be sent a SIGHUP signal followed by a SIGCONT signal.  Since the
			# second child is not STOPPED though, we can safely forego ignoring the
			# SIGHUP signal.  In any case, there are no ill-effects if it is ignored.
			#
			# import signal           # Set handlers for asynchronous events.
			# signal.signal(signal.SIGHUP, signal.SIG_IGN)
			try:
				# Fork a second child and exit immediately to prevent zombies.  This
				# causes the second child process to be orphaned, making the init
				# process responsible for its cleanup.  And, since the first child is
				# a session leader without a controlling terminal, it's possible for
				# it to acquire one by opening a terminal in the future (System V-
				# based systems).  This second fork guarantees that the child is no
				# longer a session leader, preventing the daemon from ever acquiring
				# a controlling terminal.
				pid		= os.fork()
			except OSError as e:
				raise Exception("{0} [{1}]".format(e.strerror, e.errno))

			if (pid == 0):
				# Since the current working directory may be a mounted filesystem, we
				# avoid the issue of not being able to unmount the filesystem at
				# shutdown time by changing it to the root directory.
				os.chdir(self.workdir)
				# We probably don't want the file mode creation mask inherited from
				# the parent, so we give the child complete control over permissions.
				os.umask(self.umask)
			else:
				# exit() or _exit()?  See below.
				os._exit(0)
		else:
			# exit() or _exit()?
			# _exit is like exit(), but it doesn't call any functions registered
			# with atexit (and on_exit) or any registered signal handlers.  It also
			# closes any open file descriptors.  Using exit() may cause all stdio
			# streams to be flushed twice and any temporary files may be unexpectedly
			# removed.  It's therefore recommended that child branches of a fork()
			# and the parent branch(es) of a daemon use _exit().
			os._exit(0)

		# Close all open file descriptors.  This prevents the child from keeping
		# open any file descriptors inherited from the parent.  There is a variety
		# of methods to accomplish this task.  Three are listed below.
		#
		# Try the system configuration variable, SC_OPEN_MAX, to obtain the maximum
		# number of open file descriptors to close.  If it doesn't exists, use
		# the default value (configurable).
		#
		# try:
		#    maxfd = os.sysconf("SC_OPEN_MAX")
		# except (AttributeError, ValueError):
		#    maxfd = self.maxfd
		#
		# OR
		#
		# if (os.sysconf_names.has_key("SC_OPEN_MAX")):
		#    maxfd = os.sysconf("SC_OPEN_MAX")
		# else:
		#    maxfd = self.maxfd
		#
		# OR
		#
		# Use the getrlimit method to retrieve the maximum file descriptor number
		# that can be opened by this process.  If there is not limit on the
		# resource, use the default value.
		#
		import resource
		maxfd				= resource.getrlimit(resource.RLIMIT_NOFILE)[1]
		if (maxfd == resource.RLIM_INFINITY):
			maxfd			= self.maxfd

		# Iterate through and close all file descriptors.
		for fd in range(0, maxfd):
			try:
				os.close(fd)
			except OSError:
				pass

		# Redirect the standard I/O file descriptors to the specified file.  Since
		# the daemon has no controlling terminal, most daemons redirect stdin,
		# stdout, and stderr to /dev/null.  This is done to prevent side-effects
		# from reads and writes to the standard I/O file descriptors.

		# This call to open is guaranteed to return the lowest file descriptor,
		# which will be 0 (stdin), since it was closed above.
		os.open(self.redir, os.O_RDWR)

		# Duplicate standard input to standard output and standard error.
		os.dup2(0, 1)
		os.dup2(0, 2)

