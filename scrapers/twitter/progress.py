import sys


class Progress:
    def __init__(self, current, total) -> None:
        self.current = current
        self.total = total

    def print_progress(self, current, waiting, retry_cnt, no_tweets_limit) -> None:
        self.current = current
        progress = current / self.total
        bar_length = 40
        progress_bar = "[" + "=" * int(bar_length * progress) + "-" * (bar_length - int(bar_length * progress)) + "]"

        if no_tweets_limit:
            message = f"Tweets scraped : {current} - waiting to access older tweets {retry_cnt} min on 15 min"\
                if waiting else f"Tweets scraped : {current}"
        else:
            message = (f"Progress: [{progress_bar:<40}] {progress:.2%} {current} of {self.total}"
                       f" - waiting to access older tweets {retry_cnt} min on 15 min") \
                if waiting else f"Progress: [{progress_bar:<40}] {progress:.2%} {current} of {self.total}"

        sys.stdout.write("\r" + message)
        sys.stdout.flush()