# UV 설정 가이드

이 프로젝트는 `uv`를 사용하여 Python 패키지 관리를 합니다.

## UV 설치

먼저 `uv`가 설치되어 있는지 확인하세요:

```bash
uv --version
```

설치되어 있지 않다면 다음 명령어로 설치할 수 있습니다:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

또는 pip를 통해 설치:

```bash
pip install uv
```

## 프로젝트 설정

### 1. 가상 환경 생성 및 의존성 설치

프로젝트 루트 디렉토리에서 다음 명령어를 실행하세요:

```bash
cd /home/ubuntu/Threelacha_streamlit
uv venv
```

### 2. 가상 환경 활성화

```bash
source .venv/bin/activate
```

### 3. 의존성 설치

```bash
uv pip install -e .
```

또는 `pyproject.toml`의 의존성을 직접 설치:

```bash
uv pip install streamlit pandas boto3 trino folium streamlit-folium
```

### 4. Streamlit 실행

#### 방법 1: 가상 환경 활성화 후 실행

가상 환경이 활성화된 상태에서:

```bash
streamlit run app.py
```

#### 방법 2: UV를 통한 직접 실행 (권장)

가상 환경을 활성화하지 않고도 `uv run`을 사용하여 실행할 수 있습니다:

```bash
uv run streamlit run app.py
```

이 방법은 uv가 자동으로 가상 환경을 관리하므로 더 편리합니다.

## UV 명령어 참고

### 의존성 추가

새로운 패키지를 추가하려면:

```bash
uv pip install <패키지명>
```

그리고 `pyproject.toml`의 `dependencies` 섹션에 수동으로 추가하거나:

```bash
uv add <패키지명>
```

### 의존성 동기화

`pyproject.toml`을 업데이트한 후:

```bash
uv pip sync pyproject.toml
```

### Lock 파일 생성

의존성 버전을 고정하려면:

```bash
uv lock
```

이 명령어는 `uv.lock` 파일을 생성합니다. 이 파일은 버전 관리에 포함하는 것을 권장합니다.

## 주의사항

- `.venv` 디렉토리는 `.gitignore`에 포함되어 있어 버전 관리되지 않습니다.
- `uv.lock` 파일은 버전 관리에 포함하는 것을 권장합니다 (재현 가능한 빌드를 위해).
- 현재 `.gitignore`에서 `uv.lock`이 주석 처리되어 있으므로, 필요시 주석을 해제하세요.

