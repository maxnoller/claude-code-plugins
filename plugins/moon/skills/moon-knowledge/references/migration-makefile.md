# Migration Guide: Makefile to Moon

## Overview

Convert Makefile targets to moon tasks for caching, parallel execution, and better developer experience.

## Basic Migration

### Before (Makefile)

```makefile
.PHONY: build clean test lint dev

build:
	npm run build

clean:
	rm -rf dist node_modules

test: build
	npm test

lint:
	eslint src

dev:
	npm run dev

all: lint test build
```

### After (moon.yml)

```yaml
tasks:
  build:
    command: 'npm run build'
    inputs:
      - 'src/**/*'
      - 'package.json'
    outputs:
      - 'dist'

  clean:
    command: 'rm -rf dist node_modules'
    options:
      cache: false

  test:
    command: 'npm test'
    deps:
      - '~:build'
    inputs:
      - 'src/**/*'
      - 'tests/**/*'

  lint:
    command: 'eslint src'
    inputs:
      - 'src/**/*'

  dev:
    command: 'npm run dev'
    preset: 'server'

  # "all" target becomes multiple runs:
  # moon run project:lint project:test project:build
```

## Pattern Rules

### Makefile

```makefile
%.o: %.c
	$(CC) -c $< -o $@
```

### Moon (for compiled languages)

```yaml
tasks:
  compile:
    command: 'gcc'
    args: ['-c', 'src/*.c', '-o', 'build/']
    inputs:
      - 'src/**/*.c'
      - 'src/**/*.h'
    outputs:
      - 'build/**/*.o'
```

## Variables

### Makefile

```makefile
CC = gcc
CFLAGS = -Wall -O2

build:
	$(CC) $(CFLAGS) -o app src/*.c
```

### Moon

```yaml
tasks:
  build:
    command: 'gcc'
    args: ['-Wall', '-O2', '-o', 'app', 'src/*.c']
    env:
      CC: 'gcc'
      CFLAGS: '-Wall -O2'
    # Or use shell expansion:
    # command: '${CC} ${CFLAGS} -o app src/*.c'
```

## Conditional Execution

### Makefile

```makefile
build:
ifeq ($(ENV),production)
	npm run build:prod
else
	npm run build:dev
endif
```

### Moon

```yaml
tasks:
  build:
    command: 'npm run build:${ENV:-dev}'
    env:
      ENV: '${ENV:-development}'

  # Or separate tasks
  build-prod:
    command: 'npm run build:prod'
    env:
      NODE_ENV: 'production'

  build-dev:
    command: 'npm run build:dev'
    env:
      NODE_ENV: 'development'
```

## Complex Dependencies

### Makefile

```makefile
app: lib1 lib2
	link lib1.o lib2.o -o app

lib1:
	compile lib1.c

lib2: lib1
	compile lib2.c
```

### Moon (multi-project)

```yaml
# projects/lib1/moon.yml
tasks:
  build:
    command: 'compile lib1.c'
    outputs: ['lib1.o']

# projects/lib2/moon.yml
dependsOn:
  - 'lib1'

tasks:
  build:
    command: 'compile lib2.c'
    deps:
      - 'lib1:build'
    outputs: ['lib2.o']

# projects/app/moon.yml
dependsOn:
  - 'lib1'
  - 'lib2'

tasks:
  build:
    command: 'link lib1.o lib2.o -o app'
    deps:
      - '^:build'
    outputs: ['app']
```

## Shell Commands

### Makefile

```makefile
deploy:
	@echo "Deploying..."
	scp -r dist/ server:/app/
	ssh server "systemctl restart app"
```

### Moon

```yaml
tasks:
  deploy:
    command: 'bash'
    args:
      - '-c'
      - |
        echo "Deploying..."
        scp -r dist/ server:/app/
        ssh server "systemctl restart app"
    deps:
      - '~:build'
    options:
      cache: false
```

## Keep Makefile as Wrapper

If your team is used to `make`, keep a thin Makefile:

```makefile
.PHONY: build test lint dev ci

build:
	moon run :build

test:
	moon run :test

lint:
	moon run :lint

dev:
	moon run :dev

ci:
	moon ci
```

## Tips

1. **Replace `.PHONY`** - All moon tasks are "phony" by default
2. **Add inputs/outputs** - Enables caching (Makefile only caches files)
3. **Use deps** - Better than Make's dependency syntax
4. **Parallel by default** - Moon runs independent tasks in parallel
5. **Cross-platform** - Moon works on Windows too
