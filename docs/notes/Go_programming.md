---
id: go-programming
title: Go Programming
date: 2025-10-23
tags: [go, programming, wsl, development-setup]
---

# Go programming

## Prompt

What is the recommended way to install Go for development on WSL?

## Response

Thought for 1m 18s

Short answer: Install the official Linux Go toolchain inside WSL from go.dev, keep your code on the WSL filesystem,
and use a version manager (mise or asdf) only if you need per-project pinning.

# Recommended (WSL, Ubuntu 24.04)

* Use the **official tarball**. Avoid `apt` for Go because it lags behind upstream.
* Keep projects under `/home/<you>/...`, not `/mnt/c`, for I/O performance. [Go+2Go+2](https://go.dev/doc/install)

## Install Go 1.25.3 (current stable)

```bash
# deps for cgo and downloads
sudo apt-get update && sudo apt-get install -y build-essential curl ca-certificates

# pick arch
case "$(dpkg --print-architecture)" in
  amd64) GOARCH=amd64; SUM=0335f314b6e7bfe08c3d0cfaa7c19db961b7b99fb20be62b0a826c992ad14e0f;;
  arm64) GOARCH=arm64; SUM=1d42ebc84999b5e2069f5e31b67d6fc5d67308adad3e178d5a2ee2c9ff2001f5;;
  *) echo "unsupported arch"; exit 1;;
esac
VER=1.25.3
cd /tmp
curl -fsSLO "https://go.dev/dl/go${VER}.linux-${GOARCH}.tar.gz"
echo "${SUM}  go${VER}.linux-${GOARCH}.tar.gz" | sha256sum -c -

# install
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "go${VER}.linux-${GOARCH}.tar.gz"

# PATH and GOPATH
grep -q '/usr/local/go/bin' ~/.bashrc || {
  printf '\nexport PATH=/usr/local/go/bin:$HOME/go/bin:$PATH\n' >> ~/.bashrc
}
mkdir -p "$HOME/go"
exec $SHELL -l

# verify
go version
go env GOROOT GOPATH CGO_ENABLED
```

Notes:

* Checksums come from the official downloads page. Verify if you change version/arch. [Go](https://go.dev/dl/)
* `build-essential` provides `gcc` for cgo when needed. [Go](https://go.dev/wiki/cgo)
* Install on WSL’s Linux FS; don’t mix with Windows Go MSI. [Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/filesystems)

## Quick test

```bash
mkdir -p ~/src/hello && cd ~/src/hello
go mod init example.com/hello
cat > main.go <<'EOF'
package main
import "fmt"
func main(){ fmt.Println("ok") }
EOF
go run .
```

# If you need per-project versions

Use **mise** or **asdf**. Both keep the binary under WSL and auto-switch versions in each repo.

### Option A: mise

```bash
# install mise (see docs for the installer you prefer)
curl https://mise.jdx.dev/install.sh | sh
exec $SHELL -l
mise use -g go@1.25.3        # global
# or per project:
cd ~/src/hello
mise use go@1.25.3
```

* Supports `.go-version` and `.tool-versions` files. [mise.jdx.dev+1](https://mise.jdx.dev/getting-started.html)

### Option B: asdf

```bash
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc && exec $SHELL -l
asdf plugin add golang https://github.com/asdf-community/asdf-golang.git
asdf install golang 1.25.3
asdf global golang 1.25.3
```

* Plugin is maintained by asdf-community. You can pin per-repo with `.tool-versions`. [asdf-vm.com+1](https://asdf-vm.com/guide/getting-started.html)

# Why this setup

* **Upstream toolchain** gives latest fixes and performance. Install steps are the canonical method. [Go](https://go.dev/doc/install)
* **WSL FS** avoids slow cross-OS file I/O. [Microsoft Learn+1](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
* **Version manager** only when you need multiple Go versions or reproducible per-repo pins. [mise.jdx.dev+1](https://mise.jdx.dev/lang/go.html)

Sources: Go install docs; Go downloads (1.25.3 and checksums); Microsoft WSL filesystem guidance; mise docs; asdf + golang plugin; cgo requirements. [Go+5Go+5Go+5](https://go.dev/doc/install)

## Prompt

Is that better than installing Go via Snap on Ubuntu? Here is the context and output:

```bash
$ go --help
Command 'go' not found, but can be installed with:
sudo snap install go # version 1.25.3, or
sudo apt install golang-go # version 2:1.21~2
sudo apt install gccgo-go # version 2:1.21~2
See 'snap info go' for additional versions.
$ snap info go
name: go
summary: The Go programming language
publisher: Canonical✓
store-url: <https://snapcraft.io/go>
contact: <https://bugs.launchpad.net/go-snap/+filebug>
license: BSD-3-Clause
description: |
Go is an open source programming language that enables the production of simple, efficient and
reliable software at scale.
snap-id: Md1HBASHzP4i0bniScAjXGnOII9cEK6e
channels:
latest/stable: 1.25.3 2025-10-14 (10971) 55MB classic
latest/candidate: ↑
latest/beta: ↑
latest/edge: 1.25-ecc06f0 2025-04-09 (10896) 117MB classic
1.25/stable: 1.25.3 2025-10-14 (10971) 55MB classic
...
```

## Response

Thought for 42s

Yes. For WSL dev, prefer the upstream tarball (or a version manager). Snap is OK for a quick single global Go, but it’s less controllable.

## Why tarball > snap on WSL

* Exact version, no forced auto-updates; easy to switch/pin with mise/asdf. [Go](https://go.dev/doc/install)
* No dependence on `systemd` or snapd. Snap needs systemd enabled in WSL. [Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/systemd)
* Snap updates by default; you must explicitly schedule or hold them to avoid surprise version changes. [Snapcraft](https://snapcraft.io/docs/managing-updates)
* Snap can run multiple instances only via “parallel installs,” which is extra ceremony and not always smooth with classic snaps. [Snapcraft](https://snapcraft.io/docs/parallel-installs)

## If you still want snap

```bash
# 1) Ensure WSL has systemd
# /etc/wsl.conf
[boot]
systemd=true
# Then: wsl --shutdown  # from Windows PowerShell, restart Ubuntu
```

```bash
# 2) Install Go via snap (classic confinement, pinned track)
sudo snap install go --classic --channel=1.25/stable
```

```bash
# 3) Prevent surprise upgrades
sudo snap refresh --hold=60d go         # or set a refresh schedule
snap refresh --time
```

Notes: the `go` snap uses **classic** confinement. Auto-refresh can be held or scheduled, but it’s global snapd behavior. [Ubuntu Documentation+1](https://documentation.ubuntu.com/snapcraft/stable/explanation/classic-confinement/)

## Summary

* Use **tarball or mise/asdf** for reproducible, per-project Go on WSL. [Go](https://go.dev/doc/install)
* Use **snap** only if you want one global Go and accept snapd management. Pin the channel and hold/schedule updates. [Snapcraft+1](https://snapcraft.io/go)

## Prompt

Please reformat so that each command to be run individually is placed in its own Markdown code block. Here is the original snippet:

```markdown
# deps for cgo and downloads

sudo apt-get update && sudo apt-get install -y build-essential curl ca-certificates

# pick arch

case "$(dpkg --print-architecture)" in
amd64) GOARCH=amd64; SUM=0335f314b6e7bfe08c3d0cfaa7c19db961b7b99fb20be62b0a826c992ad14e0f;;
arm64) GOARCH=arm64; SUM=1d42ebc84999b5e2069f5e31b67d6fc5d67308adad3e178d5a2ee2c9ff2001f5;;
\*) echo "unsupported arch"; exit 1;;
esac
VER=1.25.3
cd /tmp
curl -fsSLO "https://go.dev/dl/go${VER}.linux-${GOARCH}.tar.gz"
echo "${SUM} go${VER}.linux-${GOARCH}.tar.gz" | sha256sum -c -

# install

sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "go${VER}.linux-${GOARCH}.tar.gz"

# PATH and GOPATH

grep -q '/usr/local/go/bin' ~/.bashrc || {
printf '\\nexport PATH=/usr/local/go/bin:$HOME/go/bin:$PATH\\n' >> ~/.bashrc
}
mkdir -p "$HOME/go"
exec $SHELL -l

# verify

go version
go env GOROOT GOPATH CGO_ENABLED
```

## Response

Thought for 21s

Reformatted. Run each block separately.

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y build-essential curl ca-certificates
```

```bash
case "$(dpkg --print-architecture)" in
  amd64) GOARCH=amd64; SUM=0335f314b6e7bfe08c3d0cfaa7c19db961b7b99fb20be62b0a826c992ad14e0f;;
  arm64) GOARCH=arm64; SUM=1d42ebc84999b5e2069f5e31b67d6fc5d67308adad3e178d5a2ee2c9ff2001f5;;
  *) echo "unsupported arch"; exit 1;;
esac
```

```bash
VER=1.25.3
```

```bash
cd /tmp
```

```bash
curl -fsSLO "https://go.dev/dl/go${VER}.linux-${GOARCH}.tar.gz"
```

```bash
echo "${SUM}  go${VER}.linux-${GOARCH}.tar.gz" | sha256sum -c -
```

```bash
sudo rm -rf /usr/local/go
```

```bash
sudo tar -C /usr/local -xzf "go${VER}.linux-${GOARCH}.tar.gz"
```

```bash
grep -q '/usr/local/go/bin' ~/.bashrc || {
  printf '\nexport PATH=/usr/local/go/bin:$HOME/go/bin:$PATH\n' >> ~/.bashrc
}
```

```bash
mkdir -p "$HOME/go"
```

```bash
exec $SHELL -l
```

```bash
go version
```

```bash
go env GOROOT GOPATH CGO_ENABLED
```

## Prompt

“go.mod file not found in current directory.” Can you explain?

## Response

Thought for 1m 38s

You launched the debugger in **~/go** (your GOPATH) where there is **no `go.mod`**. Delve runs `go build .`; with modules on, Go requires a `go.mod` in the current or parent dir, so the build fails.

## Fix

1. Run from a module directory, or create one.
2. Point VS Code’s debug `"program"` to the package dir that contains `main`.

### Minimal commands

```bash
# verify where you are and module state
pwd
go env GOPATH GO111MODULE
```

```bash
# go to your project (not $HOME/go) e.g.
cd ~/exercises
```

```bash
# create a module at the project root (once)
go mod init example.com/exercises
```

```bash
# put main files under a package dir, then test-run
cd src/start/01-essentials
go run .
```

### VS Code launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Go: Launch Package",
      "type": "go",
      "request": "launch",
      "mode": "auto",
      "program": "${fileDirname}"
    }
  ]
}
```

### Avoid

* Opening `$HOME/go` as the workspace. Use it only for tools (`bin/`, `pkg/`).
* GOPATH mode. If you must, set `GO111MODULE=off` and place code under `$GOPATH/src/...`, but this is legacy.

## Prompt

It is confusing because I selected Ctrl+F5 “Run Without Debugging.”

## Response

Thought for 1m 14s

Ctrl+F5 still uses the Go debug adapter (Delve) and your **launch configuration**.
It tried to build **~/go** (GOPATH tools dir) where there’s **no `go.mod`**, so it failed.
“Run Without Debugging” ≠ `go run .`; it’s a launch of the configured package without attaching breakpoints.

## Fix fast

1. Open the **module root** (the folder that has `go.mod`) as the VS Code workspace. Do not open `$HOME/go`.
2. Point the launch `"program"` at the package that contains `main`, or run from the terminal.

### Minimal terminal path

```bash
cd ~/exercises/src/start/01-essentials
go run .
```

### If no module yet

```bash
cd ~/exercises
go mod init example.com/exercises
```

### VS Code `.vscode/launch.json`

Use the current file’s folder so Ctrl+F5 builds the right package:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Go: Launch Package",
      "type": "go",
      "request": "launch",
      "mode": "auto",
      "program": "${fileDirname}"
    }
  ]
}
```

## Why you saw Delve

VS Code sends `noDebug: true` to the Go extension, but Delve still launches to run the program;
it still performs `go build .` in the directory resolved by `"program"`. No browsing used.

## Prompt

Is there a standard formatting style and tool for Go? A linter? Is there a standard tool for scaffolding a project (like Cookiecutter)? What about building and installing (like Make or Just)? I prefer official or standard tools if possible. The same question applies to tests (e.g., JUnit in Java).

Additionally, I am looking for a guide for a new Go programmer: what must I absolutely know? Please write a short article that includes the first book to read, advanced recommended books, must-know libraries (e.g., CLI apps, REST, databases, data processing like NumPy/Pandas), must-read blogs, and newsletters, podcasts, and YouTube channels—that is, the culture and ecosystem a Go programmer is expected to know.

## Response

Thought for 5m 49s

Yes. Use the built-ins:

* **Formatter:** `gofmt` (and `go fmt`), optionally `goimports` to fix imports too. [Go Packages+2Go.dev+2](https://pkg.go.dev/cmd/gofmt)
* **Linter:** `go vet` is official. Add **Staticcheck** or **golangci-lint** for broader checks. [Go Packages+2Staticcheck+2](https://pkg.go.dev/cmd/vet)
* **Project scaffolding:** none official. Start with `go mod init`; use `cobra-cli` only if you want CLI scaffolding. [Go.dev+1](https://go.dev/doc/code)
* **Build & install:** `go build`, `go install`, `go run`. For installing tools: `go install pkg@version`. [Reddit+1](https://www.reddit.com/r/devops/comments/1axj8t2/command_runners_make_vs_scripts_vs_just_vs/)
* **Testing:** stdlib `testing` + `go test`; fuzzing, coverage, race detector, benchmarks are built in. [Go.dev+2Go.dev+2](https://go.dev/doc/tutorial/add-a-test)

---

# Go, fast-start guide for experienced devs

1. Tooling you will actually use

---

```bash
# format
go fmt ./...
go install golang.org/x/tools/cmd/goimports@latest
goimports -w .

# vet + linters
go vet ./...
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
golangci-lint run

# build / run / install
go build ./cmd/myapp
go run ./cmd/myapp
go install ./cmd/myapp

# tests (unit, race, coverage, bench)
go test ./... -race -cover
go test -bench=. -benchmem ./...
```

Refs: formatting, vet, test, install. [Stack Overflow+3Go Packages+3Go Packages+3](https://pkg.go.dev/cmd/gofmt)

2. Minimal, idiomatic project layout

---

```
myapp/
  go.mod
  cmd/myapp/main.go
  internal/…        # not importable outside this module
  pkg/…             # optional; public libraries
```

Create with:

```bash
go mod init example.com/myorg/myapp
```

See “How to Write Go Code” and workspaces (`go work`) for multi-module repos. Internal packages are a language feature. [Go.dev+2Go.dev+2](https://go.dev/doc/code)

3. Must-know language and stdlib pieces

---

* **Concurrency:** goroutines, channels, `select`, `context.Context`; `errgroup` for structured concurrency. [Medium](https://medium.com/swlh/how-to-structure-a-go-command-line-project-788c318a1d8c)
* **HTTP:** `net/http` first; only add a router when you need it. Official Gin tutorial shows a full REST flow. Prefer `chi` or `gin` if you want a framework. [alexedwards.net+2Go.dev+2](https://www.alexedwards.net/blog/an-introduction-to-packages-imports-and-modules)
* **DB:** `database/sql` + a driver (Postgres: `pgx`). Consider `sqlc` for type-safe queries; ORMs like GORM/Ent are popular but optional. [GORM+3Go Packages+3Go Packages+3](https://pkg.go.dev/database/sql)
* **Profiles & races:** `net/http/pprof`, `go test -race`. [Go Packages+1](https://pkg.go.dev/net/http/pprof)

4. Libraries worth knowing (batteries after stdlib)

---

* **CLI:** `spf13/cobra`, `urfave/cli`. Generator: `cobra-cli`. [GitHub+2cli.urfave.org+2](https://github.com/spf13/cobra)
* **Routers/Web:** `go-chi/chi`, `gin-gonic/gin`. [go-chi.io+1](https://go-chi.io/)
* **SQL:** `jackc/pgx`, `sqlc`. ORMs: `GORM`, `Ent`. [Entgo+3Go Packages+3docs.sqlc.dev+3](https://pkg.go.dev/github.com/jackc/pgx)
* **Numerics/Data:** `gonum`, data frames with `go-gota/gota` (no pandas-equivalent in stdlib). [Go Packages+1](https://pkg.go.dev/gonum.org/v1/gonum)

5. Testing beyond basics

---

* Unit tests in `_test.go` with `testing`.
* Fuzz tests: `go test` supports fuzzing natively.
* Benchmarks: `BenchmarkXxx(b *testing.B)`.
* Coverage: `-cover` and HTML with `-coverprofile`. [Go.dev+1](https://go.dev/doc/tutorial/add-a-test)

6. Learning path

---

* **First read:** *Effective Go* + the official “How to Write Go Code.” [Go.dev+1](https://go.dev/doc/effective_go)
* **First book:** *The Go Programming Language* (Donovan & Kernighan). [Amazon](https://www.amazon.com/Programming-Language-Addison-Wesley-Professional-Computing/dp/0134190440)
* **Next books:** *Concurrency in Go* (Cox-Buday); *100 Go Mistakes and How to Avoid Them* (Harsanyi). [O'Reilly Media+1](https://www.oreilly.com/library/view/concurrency-in-go/9781491941294/)

7. Keep current

---

* **Official Go Blog** for features and release notes.
* **Golang Weekly** newsletter.
* **Go Time** podcast.
* **GopherCon** talks on YouTube. [YouTube+3Go.dev+3golangweekly.com+3](https://go.dev/blog/)

8. What is “standard” vs “community”

---

* **Standard:** `go fmt/gofmt`, `go vet`, `go build/install/test`, `testing`, modules/workspaces, `pprof`, race detector. [Go.dev+6Go.dev+6Go Packages+6](https://go.dev/doc/cmd)
* **Community defaults:** `goimports`, Staticcheck, golangci-lint, `cobra`/`chi`/`gin`, `pgx`/`sqlc`, `gonum`. Use as needed; none are mandated. [Go Packages+7Go Packages+7Staticcheck+7](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)

If you want, I’ll generate a skeleton repo with `go.mod`, `cmd/`, `internal/`, a Makefile wrapper, and CI steps for `fmt`, `vet`, `staticcheck`, `golangci-lint`, and `go test -race`.

## Prompt

Is Make the typical orchestrator for large Go projects? What do Kubernetes and Helm use? Yes—please generate the skeleton repo you mentioned.

## Response

Thought for 1m 52s

Use the Go toolchain for build/test. For orchestration, **Makefiles are the common standard** in large Go repos. **Kubernetes** builds with `make` (Bazel was removed in 2021). **Helm**’s dev guide uses `make test`. [Google Groups+2Go Packages+2](https://groups.google.com/g/kubernetes-dev/c/tRqW6b7gPMA)

Below is a minimal, idiomatic **skeleton repo** with Make-based tasks and CI.

0. Create project

---

```bash
mkdir -p myapp && cd myapp
go mod init example.com/you/myapp
go mod edit -go=1.25
```

1. Source layout

---

```bash
mkdir -p cmd/myapp internal/hello .github/workflows
```

```bash
cat > cmd/myapp/main.go <<'EOF'
package main

import (
 "fmt"

 "example.com/you/myapp/internal/hello"
)

func main() {
 fmt.Println(hello.Msg())
}
EOF
```

```bash
cat > internal/hello/hello.go <<'EOF'
package hello

func Msg() string { return "ok" }
EOF
```

```bash
cat > internal/hello/hello_test.go <<'EOF'
package hello

import "testing"

func TestMsg(t *testing.T) {
 if got := Msg(); got != "ok" {
  t.Fatalf("want ok, got %q", got)
 }
}
EOF
```

2. Makefile (fmt, vet, lint, test, build, run)

---

```bash
cat > Makefile <<'EOF'
SHELL := /usr/bin/env bash
BIN   := myapp
PKG   := ./cmd/$(BIN)

.PHONY: help tools fmt vet lint test race cover build run tidy ci

help:
 @printf "targets: tools fmt vet lint test race cover build run tidy ci\n"

tools: ## install dev tools
 go install golang.org/x/tools/cmd/goimports@latest
 go install honnef.co/go/tools/cmd/staticcheck@latest
 go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

fmt:
 go fmt ./...
 goimports -w .

vet:
 go vet ./...

lint:
 golangci-lint run

test:
 go test ./...

race:
 go test -race ./...

cover:
 go test -coverprofile=coverage.out ./...
 go tool cover -func=coverage.out

build:
 go build -o bin/$(BIN) $(PKG)

run:
 go run $(PKG)

tidy:
 go mod tidy

ci: fmt vet lint test
EOF
```

3. Optional linter config

---

```bash
cat > .golangci.yml <<'EOF'
run:
  timeout: 3m
linters:
  enable:
    - govet
    - staticcheck
    - gosimple
    - ineffassign
    - errcheck
    - gofmt
EOF
```

4. GitHub Actions CI

---

```bash
cat > .github/workflows/ci.yml <<'EOF'
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.25.x'
      - run: go version
      - run: make tools
      - run: make ci
EOF
```

5. Ignore build artifacts

---

```bash
cat > .gitignore <<'EOF'
bin/
coverage.out
EOF
```

6. Try it

---

```bash
make tools
make run
make test
make build
```

## What’s “official/standard”

* **Format:** `gofmt` / `go fmt`. [Go Packages+1](https://pkg.go.dev/cmd/gofmt)
* **Linter:** `go vet` in std; add Staticcheck or golangci-lint. [Go Packages](https://pkg.go.dev/cmd/vet)
* **Tests:** `testing` + `go test` (unit, fuzz, bench, coverage). [Go Packages+1](https://pkg.go.dev/testing)
* **Build/Install:** `go build`, `go install`, `go run`. (No external build tool required.)
* **Orchestration:** no official tool, but **Makefiles** are the norm in big Go projects; **Kubernetes uses make**; **Helm uses make** in its dev flow. [Google Groups+1](https://groups.google.com/g/kubernetes-dev/c/tRqW6b7gPMA)

If you prefer releases, wire in **GoReleaser** later; it integrates cleanly with Make. [goreleaser.com+1](https://goreleaser.com/cmd/goreleaser_build/)

## Prompt

What does `go install` do?

## Response

Thought for 22s

It compiles a **main package** and puts the executable in **$GOBIN** (or `$(go env GOPATH)/bin` if GOBIN is empty). Non-main packages are just built and cached.

## Key points

* **Local binary install**

  ```bash
  go install ./cmd/myapp      # writes $GOBIN/myapp
  ```

* **Tool install (module-aware, preferred)**

  ```bash
  go install golang.org/x/tools/cmd/goimports@latest
  go install honnef.co/go/tools/cmd/staticcheck@2024.1.1
  ```

  The `@version` form resolves modules and installs without touching your `go.mod`.

* **Where it goes**

  * If `GOBIN` is set: `$GOBIN/`.

  * Else: `$(go env GOPATH)/bin/`.
    Add to PATH:

    ```bash
    export PATH="$(go env GOBIN 2>/dev/null || echo $(go env GOPATH)/bin):$PATH"
    ```

* **What it does not do**

  * It does **not** “install libraries” into your project. With modules, compiled archives go to the build/module cache.
  * `go get` no longer installs binaries; use `go install pkg@version` instead.

## Quick checks

```bash
go env GOBIN GOPATH
which myapp
```

## Prompt

But what does `go install` with no arguments do? `[build flags] [packages]` are optional. By default now, what does `go install` do without a module init? Here is `go help install`:

```
go help install
usage: go install [build flags] [packages]

Install compiles and installs the packages named by the import paths.

Executables are installed in the directory named by the GOBIN environment
variable, which defaults to $GOPATH/bin or $HOME/go/bin if the GOPATH
environment variable is not set. Executables in $GOROOT
are installed in $GOROOT/bin or $GOTOOLDIR instead of $GOBIN.

If the arguments have version suffixes (like @latest or @v1.0.0), "go install"
builds packages in module-aware mode, ignoring the go.mod file in the current
directory or any parent directory, if there is one. This is useful for
installing executables without affecting the dependencies of the main module.
To eliminate ambiguity about which module versions are used in the build, the
arguments must satisfy the following constraints:

- Arguments must be package paths or package patterns (with "..." wildcards).
  They must not be standard packages (like fmt), meta-patterns (std, cmd,
  all), or relative or absolute file paths.

- All arguments must have the same version suffix. Different queries are not
  allowed, even if they refer to the same version.

- All arguments must refer to packages in the same module at the same version.

- Package path arguments must refer to main packages. Pattern arguments
  will only match main packages.

- No module is considered the "main" module. If the module containing
  packages named on the command line has a go.mod file, it must not contain
  directives (replace and exclude) that would cause it to be interpreted
  differently than if it were the main module. The module must not require
  a higher version of itself.

- Vendor directories are not used in any module. (Vendor directories are not
  included in the module zip files downloaded by 'go install'.)

If the arguments don't have version suffixes, "go install" may run in
module-aware mode or GOPATH mode, depending on the GO111MODULE environment
variable and the presence of a go.mod file. See 'go help modules' for details.
If module-aware mode is enabled, "go install" runs in the context of the main
module.

When module-aware mode is disabled, non-main packages are installed in the
directory $GOPATH/pkg/$GOOS\_$GOARCH. When module-aware mode is enabled,
non-main packages are built and cached but not installed.

Before Go 1.20, the standard library was installed to
$GOROOT/pkg/$GOOS\_$GOARCH.
Starting in Go 1.20, the standard library is built and cached but not installed.
Setting GODEBUG=installgoroot=all restores the use of
$GOROOT/pkg/$GOOS\_$GOARCH.

For more about build flags, see 'go help build'.

For more about specifying packages, see 'go help packages'.

## See also: go build, go get, go clean
```

## Response

Thought for 49s

Default: `go install` with no args targets **the package in the current directory**. Outcome depends on context.

## What happens

| Where you run it                                                     | Package kind | Result                                                         |
| -------------------------------------------------------------------- | ------------ | -------------------------------------------------------------- |
| **Inside a module** (`go.mod` found)                                 | `main`       | Builds and writes the binary to **$GOBIN** (or `$GOPATH/bin`). |
| Inside a module                                                      | non-`main`   | Builds and caches only. Nothing installed.                     |
| **Outside any module** and **under `$GOPATH/src/...`** (GOPATH mode) | `main`       | Installs the binary to **$GOBIN**.                             |
| Outside any module and under `$GOPATH/src/...`                       | non-`main`   | Installs archives to `$GOPATH/pkg/$GOOS_$GOARCH`.              |
| **Outside any module** and **not** under `$GOPATH/src/...`           | any          | Fails with “cannot find main module; see ‘go help modules’”.   |

## Special case

* `go install path@version` works **anywhere**. It ignores local `go.mod` and installs the tool’s binary to **$GOBIN**.

## Quick checks

```bash
go env GOMOD GO111MODULE GOPATH GOBIN   # module on/off and install dirs
```

```bash
go list -f '{{.Name}}' .                # shows 'main' or a library package
```

No browsing used.

## Prompt

Is there any interpreter for Go, similar to IPython?

## Response

Thought for 1m 4s

No official interpreter. Go is compiled. Use third-party REPLs or notebooks if you want IPython-style interactivity.

## Options

* **Yaegi**: mature Go interpreter and REPL. Good for scripting and embedding.
  Install: `go install github.com/traefik/yaegi/cmd/yaegi@latest` → run `yaegi`. [GitHub+1](https://github.com/traefik/yaegi)

* **gomacro**: feature-rich interpreter with generics and macros; fast REPL.
  Install: `go install github.com/cosmos72/gomacro@latest` → run `gomacro`. [GitHub+1](https://github.com/cosmos72/gomacro)

* **gore**: lightweight REPL; author now recommends gomacro/yaegi for speed.
  Install: `go install github.com/x-motemen/gore/cmd/gore@latest`. [GitHub](https://github.com/x-motemen/gore)

* **Jupyter**: use **gophernotes** kernel (runs Go interactively; uses gomacro under the hood).
  Quick install (Linux):

  ```
  go install github.com/gopherdata/gophernotes@v0.7.5
  mkdir -p ~/.local/share/jupyter/kernels/gophernotes
  cd ~/.local/share/jupyter/kernels/gophernotes
  cp "$(go env GOPATH)"/pkg/mod/github.com/gopherdata/gophernotes@v0.7.5/kernel/* .
  sed "s|gophernotes|$(go env GOPATH)/bin/gophernotes|" < kernel.json.in > kernel.json
  ```

  Then start Jupyter and pick “Go”. [GitHub](https://github.com/gopherdata/gophernotes)

## Caveats

* **No official REPL** in the Go toolchain; `go run` compiles then runs. [Go+1](https://go.dev/doc/faq)
* Interpreters have **incomplete coverage** and edge-case gaps; expect occasional incompatibilities with complex packages. Prefer compiled `go run`/`go test` for production behavior. [GitHub](https://github.com/traefik/yaegi/discussions/1548)

If you want, I can add a `repl/` target to your Makefile that installs `yaegi` and drops you into a Go REPL.

## Prompt

Gophernotes uses Gomacro, but the last tagged release of Gomacro was in 2018. Should I be concerned?

## Response

Thought for 1m 6s

Accurate but incomplete: **gomacro’s last *tagged release* is 2018**, yet the project is still active and updated for Go 1.18+; pkg docs show 2025 updates. **gophernotes** depends on gomacro and last released in 2022. For something maintained, prefer **Yaegi** (REPL) or **GoNB** (Jupyter, compile-per-cell).

## What to use

* **Terminal REPL:** Yaegi. Mature, active.

  ```bash
  go install github.com/traefik/yaegi/cmd/yaegi@latest
  yaegi
  ```

  Source: project README and package docs. [GitHub+1](https://github.com/traefik/yaegi)

* **Jupyter notebooks:** GoNB. Modern kernel that compiles each cell, so full Go compatibility, CGO works; actively released.

  ```bash
  go install github.com/janpfeifer/gonb@latest
  gonb --install
  ```

  Notes: Windows via WSL or Docker. [GitHub](https://github.com/janpfeifer/gonb)

* **Legacy notebook path:** gophernotes (uses gomacro). Works but slower cadence; plugin limits on Windows.

  ```bash
  go install github.com/gopherdata/gophernotes@v0.7.5
  ```

  [GitHub](https://github.com/gopherdata/gophernotes)

## On your “2018” observation

* gomacro **tags** stop at v2.7 (2018), but the repo and modules are active and docs show 2025 timestamps; README requires Go 1.18+. Use `@latest` to pull current head. [GitHub+2Go Packages+2](https://github.com/cosmos72/gomacro/tags)

Summary: pick **Yaegi** for a maintained REPL; pick **GoNB** for maintained notebooks; use **gophernotes+gomacro** only if you need its interpreter-specific features.

## Prompt

I only use JupyterLab. What is the best option?

## Response

Thought for 51s

Best: **GoNB** kernel. It compiles each cell with the standard Go toolchain, works in JupyterLab, and is supported on WSL. [GitHub](https://github.com/janpfeifer/gonb)

## Install on WSL (Ubuntu)

```bash
# prerequisite: Go installed and on PATH
go version
```

```bash
# install kernel + helpers
go install github.com/janpfeifer/gonb@latest
go install golang.org/x/tools/cmd/goimports@latest
go install golang.org/x/tools/gopls@latest
```

```bash
# register the kernel with Jupyter
gonb --install
```

```bash
# verify and launch
jupyter kernelspec list | grep -i gonb
jupyter lab
```

GoNB’s README documents `gonb --install`, JupyterLab support, and WSL usage. [GitHub](https://github.com/janpfeifer/gonb)

## Quick alternative (no local setup)

```bash
docker pull janpfeifer/gonb_jupyterlab:latest
docker run -it --rm -p 8888:8888 -v "$PWD":/notebooks janpfeifer/gonb_jupyterlab:latest
```

This image bundles JupyterLab + GoNB. [GitHub](https://github.com/janpfeifer/gonb)

## Why not gophernotes?

It’s interpreter-based via **gomacro** and has slower releases; works, but not my first choice for JupyterLab today on WSL. Install steps show the gomacro dependency and manual kernelspec copy. [GitHub](https://github.com/gopherdata/gophernotes)

## Notes

JupyterLab runs any registered kernel; GoNB is a kernel that follows the Jupyter protocol. [docs.jupyter.org](https://docs.jupyter.org/en/stable/projects/kernels.html)

## Prompt

Is Go object-oriented?

## Response

Thought for 17s

Yes, but not class-based. Go is **object-oriented via types + methods + interfaces**, not via classes or inheritance.

## Core facts

* **Types with methods:** any named type can have methods (value or pointer receiver).
* **Encapsulation:** package-level; identifiers starting with a capital letter are exported.
* **Polymorphism:** **interfaces** with **structural typing** (no `implements` clause); satisfied implicitly.
* **Composition:** **embedding** promotes fields/methods; no subclassing or overriding.
* **No features:** no classes, inheritance, method/operator overloading, or required constructors (use `NewT` functions).

## Minimal example

```go
package main

import "fmt"

type Shaper interface{ Area() float64 }        // interface (structural)
type Rect struct{ W, H float64 }               // concrete type

func (r Rect) Area() float64 { return r.W * r.H } // method

// Embedding = composition, not inheritance
type LabeledRect struct {
    Rect
    Label string
}

func main() {
    var s Shaper = Rect{W: 3, H: 2} // implicit interface satisfaction
    fmt.Println(s.Area())           // 6

    lr := LabeledRect{Rect{3, 2}, "A"}
    fmt.Println(lr.Area(), lr.Label) // promoted method, field access
}
```

## Method-set notes (succinct)

* Method on **value receiver** is callable on both values and pointers.
* Method on **pointer receiver** requires a pointer (except when addressable; compiler auto-takes address).
* Interfaces hold a pair *(concrete value, method set)*; use **type assertions** or **type switches** when needed.

**Summary:** Go supports OO through **interfaces and composition**, favoring decoupling over inheritance.

## Prompt

Is this similar to Rust? Please compare and contrast. What are the different types of “typing”?

## Response

Thought for 29s

Short answer: Similar goals. Different mechanics.
Go = structural interfaces + GC + CSP.
Rust = nominal traits + ownership + zero-cost generics.

## Go vs Rust — OO and typing

* **Abstraction unit**

  * Go: interfaces are **structural**; any type that has the methods “implements” automatically.
  * Rust: traits are **nominal**; a type implements a trait only if there is an explicit `impl`.
* **Dispatch**

  * Go: dynamic via `interface` values (runtime itab). No static specialization from interfaces.
  * Rust: **static by default** with monomorphization of generics; **dynamic** via `dyn Trait` trait objects.
* **Composition vs inheritance**

  * Go: no inheritance; **embedding** promotes methods/fields.
  * Rust: no inheritance; compose data with `struct`, behavior with multiple trait impls and blanket impls.
* **Encapsulation**

  * Go: package-scoped; export by Capitalization.
  * Rust: module-scoped `pub` with fine-grained visibility (`pub(crate)`, `pub(super)`).
* **Generics**

  * Go: since 1.18; constraints are interfaces; no specialization; type inference is local.
  * Rust: mature generics; rich trait bounds (HRTBs, associated types), specialization mostly unstable.
* **Memory model**

  * Go: garbage collected; simple ownership; potential pause/latency trade-offs.
  * Rust: **affine** ownership + borrow checker; no GC; stricter APIs but predictable performance.
* **Errors**

  * Go: `error` values + `if err != nil`; panic for exceptional.
  * Rust: `Result<T,E>` + `?`; `panic!` for exceptional; exhaustive handling enforced by types.
* **Concurrency**

  * Go: goroutines + channels + `select`; CSP style, runtime scheduler, data race detector.
  * Rust: threads + channels; async/await with executors (Tokio, async-std); `Send`/`Sync` traits enforce safety.
* **Tooling**

  * Go: `go build/install/test`, `gofmt`, `go vet`.
  * Rust: Cargo for everything, `rustfmt`, `clippy`, `cargo test/bench`.

## Typing taxonomy (concise)

* **Static vs dynamic**: checked at compile time (Rust, Go) vs runtime (Python).
* **Strong vs weak**: coercions disallowed vs silently allowed. Go and Rust are **strong**.
* **Nominal vs structural**: names decide compatibility (Rust traits, most OO) vs shape decides (Go interfaces, TypeScript structural types).
* **Duck typing**: dynamic structural typing (“if it quacks”).
* **Gradual typing**: optional static types atop dynamic core (Python+typing, TypeScript).
* **Parametric polymorphism**: generics (`Vec<T>`, `[]T`).
* **Ad-hoc polymorphism**: overloaded behavior by type classes/traits (Rust traits), interfaces (Go).
* **Subtyping**: subtype values usable where supertypes expected (classic OO). Go lacks nominal subtyping; Rust uses trait bounds, not class subtyping.
* **Linear/affine types**: values used at most once; basis for Rust ownership (affine).
* **Type inference**: compiler deduces types. Rust: strong local inference with annotated item boundaries; Go: limited local inference (`:=`).
* **Lifetimes/regions**: static reasoning about reference validity (Rust only).
* **Nullability**: Rust encodes with `Option<T>`; Go has `nil` for pointers/maps/slices/channels/interfaces; no non-null types in the language.

## When to pick which

* **Go**: fast build times, simple concurrency, small teams, services where GC is acceptable and ergonomics matter.
* **Rust**: performance, tight latency, embedded, FFI-heavy, or correctness where ownership checks save you from whole classes of bugs.

If you want, I can add parallel examples of the same small service in both languages showing interfaces vs traits, static vs dynamic dispatch, and error handling.

## Prompt

Can you explain GC and CSP as used by Go?

## Response

Thought for 52s

GC = Go’s garbage collector. CSP = Communicating Sequential Processes.

## GC (Go)

* Purpose: reclaim heap memory automatically.
* Design: concurrent, tri-color mark-and-sweep with write barriers and pacing; mostly non-moving; low-pause by running alongside mutators. Tuning via `GOGC`, profiles via `pprof`. [tip.golang.org](https://tip.golang.org/doc/gc-guide)

## CSP (in Go)

* Idea: structure concurrency as independent processes that communicate over channels, not shared mutable state. Go adopts this via **goroutines + channels + `select`**. It’s CSP-inspired, not a formal CSP implementation. [Go.dev+1](https://go.dev/blog/codelab-share)
* Memory model: channel send/receive and other sync ops establish **happens-before** edges between goroutines. [Go.dev](https://go.dev/ref/mem)

### Minimal CSP-style snippet

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

work := make(chan int)
go func() {                   // producer
 for i := 0; i < 3; i++ { work <- i }
 close(work)
}()

sum := make(chan int)
go func() {                   // consumer
 s := 0
 for v := range work { s += v }
 sum <- s
}()

select {                      // coordination
case v := <-sum:
 fmt.Println(v)            // 3
case <-ctx.Done():
}
```

### Primary sources

* Go GC guide. [tip.golang.org](https://tip.golang.org/doc/gc-guide)
* “Share Memory by Communicating” + codewalk. [Go.dev+1](https://go.dev/blog/codelab-share)
* Go Memory Model. [Go.dev](https://go.dev/ref/mem)
* Hoare, *Communicating Sequential Processes*. [ACM Digital Library](https://dl.acm.org/doi/10.1145/359576.359585)

## Prompt

Can you include Python, Java, and JavaScript in the Go vs. Rust comparison regarding typing and object orientation? I would like a table to show the differences and similarities at a glance.

## Response

Thought for 48s

Yes. Here’s a compact matrix comparing **Go, Rust, Python, Java, JavaScript** on typing and OO.

| Language       | When types checked    | Strength                            | Nominal vs structural                                            | OO model                                   | Inheritance                                       | Polymorphism                                                    | Generics                                   | Memory mgmt                 | Nullability                        | Error handling                          | Gradual typing                     |
| -------------- | --------------------- | ----------------------------------- | ---------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------ | --------------------------- | ---------------------------------- | --------------------------------------- | ---------------------------------- |
| **Go**         | Static (compile-time) | Strong                              | **Structural** interfaces; concrete types are nominal            | Types + methods; composition via embedding | None (composition only)                           | Interfaces (dynamic via `interface{}`); parametric via generics | Yes (1.18+, parametric; no specialization) | GC (concurrent, non-moving) | `nil` for ptr/map/slice/chan/iface | `error` values; `panic` for exceptional | No                                 |
| **Rust**       | Static                | Strong                              | **Nominal** traits and types                                     | Traits + structs; composition              | None (no class inheritance)                       | Static via traits (monomorphization); dynamic via `dyn Trait`   | Yes (monomorphized, powerful bounds)       | Ownership/borrowing, no GC  | `Option<T>` (no null refs)         | `Result<T,E>`; `panic!` exceptional     | No                                 |
| **Python**     | Dynamic (runtime)     | Strong                              | Nominal classes at runtime; **structural** via `typing.Protocol` | Class-based; multiple inheritance          | Yes (multiple)                                    | Duck typing; runtime dynamic dispatch                           | Yes (static-only hints; runtime erased)    | Refcount + cycle GC         | `None` (Optional in hints)         | Exceptions                              | **Yes** (optional hints since 3.5) |
| **Java**       | Static                | Strong                              | **Nominal** classes/interfaces                                   | Class-based                                | Single inheritance + multiple interfaces          | Subtyping + dynamic dispatch; interfaces                        | Yes (erased, invariant by default)         | GC (moving, generational)   | `null`; `Optional<T>` idiom        | Checked + unchecked exceptions          | No                                 |
| **JavaScript** | Dynamic               | **Weak/loose** (implicit coercions) | Structural/duck by convention                                    | Prototype-based; `class` is sugar          | Prototype chains (no classical class inheritance) | Duck typing; dynamic dispatch                                   | No (use TypeScript for static generics)    | GC                          | `null` and `undefined`             | Exceptions                              | N/A (TypeScript adds it)           |

### Quick notes

* **Static vs dynamic**: Rust/Go/Java compile-time; Python/JS runtime.
* **Strong vs weak**: Rust/Go/Java/Python disallow silent coercions; JS allows many (`'2' * 3 → 6`).
* **Nominal vs structural**: Rust/Java need explicit `impl`/`implements`; Go interfaces match by method **shape**; Python gains structural typing in static analysis via `Protocol`.
* **OO style**: Go and Rust avoid class inheritance; prefer interfaces/traits + composition.
* **Generics**: Rust is monomorphized (zero-cost). Java erases. Go is parametric without specialization. Python’s `typing` is for static analyzers only.
* **Memory**: Rust = ownership, no GC. Others use GC.
* **Nullability**: Rust types encode absence with `Option<T>`; others have null-ish values.
* **Errors**: Rust models errors in types; Go uses `error` returns; Java uses exceptions; Python/JS use exceptions.

### Typing taxonomy (minimal)

* **Static/Dynamic**: when checks occur.
* **Strong/Weak**: whether the language implicitly coerces across types.
* **Nominal/Structural**: name-based compatibility vs shape-based.
* **Duck typing**: dynamic structural typing.
* **Gradual typing**: optional static types on a dynamic core.
* **Parametric polymorphism**: generics.
* **Ad-hoc polymorphism**: traits/interfaces/type classes.
* **Subtyping**: substitutability within a type hierarchy.

No browsing used.

## Prompt

Is there a standard project skeleton generator for Go (like Copier/Cookiecutter or cargo-generate)?

## Response

Thought for 12s

No official generator. The Go “standard” is: `go mod init`, add `cmd/` and `internal/`, then build with `go build` and test with `go test`. Generators exist, but none are canonical.

## Practical options

* **Cobra (CLI apps)**: scaffolds a Cobra-based CLI.

  ```bash
  go install github.com/spf13/cobra-cli@latest
  cobra-cli init myapp
  cd myapp
  cobra-cli add serve
  ```

* **Buffalo (web)**: full-stack web scaffolder.

  ```bash
  go install github.com/gobuffalo/cli/cmd/buffalo@latest
  buffalo new myapp && cd myapp
  ```

* **Kratos (microservices)**:

  ```bash
  go install github.com/go-kratos/kratos/cmd/kratos/v2@latest
  kratos new myapp && cd myapp
  ```

* **Goa (design-first codegen)**:

  ```bash
  go install goa.design/goa/v3/cmd/goa@latest
  # write design/*.go, then:
  goa gen <module>
  ```

* **Generic template tools** (not Go-specific): **cookiecutter**, **copier**, **boilr**.

## Useful add-ons

* **gotests** (generate table-driven tests from code):

  ```bash
  go install github.com/cweill/gotests/gotests@latest
  gotests ./... -all -w
  ```

* **goreleaser** (release config scaffold):

  ```bash
  go install github.com/goreleaser/goreleaser/v2@latest
  goreleaser init
  ```

## Recommendation

Use the minimal layout you already have (`go.mod`, `cmd/`, `internal/`, Makefile). Add **cobra-cli** only for CLIs. Pick **Buffalo/Kratos/Goa** only if you adopt those frameworks.

## Prompt

Should we convert our started project to a Copier or Cookiecutter template so it can be reused, or are there better templates already available?

## Response

Thought for 45s

Short answer: Yes. Make a thin **Copier** template for your house style. There’s no official Go generator; community templates exist but aren’t canonical. Keep it minimal and updateable.

# When to template

* You want repeatable: `go mod init`, layout, Make targets, CI, lint config.
* You expect many near-identical services/CLIs.
* You want `copier update` to roll fixes into children.

# When not to

* One-off app or heavy framework choice (then use that tool’s generator: `cobra-cli`, `kratos`, `buffalo`).

---

## Minimal Copier template (drop-in)

```
go-template/
├─ copier.yml
├─ .gitignore.jinja
├─ README.md.jinja
├─ go.mod.jinja
├─ cmd/{{ bin_name }}/main.go.jinja
├─ internal/hello/hello.go
├─ internal/hello/hello_test.go
├─ Makefile
├─ .golangci.yml
└─ .github/workflows/ci.yml.jinja
```

**copier.yml**

```yaml
_min_copier_version: "7.0.0"

project_name:
  type: str
  default: "myapp"

module_path:
  type: str
  help: "Go module path (e.g., github.com/acme/{{ project_name }})"
  default: "example.com/you/{{ project_name }}"

go_version:
  type: str
  default: "1.25"

bin_name:
  type: str
  default: "{{ project_name }}"

use_github_actions:
  type: bool
  default: true

license:
  type: str
  choices: ["MIT", "Apache-2.0", "None"]
  default: "MIT"
```

**go.mod.jinja**

```go
module {{ module_path }}

go {{ go_version }}
```

**cmd/{{ bin_name }}/main.go.jinja**

```go
package main

import (
 "fmt"

 "{{ module_path }}/internal/hello"
)

func main() { fmt.Println(hello.Msg()) }
```

**internal/hello/hello.go**

```go
package hello

func Msg() string { return "ok" }
```

**internal/hello/hello_test.go**

```go
package hello

import "testing"

func TestMsg(t *testing.T) {
 if got := Msg(); got != "ok" { t.Fatalf("want ok, got %q", got) }
}
```

**Makefile**

```make
SHELL := /usr/bin/env bash
BIN   := {{ bin_name }}
PKG   := ./cmd/$(BIN)

.PHONY: tools fmt vet lint test race cover build run tidy ci

tools:
 go install golang.org/x/tools/cmd/goimports@latest
 go install honnef.co/go/tools/cmd/staticcheck@latest
 go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

fmt:   ; go fmt ./... && goimports -w .
vet:   ; go vet ./...
lint:  ; golangci-lint run
test:  ; go test ./...
race:  ; go test -race ./...
cover: ; go test -coverprofile=coverage.out ./... && go tool cover -func=coverage.out
build: ; go build -o bin/$(BIN) $(PKG)
run:   ; go run $(PKG)
tidy:  ; go mod tidy
ci:    ; $(MAKE) fmt vet lint test
```

**.golangci.yml**

```yaml
run:
  timeout: 3m
linters:
  enable: [govet, staticcheck, gosimple, ineffassign, errcheck, gofmt]
```

**.github/workflows/ci.yml.jinja**

```yaml
{% if use_github_actions %}
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '{{ go_version }}.x' }
      - run: make tools
      - run: make ci
{% endif %}
```

**.gitignore.jinja**

```
bin/
coverage.out
```

**README.md.jinja**

````markdown
# {{ project_name }}

- Module: `{{ module_path }}`
- Go: `{{ go_version }}`

## Quick start
```bash
make tools
make run
make test
````

````

---

## Use it

```bash
# install copier
pipx install copier  # or: pip install --user copier
````

```bash
# generate a new project
copier copy /path/to/go-template my-new-app
cd my-new-app
make run
```

```bash
# later, propagate template updates
copier update
```

---

## Existing templates

* Many exist, none official. Most are opinionated or framework-bound.
* Use **Cobra’s** `cobra-cli` if you want a CLI skeleton.
* Use **Kratos** or **Buffalo** only if you’re adopting those stacks.

**Recommendation:** keep your template **thin** (layout, lint, CI, Make). Add extras only when multiple repos need them.

---
