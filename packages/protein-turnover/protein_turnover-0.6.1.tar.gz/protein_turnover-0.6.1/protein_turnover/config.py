from __future__ import annotations


MIN_RT = 2
ABUNDANCE_CUTOFF = 0.01
# split jobs into this many spectra
# set to zero to not split
NSPECTRA = 10000
# quadrature limit for estimating area under curve (unused now)
# see USE_QUAD in fitenvelopes.py
# QUAD_LIMIT = 500
# https://docs.python.org/3/library/logging.html#logrecord-attributes
LOG_FORMAT = "%(levelname)s|[%(asctime)s]|%(process)d| %(message)s"

# XCMS_STEP = 0.0
PEPXML_CHUNKS = 1000

MAIL_SUBJECT = "turnover pipeline"
# default "from" sender
MAIL_SENDER = "turnover-pipeline@uwa.edu.au"
# set to None or 'none' to stop any emailing
# e.g. MAIL_SERVER="uwa-edu-au.mail.protection.outlook.com"
MAIL_SERVER = "mailhost"
MAIL_TIMEOUT = 20.0
# e.g. "https://protein-turnover.plantenergy.org/inspect/{jobid}"
INSPECT_URL: str | None = None
# email template with {job:TurnoverJob, url:str}
MAIL_TEXT = """Protein Turnover Job "{job.job_name}" has <b>finished</b>!{url}."""
# set to True for production version (hides debug click commands)

INTERPOLATE_INTENSITY = True

# add origin...
WITH_ORIGIN = False

# Dinosaur
JAVA_PATH = None  # "java"
DINOSAUR_JAR = None

SQLITE_VERSION = 1
