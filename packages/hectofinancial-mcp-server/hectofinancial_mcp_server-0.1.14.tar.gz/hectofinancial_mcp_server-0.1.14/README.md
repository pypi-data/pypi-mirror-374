# 헥토파이낸셜 MCP 서버

헥토파이낸셜의 연동 문서를 쉽고 빠르게 검색·조회할 수 있는 MCP 서버입니다.

> **MCP란?** Model Context Protocol의 줄임말로, "AI를 위한 USB-C 포트"라고 불리며, LLM이 외부 데이터와 도구에 표준화된 방식으로 접근할 수 있게 해주는 프로토콜입니다.

## 📋 개요

이 MCP 서버는 헥토파이낸셜의 연동 문서를 검색하고, 개발자들이 필요한 정보를 빠르게 찾을 수 있도록 도와줍니다. 전자결제(PG), 내통장결제, 간편현금결제, 화이트라벨 서비스 관련 문서를 제공합니다.

### 🛠️ 제공 도구

| 도구 | 설명 |
|------|------|
| **`search_docs`** | 키워드 및 카테고리를 통해 헥토파이낸셜 연동 문서를 검색합니다. 카테고리(PG, 내통장결제, 간편현금결제, 화이트라벨)를 명시하면 검색 정확성이 향상됩니다. |
| **`list_docs`** | 전체 연동 문서 목록을 조회합니다. 카테고리별(PG, 내통장결제, 간편현금결제, 화이트라벨) 필터링을 제공합니다. |
| **`get_docs`** | 문서 ID 또는 파일명으로 특정 문서의 전체 내용을 조회합니다. |

## 🚀 사용 방법

### 요구사항
- Python 3.10+
- uv 설치 필수
- MCP 클라이언트 (Cursor, Claude Desktop 등)

### uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🖇️ MCP 클라이언트 연동

### Cursor
**🔗 원클릭 설정:** [Cursor에서 바로 설정하기](cursor://anysphere.cursor-deeplink/mcp/install?name=hectofinancial-mcp-server&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJoZWN0b2ZpbmFuY2lhbC1tY3Atc2VydmVyQGxhdGVzdCJdfQo=)

또는 프로젝트 루트에 `.cursor/mcp.json` 파일을 생성:

```json
{
  "mcpServers": {
    "hecto-financial": {
      "command": "uvx",
      "args": ["hectofinancial-mcp-server@latest"]
    }
  }
}
```
### VS Code
**🔗 원클릭 설정:** [VS Code에서 바로 설정하기](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22hectofinancial-mcp-server%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22hectofinancial-mcp-server%40latest%22%5D%7D)

**수동 설정 방법:**
1. VS Code에서 `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)를 눌러 명령 팔레트 열기
2. "Preferences: Open User Settings (JSON)" 검색 후 선택
3. `settings.json` 파일에 다음 설정 추가:

```json
{
  "mcp": {
    "servers": {
      "hectofinancial-mcp-server": {
        "command": "uvx",
        "args": [
          "hectofinancial-mcp-server@latest"
        ]
      }
    }
  }
}
```

### Claude Desktop
`~/.claude_desktop_config.json` 파일에 추가:

```json
{
  "mcpServers": {
    "hecto-financial": {
      "command": "uvx",
      "args": ["hectofinancial-mcp-server@latest"]
    }
  }
}
```

### 기타 MCP 클라이언트
다른 MCP 클라이언트에서도 다음과 같은 설정을 사용할 수 있습니다:

```json
{
  "mcpServers": {
    "hecto-financial": {
      "command": "uvx",
      "args": ["hectofinancial-mcp-server@latest"]
    }
  }
}
```

## 💬 사용 예시

MCP 클라이언트(Cursor, Claude Desktop 등)에서 다음과 같은 질문들을 시도해보세요:

### 🔍 연동 가이드 검색
> **⌨️** "헥토파이낸셜 신용카드 결제 연동 방법 알려줘"  
> **⌨️** "내통장결제 API 호출 어떻게 해?"  
> **⌨️** "간편현금결제 휴대폰 인증 구현법 찾아줘"  
> **⌨️** "화이트라벨 서비스 사용법 알려줘"

### 🔧 실제 구현 질문
> **⌨️** "PG에서 결제 승인 후 noti 처리는 어떻게 해?"  
> **⌨️** "내통장결제에서 테스트 환경 URL과 상용 환경 URL 차이점은?"  
> **⌨️** "간편현금결제에서 정기결제 등록하는 방법 알려줘"  
> **⌨️** "PG에서 결제 취소 API 사용법은?"

## 📄 License

This project is licensed under the MIT License.