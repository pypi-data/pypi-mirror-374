# Protein Turnover

protein turnover computations

Install with:

```bash
pip install protein-turnover
# If you plan to use non-western text for your job names maybe also install unidecode
# pip install Unidecode
# *OR*
pip install protein-turnover[unidecode]
```

This will give you a `turnover` command (equivalent to `python -m protein_turnover`).

A superior entry point is to use [uv](https://docs.astral.sh/uv/). With `uv` installed you can install
`protein-turnover` (+plus website) with

```bash
uv tool install protein-turnover --with=protein-turnover-website --with=gunicorn
```

## The Turnover Job File

To run protein-turnover you need to create a jobfile (which is in [toml format](https://toml.io)).

e.g.:

```toml
# job name is a display name and should contain information about what the job is about.
job_name = "My Experiment"
pepxml = "chx_cc_repeat.interact.pep.xml"
protxml = "chx_cc_repeat.combined.prot.xml"
# a list of mzML files
mzmlfiles = [ "milla009642.mzML"]
# internal job identifier (*optional* used to create auxilary filenames)
jobid = "job1"
# for cached data. If not specifies cache files will be placed in the
# same directories as original datafiles
cache_dir = "."
# email is *optional*
email = "me.lastname@uwa.edu.au"

[settings]
# these are the default settings
rtTolerance = 15.0
mzTolerance = 1e-5
labelledIsotopeNumber = 15
labelledElement = "N"
maximumLabelEnrichment = 0.95
retentionTimeCorrection = "SimpleMedian"
useObservedMz = false
minProbabilityCutoff = 0.8
enrichmentColumns = 10
```

So a minimal jobfile would be (say):

```toml
job_name = "My Experiment"
pepxml = "chx_cc_repeat.interact.pep.xml"
protxml = "chx_cc_repeat.combined.prot.xml"
mzmlfiles = [ "milla009642.mzML"]
```

### Notes:

- `email` will only work if the `config.MAIL_SERVER` is correct.
- `job_name` is really just a human readable short description of the job.
- `jobid` is used (mainly) to create filenames; for example the final sqlite output file will
  be called `{jobid}.sqlite`
- File names that are not absolute are relative to the _current working directory_ of the turnover process.
- If `[settings]` is missing the values will default to the example values above. You only
  need to specify values that are different from the ones above.
- `cache_dir`: see below.

## Running a Job

```bash
turnover run {jobfile}.toml
# *OR*
python -m protein_turnover run {jobfile}.toml

# alter configuration and use info level logging and log to logfile.log
turnover --level=info --logfile=logfile.log run {jobfile}.toml
```

### Cache Files and `cache_dir`

Turnover translates all the `.mzML`, `pep.xml`, and `prot.xml` files into pandas DataFrames
stored in `.parquet` [format](https://parquet.apache.org/), plus an internal (to turnover) format that make it easy to quickly scan spectra using [`mmap`](https://docs.python.org/3/library/mmap.html).

These files are cached in `cache_dir` based on an sha256 hash of the contents of each file.
Thus re-runs of the job don't need to (re)-generate these files again.

Because of the sha256 hash you can used a single `cache_dir` for _all_ jobs.

If the cache files are deleted, they will be recreated when the job is run again.

If `cache_dir` is not specified the the
cached files will be placed in the same directory as the originator xml files.

## Viewing

One the job has run you can view the results in a browser

```bash
pip install protein-turnover-website
turnover view {jobfile}.toml
```

# Windows

A default install of python on [windows](https://www.python.org/downloads/windows/)
Will give you a `py` function instead of a `python` function. Go to the search bar and type `cmd`. In
the `cmd` shell you should use instead of `turnover ...` `py -m protein_turnver ...`
