#!/usr/bin/env python3
"""
Test Suite for Day Supply National
==================================

Comprehensive testing framework for the prescription data extraction system.
"""

from typing import Dict, List

import pandas as pd

from .extractor import PrescriptionDataExtractor, PrescriptionInput


class ComprehensiveTestSuite:
    """Comprehensive testing for all medications in the database"""

    def __init__(self):
        self.extractor = PrescriptionDataExtractor()
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "errors": [],
            "medication_types": {},
        }

    def generate_test_cases_nasal_inhalers(self) -> List[PrescriptionInput]:
        """Generate test cases for all nasal inhalers"""
        test_cases = []
        try:
            import pkg_resources

            data_path = pkg_resources.resource_filename(
                "day_supply_national", "data/nasal_inhalers.csv"
            )
            df = pd.read_csv(data_path)
        except Exception:
            return test_cases

        # Test different sig patterns for each drug
        sig_patterns = [
            "2 sprays each nostril twice daily",
            "1 spray per nostril once daily",
            "1 spray in each nostril bid",
            "use 2 sprays in each nostril q12h",
            "1-2 sprays per nostril as needed",
        ]

        for _, row in df.iterrows():
            drug_name = row["Drug_Name"]
            # Test with typical quantities
            for qty in [1, 2, 3]:
                sig = sig_patterns[qty % len(sig_patterns)]
                test_cases.append(PrescriptionInput(drug_name, str(qty), sig))

        return test_cases

    def generate_test_cases_oral_inhalers(self) -> List[PrescriptionInput]:
        """Generate test cases for all oral inhalers"""
        test_cases = []
        try:
            import pkg_resources

            data_path = pkg_resources.resource_filename(
                "day_supply_national", "data/oral_inhaler_products.csv"
            )
            df = pd.read_csv(data_path)
        except Exception:
            return test_cases

        sig_patterns = [
            "2 puffs every 4-6 hours as needed",
            "2 puffs q4h prn",
            "1 puff twice daily",
            "2 puffs bid",
            "inhale 2 puffs every 6 hours",
        ]

        for _, row in df.iterrows():
            drug_name = row["Brand_Name"]
            for qty in [1, 2]:
                sig = sig_patterns[qty % len(sig_patterns)]
                test_cases.append(PrescriptionInput(drug_name, str(qty), sig))

        return test_cases

    def generate_test_cases_insulin(self) -> List[PrescriptionInput]:
        """Generate test cases for all insulin products"""
        test_cases = []
        try:
            import pkg_resources

            data_path = pkg_resources.resource_filename(
                "day_supply_national", "data/insulin_products.csv"
            )
            df = pd.read_csv(data_path)
        except Exception:
            return test_cases

        sig_patterns = [
            "inject 10 units before meals three times daily",
            "15 units subcutaneously tid with meals",
            "inject 25 units at bedtime",
            "20 units qhs",
            "inject 30 units daily",
            "8-12 units before each meal",
        ]

        for _, row in df.iterrows():
            drug_name = row["Proprietary_Name"]
            dosage_form = row.get("Dosage_Form", "")

            # Add dosage form to drug name for better matching
            if dosage_form and dosage_form not in drug_name:
                full_name = f"{drug_name} {dosage_form}"
            else:
                full_name = drug_name

            for qty in [1, 3, 5]:
                sig = sig_patterns[qty % len(sig_patterns)]
                test_cases.append(PrescriptionInput(full_name, str(qty), sig))

        return test_cases

    def generate_edge_cases(self) -> List[PrescriptionInput]:
        """Generate edge cases and challenging scenarios"""
        edge_cases = [
            # Misspellings
            PrescriptionInput(
                "Fluonase", "1", "2 sprays each nostril bid"
            ),  # Flonase misspelled
            PrescriptionInput(
                "Albuteral", "1", "2 puffs q4h prn"
            ),  # Albuterol misspelled
            PrescriptionInput("Lantis", "3", "25 units qhs"),  # Lantus misspelled
            # Generic names - Insulin Products (testing Proper_Name alternatives)
            PrescriptionInput("insulin glargine", "5", "inject 30 units at bedtime"),  # Lantus generic
            PrescriptionInput("insulin lispro", "3", "15 units before meals"),  # Humalog generic
            PrescriptionInput("insulin aspart", "6", "8 units tid"),  # NovoLog generic
            PrescriptionInput("insulin detemir", "2", "20 units daily"),  # Levemir generic
            PrescriptionInput("insulin degludec", "3", "25 units daily"),  # Tresiba generic
            PrescriptionInput("regular insulin human", "1", "10 units qid"),  # Humulin R generic
            PrescriptionInput("insulin isophane human", "2", "15 units bid"),  # Humulin N generic
            PrescriptionInput("insulin glulisine", "4", "12 units tid"),  # Apidra generic
            
            # Generic names - Biologic Injectables (testing Proper_Name alternatives)
            PrescriptionInput("adalimumab", "2", "inject every other week"),  # Humira generic
            PrescriptionInput("etanercept", "4", "inject twice weekly"),  # Enbrel generic
            PrescriptionInput("infliximab", "1", "infuse every 8 weeks"),  # Remicade generic
            PrescriptionInput("rituximab", "2", "infuse monthly"),  # Rituxan generic
            PrescriptionInput("tocilizumab", "4", "inject weekly"),  # Actemra generic
            
            # Generic names - Non-biologic Injectables (testing Proper_Name alternatives)
            PrescriptionInput("aripiprazole ER injection", "1", "inject monthly"),  # Abilify Maintena generic
            PrescriptionInput("haloperidol decanoate", "1", "inject monthly"),  # Haldol Decanoate generic
            PrescriptionInput("fluphenazine decanoate", "2", "inject every 2 weeks"),  # Prolixin Decanoate generic
            
            # Analog names - Diabetic Injectables (testing Analog_Name alternatives)
            PrescriptionInput("lixisenatide", "1", "inject daily"),  # Adlyxin analog
            PrescriptionInput("exenatide", "1", "inject twice daily"),  # Byetta analog
            PrescriptionInput("exenatide extended release", "4", "inject weekly"),  # Bydureon analog
            PrescriptionInput("tirzepatide", "4", "inject weekly"),  # Mounjaro analog
            PrescriptionInput("semaglutide", "1", "inject weekly"),  # Ozempic analog
            PrescriptionInput("dulaglutide", "4", "inject weekly"),  # Trulicity analog
            PrescriptionInput("liraglutide", "2", "inject daily"),  # Victoza analog
            
            # Other generic names
            PrescriptionInput(
                "fluticasone nasal spray", "2", "2 sprays each nostril daily"
            ),
            # Unusual quantities
            PrescriptionInput(
                "Humira", "12", "inject every other week"
            ),  # High quantity
            PrescriptionInput(
                "Ventolin HFA", "0.5", "2 puffs prn"
            ),  # Fractional quantity
            PrescriptionInput(
                "Eye drops", "100", "1 drop ou bid"
            ),  # Very high quantity
            # Complex sigs
            PrescriptionInput(
                "Humalog", "5", "sliding scale: 8-12 units ac tid based on blood sugar"
            ),
            PrescriptionInput(
                "Albuterol HFA", "2", "2-4 puffs q4-6h prn sob/wheeze, max 12 puffs/day"
            ),
            # Missing or vague information
            PrescriptionInput("Inhaler", "1", "use as directed"),
            PrescriptionInput("Insulin", "5", "take as prescribed"),
            PrescriptionInput("Cream", "30", "apply"),
            # Mixed units
            PrescriptionInput(
                "Testosterone cypionate", "10ml", "inject 1ml every 2 weeks"
            ),
            PrescriptionInput("B12", "1000mcg", "inject monthly"),
        ]

        return edge_cases

    def run_test_batch(
        self, test_cases: List[PrescriptionInput], category: str
    ) -> Dict:
        """Run a batch of test cases and collect results"""
        results = {
            "category": category,
            "total": len(test_cases),
            "successful": 0,
            "warnings": 0,
            "errors": 0,
            "details": [],
        }

        print(f"\n{'='*80}")
        print(f"Testing {category}: {len(test_cases)} test cases")
        print(f"{'='*80}")

        for i, test_case in enumerate(test_cases):
            try:
                result = self.extractor.extract_prescription_data(test_case)

                # Check for issues
                has_error = False
                issues = []

                # Check confidence score
                if result.confidence_score < 0.5:
                    issues.append(f"Low confidence: {result.confidence_score:.2%}")

                # Check if day supply is reasonable
                if result.calculated_day_supply <= 0:
                    issues.append(f"Invalid day supply: {result.calculated_day_supply}")
                    has_error = True
                elif result.calculated_day_supply > 365:
                    issues.append(f"High day supply: {result.calculated_day_supply}")

                # Check if quantity is reasonable
                if result.corrected_quantity <= 0:
                    issues.append(f"Invalid quantity: {result.corrected_quantity}")
                    has_error = True

                # Check warnings (should be none in perfect version)
                if result.warnings:
                    results["warnings"] += 1
                    issues.extend([f"Unexpected Warning: {w}" for w in result.warnings])

                if has_error:
                    results["errors"] += 1
                else:
                    results["successful"] += 1

                # Store detailed result
                results["details"].append(
                    {
                        "input": {
                            "drug": test_case.drug_name,
                            "quantity": test_case.quantity,
                            "sig": test_case.sig_directions,
                        },
                        "output": {
                            "matched_drug": result.matched_drug_name,
                            "medication_type": result.medication_type.value,
                            "corrected_quantity": result.corrected_quantity,
                            "day_supply": result.calculated_day_supply,
                            "standardized_sig": result.standardized_sig,
                            "confidence": result.confidence_score,
                        },
                        "issues": issues,
                    }
                )

                # Print progress
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(test_cases)} tests...")

            except Exception as e:
                results["errors"] += 1
                results["details"].append(
                    {
                        "input": {
                            "drug": test_case.drug_name,
                            "quantity": test_case.quantity,
                            "sig": test_case.sig_directions,
                        },
                        "error": str(e),
                    }
                )
                print(f"  ERROR processing {test_case.drug_name}: {e}")

        # Print summary
        print(f"\n{category} Results:")
        print(f"  Successful: {results['successful']}")
        print(f"  Warnings: {results['warnings']}")
        print(f"  Errors: {results['errors']}")

        return results

    def run_all_tests(self):
        """Run all test categories"""
        print("\n" + "=" * 80)
        print("PAAS NATIONAL - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print("\nThis will test medications in the database...")

        all_results = []

        # Generate and run tests for each category
        test_categories = [
            ("Nasal Inhalers", self.generate_test_cases_nasal_inhalers()),
            ("Oral Inhalers", self.generate_test_cases_oral_inhalers()),
            ("Insulin Products", self.generate_test_cases_insulin()),
            ("Edge Cases", self.generate_edge_cases()),
        ]

        for category_name, test_cases in test_categories:
            if test_cases:  # Only run if we have test cases
                results = self.run_test_batch(test_cases, category_name)
                all_results.append(results)
                self.test_results["medication_types"][category_name] = results

        # Calculate totals
        self.test_results["total_tests"] = sum(r["total"] for r in all_results)
        self.test_results["passed"] = sum(r["successful"] for r in all_results)
        self.test_results["warnings"] = sum(r["warnings"] for r in all_results)
        self.test_results["failed"] = sum(r["errors"] for r in all_results)

        # Print final summary
        self.print_summary()

        return self.test_results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("FINAL TEST SUMMARY")
        print("=" * 80)

        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        warnings = self.test_results["warnings"]
        failed = self.test_results["failed"]

        if total > 0:
            print(f"\nTotal Tests Run: {total}")
            print(f"Passed: {passed} ({passed/total*100:.1f}%)")
            print(f"Warnings: {warnings} ({warnings/total*100:.1f}%)")
            print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        else:
            print("\nNo tests were run.")

        print("\nResults by Category:")
        for category, results in self.test_results["medication_types"].items():
            print(f"\n{category}:")
            print(f"  Total: {results['total']}")
            if results["total"] > 0:
                print(
                    f"  Success Rate: {results['successful']/results['total']*100:.1f}%"
                )
                if results["errors"] > 0:
                    print(f"  Errors: {results['errors']}")


def main():
    """Run the comprehensive test suite"""
    # Run tests
    suite = ComprehensiveTestSuite()
    results = suite.run_all_tests()

    # Provide recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if results["failed"] > 0:
        print("\nSome tests failed. Review the results for details.")
        print("Common issues to check:")
        print("- Drug names not in database")
        print("- Unusual dosing patterns")
        print("- Edge cases that need special handling")
    else:
        print("\nAll tests passed successfully!")

    if results["warnings"] > 0:
        print(f"\n{results['warnings']} warnings detected")
        print("Review warnings to ensure they are expected")


if __name__ == "__main__":
    main()
