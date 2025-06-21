from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent
from common.config import settings


def main():
    print(settings.LANGSMITH_PROJECT)


if __name__ == '__main__':
    main()
