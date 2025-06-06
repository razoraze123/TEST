import argparse
import os
import logger_setup  # noqa: F401
import config
import config_manager
from scraper_core import ScraperCore
from optimizer import ImageOptimizer
from image_pipeline import run_pipeline, replay_workflow


def run_scrape(args):
    core = ScraperCore(
        base_dir=config.BASE_DIR,
        chrome_driver_path=config.CHROME_DRIVER_PATH,
        chrome_binary_path=config.CHROME_BINARY_PATH,
    )
    id_url_map = core.charger_liens_avec_id(config.LINKS_FILE_PATH)
    ids = list(id_url_map.keys())
    summary = core.start_scraping(
        id_url_map,
        ids,
        ["variantes", "concurrents", "json"],
        driver_path=config.CHROME_DRIVER_PATH,
        binary_path=config.CHROME_BINARY_PATH,
        headless=args.headless,
        concurrent=args.concurrent,
        resume=args.resume,
    )
    print(summary)


def run_scrape_images(args):
    core = ScraperCore(
        base_dir=config.BASE_DIR,
        chrome_driver_path=config.CHROME_DRIVER_PATH,
        chrome_binary_path=config.CHROME_BINARY_PATH,
    )
    urls = core.charger_liste_urls(config.LINKS_FILE_PATH)
    dest = os.path.join(config.BASE_DIR, config.ROOT_FOLDER)
    result = core.scrap_images(
        urls,
        dest,
        driver_path=config.CHROME_DRIVER_PATH,
        binary_path=config.CHROME_BINARY_PATH,
        suffix=args.suffix,
        headless=args.headless,
    )
    print(result)


def run_optimize(args):
    optimizer = ImageOptimizer(config.OPTIPNG_PATH, config.CWEBP_PATH)
    logs = optimizer.optimize_folder(args.folder)
    for line in logs:
        print(line)


def run_resume(args):
    args.resume = True
    run_scrape(args)


def run_plugin(args):
    if args.list:
        plugins = _available_plugins()
        print("\n".join(plugins))
        return
    if args.use:
        data = config_manager.load()
        data["SCRAPER_PLUGIN"] = args.use
        config_manager.save(data)
        print(f"Plugin set to {args.use}")
        return
    print(f"Active plugin: {config.SCRAPER_PLUGIN}")


def run_workflow(args):
    if args.replay is not None:
        replay_workflow(args.replay)
    else:
        run_pipeline(args.config)


def _available_plugins():
    path = os.path.join(os.path.dirname(__file__), "plugins")
    mods = []
    for name in os.listdir(path):
        if name.endswith(".py") and name not in {"__init__.py", "base.py"}:
            mods.append(f"plugins.{name[:-3]}")
    return sorted(mods)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="woocommerce-scraper",
        description="Command line tools for the WooCommerce scraper",
    )
    sub = parser.add_subparsers(dest="command")

    p_scrape = sub.add_parser("scrape", help="Scrape product descriptions")
    p_scrape.add_argument("--headless", action="store_true", help="Run Chrome headless")
    p_scrape.add_argument("--concurrent", action="store_true", help="Use async scraping")
    p_scrape.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    p_scrape.set_defaults(func=run_scrape)

    p_images = sub.add_parser("scrape-images", help="Scrape product images")
    p_images.add_argument("--headless", action="store_true", help="Run Chrome headless")
    p_images.add_argument("--suffix", default="image-produit", help="Suffix for alt text")
    p_images.set_defaults(func=run_scrape_images)

    p_opt = sub.add_parser("optimize", help="Optimize an image folder")
    p_opt.add_argument("folder", help="Folder containing images")
    p_opt.set_defaults(func=run_optimize)

    p_resume = sub.add_parser("resume", help="Resume a previous scraping run")
    p_resume.add_argument("--headless", action="store_true", help="Run Chrome headless")
    p_resume.add_argument("--concurrent", action="store_true", help="Use async scraping")
    p_resume.set_defaults(func=run_resume)

    p_plugin = sub.add_parser("plugin", help="Manage scraping plugins")
    p_plugin.add_argument("--list", action="store_true", help="List available plugins")
    p_plugin.add_argument("--use", metavar="MODULE", help="Activate plugin module")
    p_plugin.set_defaults(func=run_plugin)

    p_work = sub.add_parser("workflow", help="Run an image workflow")
    p_work.add_argument("config", help="Path to workflow config file")
    p_work.add_argument("--replay", type=int, help="Replay workflow by id")
    p_work.set_defaults(func=run_workflow)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
