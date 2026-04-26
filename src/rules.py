from typing import List, Dict

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}

class ManufacturabilityRules:
    def __init__(self, min_wall_mm=2.0, max_overhang_deg=45.0, min_radius_mm=1.0):
        self.min_wall_mm = min_wall_mm
        self.max_overhang_deg = max_overhang_deg
        self.min_radius_mm = min_radius_mm

    def apply(self, issues: List[Dict]) -> List[Dict]:
        issues = self._deduplicate(issues)
        issues.sort(key=lambda x: SEVERITY_ORDER.get(x['severity'], 9))
        return issues

    def _deduplicate(self, issues: List[Dict], threshold=5.0) -> List[Dict]:
        seen = []
        for issue in issues:
            loc = issue['location']
            duplicate = False
            for s in seen:
                if s['issue_type'] == issue['issue_type']:
                    d = sum((a - b) ** 2 for a, b in zip(loc, s['location'])) ** 0.5
                    if d < threshold:
                        duplicate = True
                        break
            if not duplicate:
                seen.append(issue)
        return seen
