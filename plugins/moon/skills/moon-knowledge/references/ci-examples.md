# CI/CD Configuration Examples

## GitHub Actions

### Basic CI

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for affected detection

      - uses: moonrepo/setup-toolchain@v0
        with:
          auto-install: true

      - run: moon ci
```

### Parallel Jobs with Matrix

```yaml
name: CI
on: [push, pull_request]

jobs:
  ci:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        index: [0, 1, 2, 3]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: moonrepo/setup-toolchain@v0

      - run: moon ci --job ${{ matrix.index }} --jobTotal 4
```

### Split by Task Type

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: moonrepo/setup-toolchain@v0
      - run: moon ci :build

  lint-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: moonrepo/setup-toolchain@v0
      - run: moon ci :lint :format

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: moonrepo/setup-toolchain@v0
      - run: moon ci :test
```

### With Run Report

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: moonrepo/setup-toolchain@v0

      - run: moon ci

      - uses: moonrepo/run-report-action@v1
        if: success() || failure()
        with:
          access-token: ${{ secrets.GITHUB_TOKEN }}
```

### With Remote Cache

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: moonrepo/setup-toolchain@v0

      - run: moon ci
        env:
          MOON_REMOTE_CACHE_TOKEN: ${{ secrets.MOON_CACHE_TOKEN }}
```

## GitLab CI

### Basic CI

```yaml
# .gitlab-ci.yml
stages:
  - ci

variables:
  GIT_DEPTH: 0  # Required for affected detection

moon:
  stage: ci
  image: node:20
  before_script:
    - curl -fsSL https://moonrepo.dev/install/moon.sh | bash
    - export PATH="$HOME/.moon/bin:$PATH"
  script:
    - moon ci
```

### Parallel Jobs

```yaml
stages:
  - ci

.moon-base:
  image: node:20
  variables:
    GIT_DEPTH: 0
  before_script:
    - curl -fsSL https://moonrepo.dev/install/moon.sh | bash
    - export PATH="$HOME/.moon/bin:$PATH"

moon-0:
  extends: .moon-base
  stage: ci
  script:
    - moon ci --job 0 --jobTotal 4

moon-1:
  extends: .moon-base
  stage: ci
  script:
    - moon ci --job 1 --jobTotal 4

moon-2:
  extends: .moon-base
  stage: ci
  script:
    - moon ci --job 2 --jobTotal 4

moon-3:
  extends: .moon-base
  stage: ci
  script:
    - moon ci --job 3 --jobTotal 4
```

### Split by Task Type

```yaml
stages:
  - build
  - test

.moon-base:
  image: node:20
  variables:
    GIT_DEPTH: 0
  before_script:
    - curl -fsSL https://moonrepo.dev/install/moon.sh | bash
    - export PATH="$HOME/.moon/bin:$PATH"

build:
  extends: .moon-base
  stage: build
  script:
    - moon ci :build

lint:
  extends: .moon-base
  stage: test
  script:
    - moon ci :lint :format

test:
  extends: .moon-base
  stage: test
  script:
    - moon ci :test
```

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  ci:
    docker:
      - image: cimg/node:20.0
    steps:
      - checkout
      - run:
          name: Install moon
          command: curl -fsSL https://moonrepo.dev/install/moon.sh | bash
      - run:
          name: Run CI
          command: ~/.moon/bin/moon ci

workflows:
  main:
    jobs:
      - ci
```

## Tips

### Exclude Tasks from CI

```yaml
# moon.yml
tasks:
  dev:
    command: 'vite dev'
    options:
      runInCI: false
    # Or use preset
    preset: 'server'
```

### Always Run in CI

```yaml
tasks:
  deploy:
    command: './deploy.sh'
    options:
      runInCI: 'always'  # Run even if not affected
```

### Skip but Allow Dependencies

```yaml
tasks:
  optional-check:
    command: 'check.sh'
    options:
      runInCI: 'skip'  # Skip but allow other tasks to depend on it
```
