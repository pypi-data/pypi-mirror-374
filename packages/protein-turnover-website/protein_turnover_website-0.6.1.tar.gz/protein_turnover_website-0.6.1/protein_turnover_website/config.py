from __future__ import annotations


# only used with email logger
ADMINS: list[str] = []  # ['your.email@gmail.com']
MAIL_SUBJECT = "turnover pipeline website"
# where should logger send email to...
# e.g. LOG_MAIL_SERVER="uwa-edu-au.mail.protection.outlook.com"
# use "none" to ensure no SMTP logger
LOG_MAIL_SERVER = "mailhost"
# note that where an email is sent by the background process
# is determined by the MAIL_SERVER configuration of `protein_turnover`
# The LOG_MAIL_SERVER above is only for the flask SMTP error logger
# Use 2 for email is required else 0 for don't need email
WANT_EMAIL = 1

# used for input placeholder
MAIL_PLACEHOLDER = "your.name@uwa.edu.au"

CAN_KILL_JOBS = True


# start length for datatables.net
PROTEIN_PAGE_LENGTH = 50


# These are the top directory locations available to users
# of this website. All files below these points will be visible.

# Tuple of "absolute path of directory", "nickname" , "file restriction regex [optional]"

# most restrictive/longest path first! e.g.
# restrict = r"^.*\.(mzML|pep.xml)$"
# MOUNTPOINTS = [
#     ("/path/to/protein_turnover_data", "Turnover", restrict),
#     ("/path/to/home", "HOME"),
# ]
MOUNTPOINTS = [("~", "HOME")]
# Don't allow soft links in MountPoint directory trees...
# If set to True then the file paths stored in the TurnoverJob file
# will adhere to the soft link path
ALLOW_LINKS = True

# where jobsfile live [required]
# JOBSDIR = "/path/to/jobs-directory"
JOBSDIR = "~/turnover_jobs"

# where cache files live [required]
# CACHEDIR = "/path/to/cachedir"
CACHEDIR = "~/turnover_cache"

dpi = 96
FIG_SIZE = (642.0 / dpi, 400.0 / dpi)
# rows, columns
# 1,3 for landscape
# 3,1 for portrait
# if 4 or more axes the intensities are plotted too
FIG_LAYOUT = (2, 2)

# only for debug sessions
ECHO_QUERY = False
# wait 60 secs for download to complete (checking every second)
COOKIE_MAX_ATTEMPTS = 60

# set this to true for nginx
# USE_X_SENDFILE = False
# last 1000 bytes of logfile
LOG_READ = 1000
# for HTML meta tags like "canonical"
SITE_URL = "https://turnover.plantenergy.edu.au"
# delay (ms) before we switch from job create page to
# job index page after submitting a new job
REFRESH_DELAY = 1000

# set this to ensure a password is required
# can be a simple password string or a dictionary of {email: password}
SITE_PASSWORD: str | dict[str, str] | None = None

STAT_FILES = -1
