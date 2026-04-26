import cadquery as cq
from pathlib import Path
from typing import Dict, Optional
from .geometry import analyze_overhangs, analyze_thin_walls, analyze_sharp_edges
from .rules import ManufacturabilityRules
from .reporter import Reporter


class CADValidator:
    def __init__(
        self,
        min_wall_mm: float = 2.0,
        max_overhang_deg: float = 45.0,
        min_radius_mm: float = 1.0,
    ):
        self.min_wall_mm = min_wall_mm
        self.max_overhang_deg = max_overhang_deg
        self.min_radius_mm = min_radius_mm
        self.rules = ManufacturabilityRules(min_wall_mm, max_overhang_deg, min_radius_mm)

    def validate(self, step_file: str) -> Dict:
        path = Path(step_file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {step_file}")

        print(f"[Validator] Loading {path.name}...")
        shape = cq.importers.importStep(str(path))
        print(f"[Validator] Running geometry analysis...")

        all_issues = []
        all_issues += analyze_overhangs(shape, self.max_overhang_deg)
        all_issues += analyze_thin_walls(shape, self.min_wall_mm)
        all_issues += analyze_sharp_edges(shape, self.min_radius_mm)

        issues = self.rules.apply(all_issues)

        results = {
            "file": str(path),
            "total_issues": len(issues),
            "critical": len([i for i in issues if i['severity'] == 'critical']),
            "warnings": len([i for i in issues if i['severity'] == 'warning']),
            "settings": {
                "min_wall_mm": self.min_wall_mm,
                "max_overhang_deg": self.max_overhang_deg,
                "min_radius_mm": self.min_radius_mm,
            },
            "issues": issues
        }

        return results

    def validate_and_report(
        self,
        step_file: str,
        output_json: Optional[str] = None,
        print_summary: bool = True,
    ) -> Dict:
        results = self.validate(step_file)

        if print_summary:
            Reporter.print_summary(results)

        if output_json:
            Reporter.save_json(results, output_json)

        return results


# ── CLI ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CAD Design Validator")
    parser.add_argument("step_file", help="Path to STEP file")
    parser.add_argument("--output-json", default="report.json", help="JSON report output path")
    parser.add_argument("--min-wall", type=float, default=2.0, help="Min wall thickness in mm")
    parser.add_argument("--max-overhang", type=float, default=45.0, help="Max overhang angle in degrees")
    parser.add_argument("--min-radius", type=float, default=1.0, help="Min edge radius in mm")
    args = parser.parse_args()

    v = CADValidator(args.min_wall, args.max_overhang, args.min_radius)
    v.validate_and_report(args.step_file, output_json=args.output_json)
