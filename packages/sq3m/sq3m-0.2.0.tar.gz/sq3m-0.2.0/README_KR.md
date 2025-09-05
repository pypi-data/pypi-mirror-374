# SQ3M - AI 기반 데이터베이스 쿼리 어시스턴트

자연어를 SQL로 변환하는 Python CLI 도구입니다. 대형 언어 모델(LLM)을 사용하며 클린 아키텍처 원칙으로 구축되었습니다.

## 🚀 주요 기능

- 🤖 **자연어를 SQL로 변환** - OpenAI 완성 모델 사용
- 🗄️ **다중 데이터베이스 지원** - MySQL과 PostgreSQL 지원
- 🧠 **자동 테이블 용도 추론** - LLM을 사용한 테이블 목적 분석
- 🎨 **아름다운 CLI 인터페이스** - Rich 라이브러리 사용
- ⚙️ **환경 변수 구성**
- 🏗️ **클린 아키텍처 설계**
- 🔍 **하이브리드 검색** - 벡터 유사도 + 키워드 검색으로 관련 테이블 찾기

## 📦 설치

### pip 사용
```bash
pip install sq3m
```

### uv 사용 (개발 권장)
```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 저장소 클론 및 설정
git clone https://github.com/leegyurak/sq3m.git
cd sq3m
uv sync
```

## ⚙️ 구성

`.env` 파일에서 환경 변수를 설정하거나 내보내기:

```bash
# OpenAI 구성
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-3.5-turbo  # 선택사항, 기본값은 gpt-3.5-turbo

# 데이터베이스 구성 (선택사항 - 대화형으로 설정 가능)
export DB_TYPE=mysql  # mysql 또는 postgresql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=your_database
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
```

## 🔧 사용 방법

### 빠른 시작

1. **sq3m 설치**:
   ```bash
   pip install sq3m
   ```

2. **OpenAI API 키 설정**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   ```

3. **도구 실행**:
   ```bash
   sq3m
   ```

4. **자연어 질문하기**:
   ```
   🤔 무엇을 알고 싶으신가요: 지난 주에 생성된 모든 사용자를 보여주세요
   ```

### 사용 가능한 명령어

대화형 세션에서:

| 명령어 | 설명 |
|--------|------------|
| 자연어 쿼리 | "모든 사용자 표시", "이번 달 주문 찾기" 등 |
| `tables` | 모든 데이터베이스 테이블과 AI가 추론한 목적 표시 |
| `help` 또는 `h` | 사용 가능한 명령어 표시 |
| `quit`, `exit`, 또는 `q` | 애플리케이션 종료 |

### 🔧 고급 구성

작업 디렉터리에 `.env` 파일 생성:

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4  # 더 나은 결과를 위해 GPT-4 사용

DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_production
DB_USERNAME=myuser
DB_PASSWORD=mypassword
```

### 💡 더 나은 결과를 위한 팁

1. **구체적으로 질문**: "사용자 표시" 대신 "이번 주에 생성된 사용자 표시"
2. **테이블 이름 사용**: 알고 있다면 특정 테이블 이름 언급
3. **후속 질문**: "이메일 주소도 표시할 수 있나요?"
4. **비즈니스 용어 사용**: "판매 합계" 대신 "월별 매출 표시"

## 🏗️ 아키텍처

이 프로젝트는 클린 아키텍처 원칙을 따릅니다:

```
sq3m/
├── domain/           # 비즈니스 로직 및 엔티티
├── application/      # 사용 사례 및 서비스
├── infrastructure/   # 외부 관심사 (데이터베이스, LLM, CLI)
└── interface/        # 사용자 인터페이스 (CLI)
```

### 주요 구성 요소:
- **도메인 계층**: 데이터베이스 엔티티, SQL 쿼리, 비즈니스 규칙
- **애플리케이션 계층**: 데이터베이스 분석, SQL 생성, 테이블 검색 서비스
- **인프라 계층**: OpenAI 통합, 데이터베이스 연결, 프롬프트 관리
- **인터페이스 계층**: Rich 기반 CLI

## 🔍 하이브리드 검색 시스템

SQ3M은 고급 하이브리드 검색을 사용하여 쿼리에 가장 관련성이 높은 테이블을 찾습니다:

- **벡터 검색**: OpenAI 임베딩을 사용한 의미론적 유사성
- **키워드 검색**: SQLite FTS5를 사용한 전체 텍스트 검색
- **순위 융합**: RRF(Reciprocal Rank Fusion) 알고리즘으로 결과 결합
- **스마트 제한**: LLM 컨텍스트를 관련성 높은 상위 10개 테이블로 제한

## 🤝 기여

기여를 환영합니다! 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [OpenAI](https://openai.com/)의 강력한 언어 모델
- [Rich](https://rich.readthedocs.io/)의 아름다운 터미널 출력
- [Click](https://click.palletsprojects.com/)의 CLI 프레임워크
- 클린 아키텍처에 대한 Robert C. Martin의 아이디어
