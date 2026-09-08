package runethread

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"regexp"
	"sort"
	"strings"
	"testing"
)

const invariantRegistryPath = "RUNETHREAD_INVARIANTS.json"

var invariantIDPattern = regexp.MustCompile(`^RT-([A-Z]+)-([0-9]{3})$`)

var foundationInvariantStatements = map[string]string{
	"RT-ARCH-001": "Core remains provider-neutral; provider-specific hosted and integration dependencies, credentials, and execution authority live outside Core.",
	"RT-ARCH-002": "Correctness-relevant behavior crosses component boundaries through explicit versioned contracts or immutable identities, not through unversioned internal implementation coupling.",
	"RT-DATA-001": "The user-owned Git repository is canonical durable semantic memory state; derived indexes, caches, and project-orientation views are not sole semantic authority.",
	"RT-GOV-001":  "Material recommendations and changes are evaluated against the actual project objective, evidence, costs, simpler alternatives, and accepted constraints; unresolved material ambiguity is surfaced rather than silently assumed.",
	"RT-REL-001":  "Released or hosted execution is bound to explicit immutable verified component, contract, and protocol identities and does not execute floating development branches as production authority.",
	"RT-SEM-001":  "Canonical memory mutation semantics have one implementation authority in Core; other components may invoke or independently replay those Core-owned semantics but must not create a second semantic implementation.",
}

type invariantRegistry struct {
	FormatVersion   int               `json:"format_version"`
	Authority       invariantAuthority `json:"authority"`
	Classifications map[string]string `json:"classifications"`
	Invariants      []invariantEntry  `json:"invariants"`
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
	if decoder.More() {
		return invariantRegistry{}, errors.New("decode invariant registry: trailing JSON values")
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
		if !regexp.MustCompile(`^[A-Z]+$`).MatchString(prefix) {
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

	for id, statement := range foundationInvariantStatements {
		entry, ok := seen[id]
		if !ok {
			return fmt.Errorf("foundation invariant %s is missing", id)
		}
		if entry.Statement != statement {
			return fmt.Errorf("foundation invariant %s statement drift", id)
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

func TestInvariantRegistryPolicy(t *testing.T) {
	registry := currentInvariantRegistry(t)
	if err := validateInvariantRegistry(registry); err != nil {
		t.Fatal(err)
	}
}

func TestInvariantRegistryRejectsFoundationStatementDrift(t *testing.T) {
	registry := currentInvariantRegistry(t)
	for i := range registry.Invariants {
		if registry.Invariants[i].ID == "RT-SEM-001" {
			registry.Invariants[i].Statement = "Hosted may implement equivalent semantics independently."
			if err := validateInvariantRegistry(registry); err == nil || !strings.Contains(err.Error(), "statement drift") {
				t.Fatalf("expected foundation statement drift failure, got %v", err)
			}
			return
		}
	}
	t.Fatal("RT-SEM-001 missing from test fixture")
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
		Statement:      "Synthetic future invariant used only to prove registry growth does not require rewriting foundation statements.",
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
