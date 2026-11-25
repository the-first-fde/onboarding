"""외부 통신 없이 기술 검증만 실행하는 진입점."""

import asyncio

from hr_onboarding.smoke import run_smoke

if __name__ == "__main__":
    print(f"Mock graph count: {asyncio.run(run_smoke())}; HR functionality deferred")
