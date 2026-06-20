from argparse import ArgumentParser

from ai.coder import CoderAgent
from ai.planner import PlannerAgent
from ai.reviewer import ReviewAgent
from routing.intent_router import IntentRouter


def run_review(args):
    print(ReviewAgent.review_project(args.path))


def run_edit(args):
    plan = PlannerAgent.create_plan(args.task)
    if getattr(args, "show_plan", True):
        from rich.console import Console
        from rich.panel import Panel

        Console().print(Panel(plan, title="🟡 Plan", border_style="yellow"))
    code = CoderAgent.generate_code(args.task, plan)
    if getattr(args, "show_solution", True):
        from rich.console import Console
        from rich.panel import Panel

        Console().print(Panel(code, title="🟢 Generated Solution", border_style="green"))


def run_classify(args):
    print(IntentRouter.route(args.prompt))


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("path")

    edit_parser = subparsers.add_parser("edit")
    edit_parser.add_argument("task")
    edit_parser.add_argument("--planner-model", default="qwen3:8b")
    edit_parser.add_argument("--coder-model", default="qwen2.5-coder:7b")
    edit_parser.add_argument("--classifier-model", default="qwen3.5:0.8b")
    edit_parser.add_argument("--show-plan", action="store_true")
    edit_parser.add_argument("--show-solution", action="store_true")

    classify_parser = subparsers.add_parser("classify")
    classify_parser.add_argument("prompt")
    classify_parser.add_argument("--classifier-model", default="qwen3.5:0.8b")

    args = parser.parse_args()

    if args.command == "review":
        run_review(args)
    elif args.command == "edit":
        run_edit(args)
    elif args.command == "classify":
        run_classify(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
