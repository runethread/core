package runethread

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"reflect"
	"regexp"
	"sort"
	"strings"
	"testing"
)

const invariantRegistryPath = "RUNETHREAD_INVARIANTS.json"

var (
	invariantIDPattern           = regexp.MustCompile(`^RT-([A-Z]+)-([0-9]{3})$`)
	classificationPrefixPattern = regexp.MustCompile(`^[A-Z]+$`)
)

var allowedInvariantScopes = map[string]struct{}{
	"agents":          {},
	"contributors":    {},
	"core":            {},
	"hosted":          {},
	"integrations":    {},
	"memory-template": {},
	"project":         {},
}

var foundationInvariantEntries = map[string]invariantEntry{
	"RT-ARCH-001": {
		ID:             "RT-ARCH-001",
		Status:         "active",
		Classification: "ARCH",
		Statement:      "Core remains provider-neutral; provider-specific hosted and integration dependencies, credentials, and execution authority live outside Core.",
		Scope:          []string{"project", "core", "hosted", "integrations"},
		Enforcement: invariantEnforcement{
			Mode:       "review",
			Mechanisms: []string{"dependency-boundary review", "exact-head architecture review"},
		},
		Evidence: []string{"ADR-005", "ADR-014", "ROADMAP"},
	},
	"RT-ARCH-002": {
		ID:             "RT-ARCH-002",
		Status:         "active",
		Classification: "ARCH",
		Statement:      "Correctness-relevant behavior crosses component boundaries through explicit versioned contracts or immutable identities, not through unversioned internal implementation coupling.",
		Scope:          []string{"project", "core", "hosted", "integrations"},
		Enforcement: invariantEnforcement{
			Mode:       "mixed",
			Mechanisms: []string{"runtime/contract identity tests", "release compatibility review", "exact-head architecture review"},
		},
		Evidence: []string{"ADR-005", "ADR-011", "ROADMAP"},
	},
	"RT-DATA-001": {
		ID:             "RT-DATA-001",
		Status:         "active",
		Classification: "DATA",
		Statement:      "The user-owned memory Git repository is canonical durable semantic memory state; derived indexes, caches, summaries, and project-orientation views are non-authoritative derived state.",
		Scope:          []string{"project", "core", "hosted", "memory-template"},
		Enforcement: invariantEnforcement{
			Mode:       "mixed",
			Mechanisms: []string{"repository validation tests", "migration preservation tests", "architecture review"},
		},
		Evidence: []string{"ADR-001", "ADR-015", "memory-template README"},
	},
	"RT-GOV-001": {
		ID:             "RT-GOV-001",
		Status:         "active",
		Classification: "GOV",
		Statement:      "Material recommendations and changes are optimized for the actual project objective rather than agreement-seeking or novelty, using evidence, costs, simpler alternatives, and accepted constraints; when unresolved material ambiguity could change the decision, clarification is sought rather than silently assumed.",
		Scope:          []string{"project", "contributors", "agents"},
		Enforcement: invariantEnforcement{
			Mode:       "mixed",
			Mechanisms: []string{"AGENTS decision discipline", "pull-request invariant impact", "exact-head review"},
		},
		Evidence: []string{"ADR-027", "AGENTS.md", "pull request template"},
	},
	"RT-REL-001": {
		ID:             "RT-REL-001",
		Status:         "active",
		Classification: "REL",
		Statement:      "Released or hosted execution is bound to explicit immutable verified identities for every correctness-relevant component, contract, and protocol it relies on, and does not execute floating development branches as production authority.",
		Scope:          []string{"project", "core", "hosted", "integrations"},
		Enforcement: invariantEnforcement{
			Mode:       "mixed",
			Mechanisms: []string{"runtime/contract release separation tests", "release gates", "hosted release-identity review"},
		},
		Evidence: []string{"ADR-011", "ADR-014", "ROADMAP"},
	},
	"RT-SEM-001": {
		ID:             "RT-SEM-001",
		Status:         "active",
		Classification: "SEM",
		Statement:      "Canonical memory mutation semantics have one implementation authority in Core; other components may invoke or independently replay those Core-owned semantics but must not create a second semantic implementation.",
		Scope:          []string{"project", "core", "hosted", "integrations"},
		Enforcement: invariantEnforcement{
			Mode:       "mixed",
			Mechanisms: []string{"MemoryService tests", "independent Core replay design", "exact-head architecture review"},
		},
		Evidence: []string{"ADR-002", "ADR-020", "ADR-021"},
	},
}

type invariantRegistry struct {
	FormatVersion   int                `json:"format_version"`
	Authority       invariantAuthority `json:"authority"`
	Classifications map[string]string  `json:"classifications"`
	Invariants      []invariantEntry   `json:"invariants"`
}

type invariantAuthority struct {
	Repository string `json:"repository"`
	Path       string `json:"path"`
}

type invariantEntry struct {
	ID             string               `json:"id"`
	Status         string               `json:"status"`
	Classification string               `json:"classification"`
	Statement      string               `json:"statement"`
	Scope          []string             `json:"scope"`
	Enforcement    invariantEnforcement `json:"enforcement"`
	Evidence       []string             `json:"evidence"`
}

type invariantEnforcement struct {
	Mode       string   `json:"mode"`
	Mechanisms []string `json:"mechanisms"`
}

func loadInvariantRegistry(data []byte) (invariantRegistry, error) {
	var registry invariantRegistry
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&registry); err != nil {
		return invariantRegistry{}, fmt.Errorf("decode invariant registry: %w", err)
	}
	var trailing any
	if err := decoder.Decode(&trailing); !errors.Is(err, io.EOF) {
		if err == nil {
			return invariantRegistry{}, errors.New("decode invariant registry: trailing JSON values")
		}
		return invariantRegistry{}, fmt.Errorf("decode invariant registry trailing data: %w", err)
	}
	return registry, nil
}

func validateInvariantRegistry(registry invariantRegistry) error {
	if registry.FormatVersion != 1 {
		return fmt.Errorf("format_version = %d, want 1", registry.FormatVersion)
	}
	if registry.Authority.Repository != "runethread/core" || registry.Authority.Path != invariantRegistryPath {
		return fmt.Errorf("authority = %q:%q, want runethread/core:%s", registry.Authority.Repository, registry.Authority.Path, invariantRegistryPath)
	}
	if len(registry.Classifications) == 0 {
		return errors.New("classifications must not be empty")
	}
	for prefix, description := range registry.Classifications {
		if !classificationPrefixPattern.MatchString(prefix) {
			return fmt.Errorf("classification prefix %q is invalid", prefix)
		}
		if strings.TrimSpace(description) == "" {
			return fmt.Errorf("classification %s has an empty description", prefix)
		}
	}
	if len(registry.Invariants) == 0 {
		return errors.New("invariants must not be empty")
	}

	seen := make(map[string]invariantEntry, len(registry.Invariants))
	ids := make([]string, 0, len(registry.Invariants))
	for _, invariant := range registry.Invariants {
		match := invariantIDPattern.FindStringSubmatch(invariant.ID)
		if match == nil {
			return fmt.Errorf("invariant id %q is invalid", invariant.ID)
		}
		if _, exists := seen[invariant.ID]; exists {
			return fmt.Errorf("duplicate invariant id %s", invariant.ID)
		}
		seen[invariant.ID] = invariant
		ids = append(ids, invariant.ID)

		if invariant.Status != "active" {
			return fmt.Errorf("%s status %q is unsupported in registry v1", invariant.ID, invariant.Status)
		}
		if invariant.Classification != match[1] {
			return fmt.Errorf("%s classification %q does not match id prefix %q", invariant.ID, invariant.Classification, match[1])
		}
		if _, ok := registry.Classifications[invariant.Classification]; !ok {
			return fmt.Errorf("%s uses undeclared classification %s", invariant.ID, invariant.Classification)
		}
		if strings.TrimSpace(invariant.Statement) == "" {
			return fmt.Errorf("%s statement is empty", invariant.ID)
		}
		if len(invariant.Scope) == 0 || hasBlankOrDuplicate(invariant.Scope) {
			return fmt.Errorf("%s scope must be non-empty and duplicate-free", invariant.ID)
		}
		for _, scope := range invariant.Scope {
			if _, ok := allowedInvariantScopes[scope]; !ok {
				return fmt.Errorf("%s uses undeclared scope %q", invariant.ID, scope)
			}
		}
		if invariant.Enforcement.Mode != "machine" && invariant.Enforcement.Mode != "mixed" && invariant.Enforcement.Mode != "review" {
			return fmt.Errorf("%s enforcement mode %q is invalid", invariant.ID, invariant.Enforcement.Mode)
		}
		if len(invariant.Enforcement.Mechanisms) == 0 || hasBlankOrDuplicate(invariant.Enforcement.Mechanisms) {
			return fmt.Errorf("%s enforcement mechanisms must be non-empty and duplicate-free", invariant.ID)
		}
		if len(invariant.Evidence) == 0 || hasBlankOrDuplicate(invariant.Evidence) {
			return fmt.Errorf("%s evidence must be non-empty and duplicate-free", invariant.ID)
		}
	}

	sorted := append([]string(nil), ids...)
	sort.Strings(sorted)
	for i := range ids {
		if ids[i] != sorted[i] {
			return fmt.Errorf("invariants must be sorted by id: got %v", ids)
		}
	}

	for id, expected := range foundationInvariantEntries {
		entry, ok := seen[id]
		if !ok {
			return fmt.Errorf("foundation invariant %s is missing", id)
		}
		if !reflect.DeepEqual(entry, expected) {
			return fmt.Errorf("foundation invariant %s policy drift", id)
		}
	}
	return nil
}

func hasBlankOrDuplicate(values []string) bool {
	seen := make(map[string]struct{}, len(values))
	for _, value := range values {
		if strings.TrimSpace(value) == "" {
			return true
		}
		if _, ok := seen[value]; ok {
			return true
		}
		seen[value] = struct{}{}
	}
	return false
}

func currentInvariantRegistry(t *testing.T) invariantRegistry {
	t.Helper()
	data, err := os.ReadFile(invariantRegistryPath)
	if err != nil {
		t.Fatalf("read %s: %v", invariantRegistryPath, err)
	}
	registry, err := loadInvariantRegistry(data)
	if err != nil {
		t.Fatal(err)
	}
	return registry
}

func invariantByID(t *testing.T, registry *invariantRegistry, id string) *invariantEntry {
	t.Helper()
	for i := range registry.Invariants {
		if registry.Invariants[i].ID == id {
			return &registry.Invariants[i]
		}
	}
	t.Fatalf("%s missing from test fixture", id)
	return nil
}

func TestInvariantRegistryPolicy(t *testing.T) {
	registry := currentInvariantRegistry(t)
	if err := validateInvariantRegistry(registry); err != nil {
		t.Fatal(err)
	}
}

func TestInvariantRegistryRejectsUnknownField(t *testing.T) {
	data, err := os.ReadFile(invariantRegistryPath)
	if err != nil {
		t.Fatal(err)
	}
	mutated := bytes.Replace(data, []byte(`"format_version": 1,`), []byte(`"format_version": 1, "unexpected": true,`), 1)
	if bytes.Equal(mutated, data) {
		t.Fatal("failed to create unknown-field test fixture")
	}
	if _, err := loadInvariantRegistry(mutated); err == nil || !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("expected unknown-field failure, got %v", err)
	}
}

func TestInvariantRegistryRejectsTrailingJSON(t *testing.T) {
	data, err := os.ReadFile(invariantRegistryPath)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := loadInvariantRegistry(append(data, []byte("\n{}\n")...)); err == nil || !strings.Contains(err.Error(), "trailing JSON values") {
		t.Fatalf("expected trailing-JSON failure, got %v", err)
	}
}

func TestInvariantRegistryRejectsFoundationPolicyDrift(t *testing.T) {
	tests := []struct {
		name   string
		mutate func(*invariantEntry)
	}{
		{
			name: "statement",
			mutate: func(entry *invariantEntry) {
				entry.Statement = "Hosted may implement equivalent semantics independently."
			},
		},
		{
			name: "scope",
			mutate: func(entry *invariantEntry) {
				entry.Scope = []string{"core"}
			},
		},
		{
			name: "enforcement",
			mutate: func(entry *invariantEntry) {
				entry.Enforcement.Mode = "review"
			},
		},
		{
			name: "evidence",
			mutate: func(entry *invariantEntry) {
				entry.Evidence = []string{"ADR-002"}
			},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			registry := currentInvariantRegistry(t)
			entry := invariantByID(t, &registry, "RT-SEM-001")
			test.mutate(entry)
			if err := validateInvariantRegistry(registry); err == nil || !strings.Contains(err.Error(), "policy drift") {
				t.Fatalf("expected foundation policy drift failure, got %v", err)
			}
		})
	}
}

func TestInvariantRegistryRejectsUndeclaredScope(t *testing.T) {
	registry := currentInvariantRegistry(t)
	entry := invariantByID(t, &registry, "RT-SEM-001")
	entry.Scope = append(entry.Scope, "hostde")
	if err := validateInvariantRegistry(registry); err == nil || !strings.Contains(err.Error(), "undeclared scope") {
		t.Fatalf("expected undeclared-scope failure, got %v", err)
	}
}

func TestInvariantRegistryRejectsDuplicateID(t *testing.T) {
	registry := currentInvariantRegistry(t)
	registry.Invariants = append(registry.Invariants, registry.Invariants[len(registry.Invariants)-1])
	if err := validateInvariantRegistry(registry); err == nil || !strings.Contains(err.Error(), "duplicate invariant id") {
		t.Fatalf("expected duplicate id failure, got %v", err)
	}
}

func TestInvariantRegistryAllowsWellFormedGrowth(t *testing.T) {
	registry := currentInvariantRegistry(t)
	registry.Invariants = append(registry.Invariants, invariantEntry{
		ID:             "RT-SEM-099",
		Status:         "active",
		Classification: "SEM",
		Statement:      "Synthetic future invariant used only to prove registry growth does not require rewriting foundation entries.",
		Scope:          []string{"project"},
		Enforcement: invariantEnforcement{
			Mode:       "review",
			Mechanisms: []string{"architecture review"},
		},
		Evidence: []string{"ADR-future"},
	})
	if err := validateInvariantRegistry(registry); err != nil {
		t.Fatalf("well-formed registry growth rejected: %v", err)
	}
}

func TestInvariantGovernanceIntegrationMarkers(t *testing.T) {
	checks := map[string][]string{
		"AGENTS.md": {
			"RUNETHREAD_INVARIANTS.json",
			"docs/runethread/INVARIANTS.md",
			"## Decision discipline",
			"agreement-seeking",
			"seek clarification",
		},
		".github/pull_request_template.md": {
			"## Invariant impact",
			"Active registry reviewed",
			"No active invariant is weakened silently",
		},
		".github/CODEOWNERS": {
			"/RUNETHREAD_INVARIANTS.json @Karageorgiou",
			"/docs/runethread/INVARIANTS.md @Karageorgiou",
			"/docs/adr/ADR-027-project-invariant-registry-and-decision-discipline.md @Karageorgiou",
			"/invariants_policy_test.go @Karageorgiou",
		},
		"docs/adr/README.md": {
			"[ADR-027](ADR-027-project-invariant-registry-and-decision-discipline.md)",
			"Project invariant registry and decision discipline",
		},
		"docs/runethread/INVARIANTS.md": {
			"Core `main`: `3da34da27183cf81a21379c91c9707f0ec54d261`",
			"public memory-template `main`: `61aea99f2b503c4da2b640a40ade588370303b0f`",
			"### Admitted to v1",
			"### Considered but not admitted",
			"Scope means applicability, not proof strength",
		},
	}
	for path, needles := range checks {
		data, err := os.ReadFile(path)
		if err != nil {
			t.Fatalf("read %s: %v", path, err)
		}
		text := string(data)
		for _, needle := range needles {
			if !strings.Contains(text, needle) {
				t.Errorf("%s missing invariant-governance marker %q", path, needle)
			}
		}
	}
}
