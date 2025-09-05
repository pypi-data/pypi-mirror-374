# Core System gRPC Package

이 패키지는 Saladlab Core System의 gRPC 프로토 파일로 생성된 서버와 스텁을 관리합니다.

## 🚀 빠른 시작

```bash
# 의존성 설치 (grpcio-tools 포함)
make install-deps

# 기존 파일 정리 (중요!)
make clean

# 릴리즈 빌드 (proto 컴파일 + import 수정 + 패키지 빌드)
make build-release

# 로컬 테스트
make test-local
```

## 📋 사전 요구사항

- Python 3.11+
- uv (Python 패키지 매니저)
- Protocol Buffer 컴파일러 (grpcio-tools)

## 🛠️ 개발 환경 설정

### 1. 의존성 설치
```bash
make install-deps
```

이 명령어는 다음을 설치합니다:
- `grpcio-tools`: Protocol Buffer 컴파일러
- `hatch`: Python 패키지 빌드 도구
- 기타 개발 의존성

### 2. 로컬 개발
```bash
# proto 파일 수정 후
make compile-proto    # proto → Python 컴파일
make fix-imports      # import 경로 수정
make build-package    # 패키지 빌드
```

## 📦 빌드 시스템

### 주요 Makefile 타겟

| 타겟 | 설명 |
|------|------|
| `help` | 사용 가능한 모든 타겟 표시 |
| `install-deps` | 의존성 설치 (grpcio-tools 포함) |
| `compile-proto` | proto 파일을 Python으로 컴파일 |
| `fix-imports` | 생성된 파일의 import 경로 수정 |
| `build-release` | **전체 릴리즈 빌드** (권장) |
| `build-package` | hatch로 패키지 빌드 |
| `publish-pypi` | PyPI에 배포 |
| `test-local` | 로컬에서 패키지 테스트 |
| `clean` | 빌드 아티팩트 정리 |

### 빌드 프로세스

```bash
# 1. 의존성 설치
make install-deps

# 2. 릴리즈 빌드 (권장)
make build-release
```

`build-release`는 다음을 순차적으로 실행합니다:
1. `clean` - 기존 빌드 아티팩트 정리
2. `compile-proto` - proto 파일 컴파일
3. `fix-imports` - import 경로 수정
4. `build-package` - 최종 패키지 빌드

## 🧪 로컬 테스트

### 패키지 설치 및 테스트
```bash
# 개발 모드로 패키지 설치
make test-local

# 수동으로 테스트
python -c "import core_system_grpc; print('Import successful!')"
```

### 개별 단계별 테스트
```bash
# proto 컴파일만 테스트
make compile-proto

# import 경로 수정만 테스트
make fix-imports

# 패키지 빌드만 테스트
make build-package
```

## 🚀 배포

### 로컬에서 배포 준비
```bash
# 1. 기존 컴파일된 파일 정리 (중요!)
make clean

# 2. proto 파일 수정 후 전체 빌드
make build-release

# 3. 커밋 및 푸시
git add .
git commit -m "feat: commit message"
git push origin main

# 4. 버전 태그 생성 및 푸시
git tag v1.0.0
git push origin v1.0.0
```

> **🧹 중요**: `make clean`은 기존에 컴파일된 Python 파일들을 모두 삭제합니다.
> 이는 이전 빌드의 잔여 파일로 인한 import 충돌을 방지하기 위해 필요합니다.

### CI/CD 배포
GitHub Actions가 자동으로 다음을 수행합니다:
1. **Makefile 검증**: Makefile 존재 확인
2. **패키지 구조 검증**: `src/core_system_grpc` 디렉토리 및 컴파일된 Python 파일 존재 확인
3. **Import 테스트**: 패키지 import 가능성 검증
4. **패키지 빌드**: `make build-package`로 최종 패키지 빌드
5. **PyPI 배포**: 검증된 패키지를 PyPI에 업로드

> **⚠️ 중요**: CI/CD에서는 proto 컴파일을 수행하지 않습니다. 
> 반드시 로컬에서 `make build-release`를 실행한 후 커밋해야 합니다.

## 🔧 문제 해결

### Import 오류가 발생하는 경우
```bash
# import 경로 재수정
make fix-imports

# 전체 재빌드
make build-release
```

### proto 파일 수정 후
```bash
# proto 파일이 수정된 경우 반드시 실행
make build-release
```

### 빌드 실패 시
```bash
# 완전 정리 후 재시도
make clean
make build-release
```

### 기존 파일로 인한 import 충돌 시
```bash
# 기존 컴파일된 파일들을 완전히 정리
make clean

# src/core_system_grpc 디렉토리 확인
ls -la src/core_system_grpc/

# 필요시 수동으로 Python 파일들 삭제
rm -rf src/core_system_grpc/messages/*.py
rm -rf src/core_system_grpc/services/*.py

# 전체 재빌드
make build-release
```

## 📁 프로젝트 구조

```
core-system-grpc/
├── proto/                    # Protocol Buffer 정의 파일
│   ├── messages/            # 메시지 정의
│   └── services/            # 서비스 정의
├── src/core_system_grpc/    # 생성된 Python 코드
├── Makefile                 # 빌드 시스템
├── pyproject.toml          # 프로젝트 설정
└── README.md               # 이 파일
```

## 📝 버전 관리

이 패키지는 시멘틱 버저닝을 따릅니다:
- **Major**: Breaking changes
- **Minor**: 새로운 서비스/메시지 추가
- **Patch**: 버그 수정, 문서 업데이트

## 🔒 라이선스

Closed Source - 사내 전용 서비스입니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 Core System Team에 문의하세요.
