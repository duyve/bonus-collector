import argparse
from rbrapi import RocketBotRoyale
from rbrapi.errors import AuthenticationError, CollectTimedBonusError, LootBoxError
from logger import Logger
from time import sleep
import os


def notify(title, text, sound):
    if sound is not None:
        os.system(f"afplay {sound}" )
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))



def parse_args():
    parser = argparse.ArgumentParser(description="RocketBotRoyale bonus collector.")
    parser.add_argument("--email", type=str, help="Email for RocketBotRoyale account")
    parser.add_argument(
        "--password", type=str, help="Password for RocketBotRoyale account"
    )
    parser.add_argument("--no-logging", action="store_true", help="Disable logging")
    parser.add_argument(
        "--auto-open-crates",
        type=str,
        help="Automatically open crates if available. Set value to 1 for regular crates, 2 for premium crates."
    )
    parser.add_argument("--notify", action="store_true", help="Enable system notifications on macOS")
    return parser.parse_args()


def main():
    args = parse_args()

    email = args.email if args.email else input("Enter email: ")
    password = args.password if args.password else input("Enter password: ")

    if args.no_logging:
        logger = None
    else:
        logger = Logger(__name__)

    while True:
        try:
            client = RocketBotRoyale(email, password)

            client.collect_timed_bonus()
            logger.info("Coins collected successfully.")

            coins = client.account().wallet["coins"]
            logger.info(f"Your coins now: {coins}.")
            if args.notify:
                notify("RocketBotRoyale", f"Coins collected successfully. Your coins now: {coins}.", "coin.mp3")

            if args.auto_open_crates :
                if args.auto_open_crates == "1" and coins >= 1000:
                    award = client.buy_crate()
                    logger.info(f"Crate award is: {award.award_id}")
                    if args.notify:
                        notify("RocketBotRoyale", f"Crate award is: {award.award_id}", "crate.mp3")
                if args.auto_open_crates == "2" and coins >= 20000:
                    award = client.buy_crate(elite=True)
                    logger.info(f"Crate award is: {award.award_id}")
                    if args.notify:
                        notify("RocketBotRoyale", f"Crate award is: {award.award_id}", "crate.mp3")

        except AuthenticationError as e:
            logger.error(f"Unable to authenticate: {e}")
        except CollectTimedBonusError as e:
            logger.info(f"Bonus not available to claim yet: {e}")
        except LootBoxError as e:
            logger.error(f"Unable to open crates: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
        finally:
            sleep(60 * 5)


if __name__ == "__main__":
    main()
