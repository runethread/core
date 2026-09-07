package starter

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
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

	got := map[string]string{}
	if err := filepath.WalkDir(root, func(path string, entry os.DirEntry, walkErr error) error {
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
		data, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		sum := sha256.Sum256(data)
		got[rel] = hex.EncodeToString(sum[:])
		return nil
	}); err != nil {
		t.Fatalf("walk generated repository: %v", err)
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

func sortedMapKeys(values map[string]string) []string {
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}
