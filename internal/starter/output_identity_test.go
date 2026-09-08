package starter

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"

	runethread "github.com/runethread/core"
)

type outputBoundaryManifest struct {
	MITGeneratedOutputSHA256        map[string]string `json:"mit_generated_output_sha256"`
	GeneratedEmptyPlaceholderSHA256 map[string]string `json:"generated_empty_placeholders_sha256"`
}

func TestInitialRepositoryOutputIdentity(t *testing.T) {
	manifestBytes, err := os.ReadFile(filepath.Join("..", "..", "LICENSING_BOUNDARY.json"))
	if err != nil {
		t.Fatalf("read output boundary manifest: %v", err)
	}
	var manifest outputBoundaryManifest
	if err := json.Unmarshal(manifestBytes, &manifest); err != nil {
		t.Fatalf("parse output boundary manifest: %v", err)
	}

	expected := make(map[string]string, len(manifest.MITGeneratedOutputSHA256)+len(manifest.GeneratedEmptyPlaceholderSHA256))
	for rel, digest := range manifest.MITGeneratedOutputSHA256 {
		expected[rel] = digest
	}
	for rel, digest := range manifest.GeneratedEmptyPlaceholderSHA256 {
		if _, exists := expected[rel]; exists {
			t.Fatalf("duplicate generated path in boundary manifest: %s", rel)
		}
		expected[rel] = digest
	}

	contractPaths := make(map[string]struct{}, len(runethread.ContractPaths()))
	for _, rel := range runethread.ContractPaths() {
		contractPaths[rel] = struct{}{}
	}

	root := filepath.Join(t.TempDir(), "memory-repo")
	if err := Init(root); err != nil {
		t.Fatalf("init repository: %v", err)
	}

	got, err := collectGeneratedOutputIdentity(root, contractPaths)
	if err != nil {
		t.Fatalf("collect generated repository identity: %v", err)
	}

	if len(got) != len(expected) {
		t.Fatalf("generated non-contract path count = %d, want %d; got=%v want=%v", len(got), len(expected), sortedMapKeys(got), sortedMapKeys(expected))
	}
	for rel, wantDigest := range expected {
		gotDigest, ok := got[rel]
		if !ok {
			t.Errorf("missing generated path %s", rel)
			continue
		}
		if gotDigest != wantDigest {
			t.Errorf("generated path %s sha256 = %s, want %s", rel, gotDigest, wantDigest)
		}
	}
	for rel := range got {
		if _, ok := expected[rel]; !ok {
			t.Errorf("unexpected generated non-contract path %s", rel)
		}
	}
}

func TestGeneratedOutputIdentityRejectsSymlink(t *testing.T) {
	root := t.TempDir()
	target := filepath.Join(root, "target.txt")
	if err := os.WriteFile(target, []byte("target bytes\n"), 0o644); err != nil {
		t.Fatalf("write symlink target: %v", err)
	}
	link := filepath.Join(root, "link.txt")
	if err := os.Symlink("target.txt", link); err != nil {
		t.Skipf("symlink creation unavailable on this platform/runner: %v", err)
	}

	_, err := collectGeneratedOutputIdentity(root, map[string]struct{}{})
	if err == nil {
		t.Fatal("generated-output identity accepted a symlink")
	}
	if !strings.Contains(err.Error(), "not a regular file") {
		t.Fatalf("generated-output identity rejected symlink with unexpected error: %v", err)
	}
}

func collectGeneratedOutputIdentity(root string, contractPaths map[string]struct{}) (map[string]string, error) {
	got := map[string]string{}
	err := filepath.WalkDir(root, func(path string, entry os.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		rel = filepath.ToSlash(rel)
		if _, isContract := contractPaths[rel]; isContract {
			return nil
		}
		if entry.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("generated non-contract path %s is not a regular file", rel)
		}
		info, err := entry.Info()
		if err != nil {
			return fmt.Errorf("inspect generated non-contract path %s: %w", rel, err)
		}
		if !info.Mode().IsRegular() {
			return fmt.Errorf("generated non-contract path %s is not a regular file", rel)
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		sum := sha256.Sum256(data)
		got[rel] = hex.EncodeToString(sum[:])
		return nil
	})
	if err != nil {
		return nil, err
	}
	return got, nil
}

func sortedMapKeys(values map[string]string) []string {
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}
