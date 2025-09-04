from prune_norminette.utils.display_result import display_results
from prune_norminette.utils.run_checks import run_checks
from prune_norminette.utils.setup_django import initialize_django


def main():
    if not initialize_django():
        return

    errors = run_checks()

    display_results(errors)


if __name__ == "__main__":
    main()
