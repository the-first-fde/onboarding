# .claude

개발용 Claude Code 프로젝트 설정이다. 역할 분담과 개발 순서는 [CLAUDE.md](../CLAUDE.md)와 [AGENTS.md](../AGENTS.md)를 따른다.

- `settings.json`: 공유 설정. ECC 알림성 hook 비활성화(`ECC_DISABLED_HOOKS`), 명령 allow/deny 규칙
- `settings.local.json`, `local/`: 개인 로컬 설정. Git 제외

팀 시절의 프로젝트 hook·agents·skills는 제거했다. 품질·보안 검사는 ECC 플러그인 hook과 CI가 맡는다.
