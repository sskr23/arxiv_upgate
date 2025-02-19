#!/Users/ssakurai/Article/arXiv/arxiv/bin/python
##################################################
#####
##### arxiv_check.py
##### Author: S.Sakurai
##### Date  : 20250219
##### get arxiv information into markdown
#####
##################################################
# Package
from arxiv import Search, SortCriterion, Client
from datetime import datetime, timedelta, timezone
from argparse import ArgumentParser
from sys import argv
from os import path
from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter

# Logger config
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = StreamHandler()
handler.setLevel(INFO)
shfmt = "%(asctime)s: %(name)s [%(levelname)s] > %(message)s"
handler.setFormatter(Formatter(shfmt))
logger.addHandler(handler)  # Need to activate it
# Parser config, no longer used.
parser = ArgumentParser(
    prog=f"{argv[0]}", description="get arXiv updates for past one week automatically"
)
# parser.add_argument("-y", "--year", default="2025", type=int)
# parser.add_argument("-d", "--day", type=int)
# parser.add_argument("-m", "--month", type=int)
# parser.add_argument("-l", "--length", type=int, default=2)
args = parser.parse_args()
DATE_FORMAT = "%Y%m%d%H%M"


def set_search_condition(date_beg_str, date_end_str):
    cut_category = "astro-ph.*"
    cut_date = f"[{date_beg_str:s} TO {date_end_str:s}]"
    search = Search(
        query=f"cat:{cut_category} AND submittedDate:{cut_date}",
        max_results=1000,
        sort_by=SortCriterion.SubmittedDate,
    )
    return search


def write_search_result(ofilename, date_beg_str, client, search):
    with open(ofilename, "w") as ofile:
        # show result in standard stream
        # writ down result in dile
        ofile.write(f"# arXiv updates on {date_beg_str[:-4]:s}\n\n")
        for ir, result in enumerate(client.results(search)):
            # if 'gamma' in result.title or 'Gamma' in result.title or 'gamma' in result.summary or 'Gamma' in result.summary: not implemented
            ofile.write(f"## {ir:03d}: {result.title}\n\n")
            ofile.write(f"Category: {result.primary_category}\n\n")
            ofile.write(f"[{result.entry_id.split("/")[-1]}]({result.entry_id})\n\n")
            ofile.write(f"> {result.summary}\n\n")


def arxiv_check():
    # check past 1week (-2 day in UTC to -9 day in UTC)
    time_utc = datetime.now(timezone.utc)
    # date_utc_begin = (time_utc + datetime.timedelta(days=-8)).date()
    # print(date_utc_begin)
    fname_template = "prompt_arxiv_"
    # check wether files are exits
    ioffset_process = []
    for i in range(7):
        # no updates in -1 day
        day_offset = -(int(i) + 2)
        date_check = (time_utc + timedelta(days=day_offset)).date()
        str_date_check = date_check.strftime("%y%m%d")
        if path.isfile(f"{fname_template}{str_date_check}.md"):
            logger.info(f"Skipping {str_date_check}")
        else:
            logger.info(f"Check {str_date_check}")
            ioffset_process.append(day_offset)
    client = Client()

    for j in ioffset_process:
        date_get = (time_utc + timedelta(days=j)).date()
        logger.debug(date_get)
        # to calculate a time difference properly, it seems that one need to set hours explicitly.
        date_begin = datetime(
            year=date_get.year,
            month=date_get.month,
            day=date_get.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        logger.debug(date_begin)
        # arxiv API requires just several seconds before from the end of the day
        date_end = date_begin + timedelta(hours=24, minutes=-1)
        # converting format required by arXiv API
        date_beg_str = date_begin.strftime(DATE_FORMAT)
        date_end_str = date_end.strftime(DATE_FORMAT)
        logger.info(f"BEGIN: {date_beg_str}")
        logger.info(f"END:   {date_end_str}")
        search = set_search_condition(date_beg_str, date_end_str)
        logger.debug(search)
        ofilename = f"{fname_template}{date_begin.strftime("%y%m%d")}.md"
        write_search_result(ofilename, date_beg_str, client, search)
        # define which days will be processed
        # date_begin = datetime(args.year, args.month, args.day)
        # date_end = date_begin + timedelta(
        #    days=args.length, seconds=3600 * 24 - 60
        # )  # Needs to be the end of the day.


if "__main__" == __name__:
    arxiv_check()
