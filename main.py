from strategies.indicator_suite_strategy import IndicatorSuiteStrategy
from strategies.ict_strategy import ICTStrategy
from strategies.rtm_strategy import RTMStrategy
from core.bot_engine import BotEngine
from utils.logger import get_logger
from utils.config import CONFIG

log = get_logger("Main", CONFIG["logging_level"])

if __name__ == "__main__":
    strategies = [IndicatorSuiteStrategy()]
    if CONFIG["features"]["ICT"]:
        strategies.append(ICTStrategy())
    if CONFIG["features"]["RTM"]:
        strategies.append(RTMStrategy())
    bot = BotEngine(strategies)
    bot.run_once()
