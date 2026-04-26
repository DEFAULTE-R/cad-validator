import json
from pathlib import Path
from typing import Dict

ICONS = {"critical": "🔴", "warning": "🟡", "info": "🔵"}

class Reporter:
    @staticmethod
    def save_json(results: Dict, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"✅ Report saved → {output_path}")

    @staticmethod
    def print_summary(results: Dict):
        print("\n" + "=" * 55)
        print(f"  CAD VALIDATION REPORT")
        print(f"  File: {results['file']}")
        print("=" * 55)
        print(f"  Total issues : {results['total_issues']}")
        print(f"  🔴 Critical  : {results['critical']}")
        print(f"  🟡 Warnings  : {results['warnings']}")
        print("=" * 55)

        if not results['issues']:
            print("\n  ✅ No manufacturability issues found!")
        else:
            for i, issue in enumerate(results['issues'], 1):
                icon = ICONS.get(issue['severity'], '•')
                print(f"\n  {i}. {icon} {issue['issue_type'].upper().replace('_', ' ')}")
                print(f"     Severity : {issue['severity']}")
                print(f"     Location : {issue['location']}")
                for k, v in issue.items():
                    if k not in ('issue_type', 'severity', 'location', 'fix'):
                        print(f"     {k.replace('_', ' ').title()} : {v}")
                print(f"     Fix      : {issue['fix']}")

        print("\n" + "=" * 55 + "\n")
