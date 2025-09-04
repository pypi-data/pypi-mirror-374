# SQ3M - AI 기반 데이터베이스 쿼리 도우미

<!-- Language Toggle -->
<div align="center">

[**🇺🇸 English**](README.md) | [**🇰🇷 한국어**](#)

</div>

대형 언어 모델(LLM)을 사용하여 자연어 쿼리를 SQL로 변환하는 Python CLI 도구입니다. 클린 아키텍처 원칙으로 구축되었습니다.

## 🚀 주요 기능

- 🤖 **OpenAI completion 모델을 사용한 자연어-SQL 변환**
- 🗄️ **MySQL, PostgreSQL 다중 데이터베이스 지원**
- 🧠 **LLM을 활용한 자동 테이블 목적 추론**
- 🎨 **Rich를 사용한 아름다운 CLI 인터페이스**
- ⚙️ **환경 변수 구성**
- 🏗️ **클린 아키텍처 설계**

## 📦 설치

### pip 사용
```bash
pip install sq3m
```

### uv 사용 (개발용 권장)
```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 저장소 클론 및 설정
git clone https://github.com/leegyurak/sq3m.git
cd sq3m
uv sync
```

## ⚙️ 구성

`.env` 파일에 환경 변수를 설정하거나 export하세요:

```bash
# OpenAI 구성
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-3.5-turbo  # 선택사항, 기본값: gpt-3.5-turbo

# 데이터베이스 구성 (선택사항 - 대화형으로 설정 가능)
export DB_TYPE=mysql  # mysql 또는 postgresql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=your_database
export DB_USERNAME=your_username
export DB_PASSWORD=your_password

# 언어 구성 (선택사항)
export LANGUAGE=ko  # en (영어) 또는 ko (한국어), 기본값: en
```

### 🌍 다국어 지원

sq3m은 `LANGUAGE` 환경변수를 통해 다양한 시스템 프롬프트 언어를 지원합니다:

- **지원 언어**:
  - `en`: 영어 (기본값)
  - `ko`: 한국어

- **시스템 프롬프트 우선순위**:
  1. 사용자 지정 경로 매개변수 (직접 지정)
  2. `SYSTEM_PROMPT_PATH` 환경변수 (절대 경로)
  3. `SYSTEM_PROMPT_FILE` 환경변수 (설정 디렉토리의 파일명)
  4. **언어별 기본 프롬프트** (LANGUAGE 환경변수 기반)
  5. 기본 fallback 프롬프트

**사용 예시:**
```bash
# 한국어 시스템 프롬프트 사용
export LANGUAGE=ko
sq3m

# 또는 .env 파일에서 설정
echo "LANGUAGE=ko" >> .env
```

## 🔧 사용법

CLI 도구 실행:

```bash
sq3m
```

도구는 다음 단계로 안내합니다:

1. **🤖 LLM 설정**: OpenAI API 키 구성 (환경에 없는 경우)
2. **🗄️ 데이터베이스 연결**: 데이터베이스 연결 설정 (환경에 없는 경우 대화형)
3. **📊 스키마 분석**: 모든 테이블을 자동으로 분석하고 목적 추론
4. **💬 대화형 쿼리**: 자연어로 질문하기

### 💡 쿼리 예시

- "모든 사용자 보여줘"
- "지난달 주문 찾기"
- "카테고리별 제품 수 세기"
- "사용자 ID 123의 사용자 세부정보 보여줘"
- "가장 잘 팔리는 제품 5개는 뭐야?"

### 🎯 CLI 명령어

- `tables` - 모든 데이터베이스 테이블과 그 목적 표시
- `help` 또는 `h` - 사용 가능한 명령어 표시
- `quit`, `exit`, 또는 `q` - 애플리케이션 종료

## 🏗️ 아키텍처

프로젝트는 클린 아키텍처 원칙을 따릅니다:

```
sq3m/
├── domain/           # 비즈니스 로직과 엔티티
│   ├── entities/     # 핵심 비즈니스 객체
│   └── interfaces/   # 추상 인터페이스
├── application/      # 유스케이스와 비즈니스 규칙
│   ├── services/     # 애플리케이션 서비스
│   └── use_cases/    # 특정 비즈니스 유스케이스
├── infrastructure/   # 외부 인터페이스
│   ├── database/     # 데이터베이스 구현체
│   ├── llm/          # LLM 서비스 구현체
│   └── prompts/      # 시스템 프롬프트
├── interface/        # 사용자 인터페이스
│   └── cli/          # CLI 구현체
└── config/           # 구성 관리
```

## 🛠️ 개발

### 사전 요구사항

- **Python 3.10+**
- **uv** 패키지 매니저 (빠른 의존성 관리를 위해 권장)

### UV 패키지 매니저 설정

이 프로젝트는 빠른 Python 패키지 관리를 위해 [uv](https://github.com/astral-sh/uv)를 사용합니다.

**uv 설치:**
```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 pip로 설치
pip install uv
```

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/leegyurak/sq3m.git
cd sq3m

# Python 환경 초기화 및 의존성 설치
uv sync --all-extras --dev

# pre-commit 훅 설치
uv run pre-commit install
```

**가상환경 활성화 (선택사항):**
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 개발 워크플로우

1. **코드 변경**
2. **테스트 실행**: `uv run pytest`
3. **린팅 실행**: `uv run ruff check --fix .`
4. **포맷팅 실행**: `uv run ruff format .`
5. **타입 체킹 실행**: `uv run mypy sq3m/`
6. **변경사항 커밋** (pre-commit 훅이 자동으로 실행됨)

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest

# 단위 테스트만 실행
uv run pytest tests/unit

# 통합 테스트 실행
uv run pytest tests/integration

# 커버리지와 함께 실행
uv run pytest --cov=sq3m

# 느린 테스트 제외하고 실행
uv run pytest -m "not slow"
```

### 코드 품질

```bash
# ruff로 린팅 및 포맷팅
uv run ruff check --fix .
uv run ruff format .

# 타입 체킹
uv run mypy sq3m/

# pre-commit 훅 (커밋 시 자동 실행)
uv run pre-commit run --all-files
```

### 애플리케이션 실행

```bash
# uv로 직접 실행
uv run sq3m

# 또는 환경 활성화 후 실행
source .venv/bin/activate
sq3m
```

## 📚 의존성

### 런타임 의존성
- **click**: CLI 프레임워크
- **rich**: 아름다운 터미널 UI
- **openai**: OpenAI API 클라이언트
- **python-dotenv**: 환경 변수 관리
- **psycopg2-binary**: PostgreSQL 드라이버
- **pymysql**: MySQL 드라이버
- **sqlparse**: SQL 파싱 유틸리티
- **pydantic**: 데이터 검증

### 개발 의존성
- **pytest**: 테스트 프레임워크
- **pytest-cov**: 커버리지 리포팅
- **pytest-asyncio**: 비동기 테스트 지원
- **ruff**: 빠른 Python 린터 및 포맷터
- **pre-commit**: Git 훅 프레임워크
- **mypy**: 정적 타입 체커

## 📋 요구사항

- **Python**: 3.10 이상
- **uv**: 패키지 매니저 (권장) 또는 pip

## 🤝 기여하기

기여를 환영합니다! Pull Request를 자유롭게 제출해 주세요.

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 열기

## 📝 라이센스

이 프로젝트는 MIT 라이센스에 따라 라이센스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- completion 모델을 제공해주신 OpenAI에 감사드립니다
- 현대적인 Python 도구로 구축: uv, ruff, pytest
- 클린 아키텍처 원칙에서 영감을 받았습니다
