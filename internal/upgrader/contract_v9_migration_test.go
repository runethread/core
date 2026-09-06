package upgrader

import (
	"bytes"
	"encoding/json"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"testing"

	runethread "github.com/runethread/core"
	"github.com/runethread/core/internal/buildinfo"
	"github.com/runethread/core/internal/indexer"
	"github.com/runethread/core/internal/starter"
	"github.com/runethread/core/internal/trust"
)

func TestContractV8FixtureMatchesTrustedV080Anchor(t *testing.T) {
	root := contractV8Fixture(t)
	state, err := inspectSource(root)
	if err != nil {
		t.Fatal(err)
	}
	if state.Kind != sourceNative || state.Version != nativeV080ReleaseVersion || state.ContractVersion != 8 {
		t.Fatalf("unexpected v0.8 fixture source state: %#v", state)
	}

	lockData := mustRead(t, filepath.Join(root, ".runethread", "lock.json"))
	var lock trust.Lock
	if err := json.Unmarshal(lockData, &lock); err != nil {
		t.Fatal(err)
	}
	if lock.ContractSHA256 != nativeContractV8SHA256 || !equalStringMap(lock.FilesSHA256, nativeContractV8Files) {
		t.Fatalf("v0.8 fixture lock does not match trusted source anchor: %#v", lock)
	}
}

func TestApplyMigratesExactContractV8SourceAndPreservesUserBytes(t *testing.T) {
	root := contractV8Fixture(t)
	memoryJSON, memoryMD := writeFixtureMemory(t, root, false)
	projectCurrent := filepath.Join(root, "projects", "test", "current-state.md")
	const currentState = "# Test — Current State\n\nLast reviewed: 2026-08-01\n\nPreserve these exact user bytes even though the view may be stale.\n"
	mustWrite(t, projectCurrent, []byte(currentState))
	if err := indexer.Write(root); err != nil {
		t.Fatal(err)
	}

	beforeJSON := mustRead(t, memoryJSON)
	beforeMD := mustRead(t, memoryMD)
	beforeCurrent := mustRead(t, projectCurrent)

	result, err := Apply(root)
	if err != nil {
		t.Fatal(err)
	}
	if result.FromVersion != nativeV080ReleaseVersion || result.ToVersion != buildinfo.ContractReleaseVersion || result.FromContract != 8 || result.ToContract != 9 {
		t.Fatalf("unexpected v8 -> v9 migration result: %#v", result)
	}
	wantChanged := ".github/workflows/validate.yml,.runethread/config.json,.runethread/lock.json,MEMORY_PROTOCOL.md,README.md"
	if got := strings.Join(result.ChangedPaths, ","); got != wantChanged {
		t.Fatalf("v8 -> v9 changed paths = %s, want %s", got, wantChanged)
	}
	if got := mustRead(t, memoryJSON); !bytes.Equal(got, beforeJSON) {
		t.Fatal("canonical memory JSON changed during v8 -> v9 migration")
	}
	if got := mustRead(t, memoryMD); !bytes.Equal(got, beforeMD) {
		t.Fatal("canonical memory Markdown changed during v8 -> v9 migration")
	}
	if got := mustRead(t, projectCurrent); !bytes.Equal(got, beforeCurrent) {
		t.Fatal("project current-state user bytes changed during v8 -> v9 migration")
	}
	if problems := trust.Check(root); len(problems) != 0 {
		t.Fatalf("target trust check failed: %+v", problems)
	}
	if stale, err := indexer.Check(root); err != nil || len(stale) != 0 {
		t.Fatalf("target index is not fresh: stale=%v err=%v", stale, err)
	}

	workflow := string(mustRead(t, filepath.Join(root, ".github", "workflows", "validate.yml")))
	if strings.Contains(workflow, "\n  push:") || !strings.Contains(workflow, "\n  pull_request:") || !strings.Contains(workflow, "\n  workflow_dispatch:") {
		t.Fatalf("unexpected v9 managed workflow triggers:\n%s", workflow)
	}
	if strings.Contains(workflow, "actions/checkout@v7") || strings.Contains(workflow, "actions/setup-go@v7") || !strings.Contains(workflow, "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1") || !strings.Contains(workflow, "actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e") {
		t.Fatalf("v9 managed workflow does not use the expected immutable Action pins:\n%s", workflow)
	}
	readme := string(mustRead(t, filepath.Join(root, "README.md")))
	if strings.Contains(readme, "canonical project state views") || !strings.Contains(readme, "non-authoritative project orientation/materialized views") {
		t.Fatalf("v9 managed README does not describe project views correctly:\n%s", readme)
	}
}

func TestApplyPreservesCustomizedV8Readme(t *testing.T) {
	root := contractV8Fixture(t)
	const custom = "# Runethread Memory\n\nCustom owner notes referencing .runethread/lock.json must survive.\n"
	path := filepath.Join(root, "README.md")
	mustWrite(t, path, []byte(custom))

	result, err := Apply(root)
	if err != nil {
		t.Fatal(err)
	}
	if got := string(mustRead(t, path)); got != custom {
		t.Fatalf("custom README was overwritten: %q", got)
	}
	if strings.Contains(strings.Join(result.ChangedPaths, ","), "README.md") {
		t.Fatalf("custom README unexpectedly reported as changed: %#v", result)
	}
}

func TestApplyRefusesCustomizedV8ManagedWorkflow(t *testing.T) {
	root := contractV8Fixture(t)
	path := filepath.Join(root, ".github", "workflows", "validate.yml")
	const custom = "name: User workflow\non: workflow_dispatch\njobs: {}\n"
	mustWrite(t, path, []byte(custom))
	configBefore := mustRead(t, filepath.Join(root, ".runethread", "config.json"))

	if _, err := Apply(root); err == nil || !strings.Contains(err.Error(), "refusing to overwrite") {
		t.Fatalf("expected customized v8 workflow refusal, got %v", err)
	}
	if got := mustRead(t, filepath.Join(root, ".runethread", "config.json")); !bytes.Equal(got, configBefore) {
		t.Fatal("v8 config changed despite workflow preflight refusal")
	}
	if got := string(mustRead(t, path)); got != custom {
		t.Fatal("custom workflow changed despite preflight refusal")
	}
}

func TestApplyRefusesTamperedContractV8SourceBeforeWriting(t *testing.T) {
	root := contractV8Fixture(t)
	path := filepath.Join(root, "MEMORY_PROTOCOL.md")
	mustWrite(t, path, append(mustRead(t, path), []byte("\ntampered\n")...))
	configBefore := mustRead(t, filepath.Join(root, ".runethread", "config.json"))

	if _, err := Apply(root); err == nil || !strings.Contains(err.Error(), "digest") {
		t.Fatalf("expected trusted v8 source digest refusal, got %v", err)
	}
	if got := mustRead(t, filepath.Join(root, ".runethread", "config.json")); !bytes.Equal(got, configBefore) {
		t.Fatal("v8 config changed despite source digest refusal")
	}
}

func contractV8Fixture(t *testing.T) string {
	t.Helper()
	root := filepath.Join(t.TempDir(), "memory")
	fixtureRoot := filepath.Join("testdata", "runethread-v0.8.0")
	if err := filepath.WalkDir(fixtureRoot, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		rel, err := filepath.Rel(fixtureRoot, path)
		if err != nil {
			return err
		}
		if rel == "." {
			return nil
		}
		target := filepath.Join(root, rel)
		if entry.IsDir() {
			return os.MkdirAll(target, 0o755)
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		return os.WriteFile(target, data, 0o644)
	}); err != nil {
		t.Fatal(err)
	}

	lockData := mustRead(t, filepath.Join(root, ".runethread", "lock.json"))
	var lock trust.Lock
	if err := json.Unmarshal(lockData, &lock); err != nil {
		t.Fatal(err)
	}
	for rel, expectedHash := range lock.FilesSHA256 {
		fixturePath := filepath.Join("testdata", "runethread-contract-v8", filepath.FromSlash(rel))
		data, err := os.ReadFile(fixturePath)
		if os.IsNotExist(err) {
			data, err = fs.ReadFile(runethread.ContractFS, rel)
		}
		if err != nil {
			t.Fatalf("materialize historical v8 %s: %v", rel, err)
		}
		if got := sha256Hex(data); got != expectedHash {
			t.Fatalf("historical v8 fixture for %s has digest %s, want %s; freeze the exact released bytes instead of using the current contract", rel, got, expectedHash)
		}
		mustWrite(t, filepath.Join(root, filepath.FromSlash(rel)), data)
	}
	if err := os.MkdirAll(filepath.Join(root, "memories"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, "projects"), 0o755); err != nil {
		t.Fatal(err)
	}
	return root
}

func equalStringMap(left, right map[string]string) bool {
	if len(left) != len(right) {
		return false
	}
	for key, value := range left {
		if right[key] != value {
			return false
		}
	}
	return true
}

func TestV9StarterManagedSupportSemantics(t *testing.T) {
	readme := string(starter.MemoryRepoReadme())
	if strings.Contains(readme, "canonical project state views") || !strings.Contains(readme, "non-authoritative project orientation/materialized views") {
		t.Fatalf("starter README has stale project-view authority wording:\n%s", readme)
	}
	workflow := string(starter.ValidationWorkflow())
	if strings.Contains(workflow, "\n  push:") || !strings.Contains(workflow, "\n  pull_request:") || !strings.Contains(workflow, "\n  workflow_dispatch:") {
		t.Fatalf("starter workflow has unexpected triggers:\n%s", workflow)
	}
	for _, line := range strings.Split(workflow, "\n") {
		trimmed := strings.TrimSpace(line)
		if !strings.HasPrefix(trimmed, "uses:") {
			continue
		}
		ref := strings.TrimSpace(strings.TrimPrefix(trimmed, "uses:"))
		if comment := strings.Index(ref, " #"); comment >= 0 {
			ref = ref[:comment]
		}
		at := strings.LastIndex(ref, "@")
		if at < 0 || len(ref[at+1:]) != 40 {
			t.Fatalf("managed workflow action is not pinned to a full SHA: %q", line)
		}
	}
}
