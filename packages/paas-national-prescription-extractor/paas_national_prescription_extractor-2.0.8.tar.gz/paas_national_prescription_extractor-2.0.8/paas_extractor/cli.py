#!/usr/bin/env python3
"""
Command Line Interface for Day Supply National
==============================================

Interactive prescription processing interface.
"""

import argparse
import json
import sys
from datetime import datetime

from .extractor import PrescriptionDataExtractor, PrescriptionInput


def format_result(result):
    """Format extraction result for display"""
    print(f"\n{'='*60}")
    print(f"PRESCRIPTION ANALYSIS RESULTS")
    print(f"{'='*60}")
    print(f"Original Drug Name: {result.original_drug_name}")
    print(f"Matched Drug Name:  {result.matched_drug_name}")
    print(
        f"Medication Type:    {result.medication_type.value.replace('_', ' ').title()}"
    )
    print(f"Match Confidence:   {result.confidence_score:.1%}")
    print(f"\n{'-'*40}")
    print(f"EXTRACTED PRESCRIPTION DATA:")
    print(f"{'-'*40}")
    print(f"Quantity:          {result.corrected_quantity}")
    print(f"Day Supply:        {result.calculated_day_supply} days")
    print(f"Standardized Sig:  {result.standardized_sig}")

    if result.warnings:
        print(f"\n{'⚠'*3} WARNINGS {'⚠'*3}")
        for i, warning in enumerate(result.warnings, 1):
            print(f"{i}. {warning}")

    if result.additional_info:
        print(f"\n{'ℹ'*3} ADDITIONAL INFORMATION {'ℹ'*3}")
        for key, value in result.additional_info.items():
            if value and key not in ["Drug_Name", "Proprietary_Name", "Brand_Name"]:
                print(f"{key.replace('_', ' ').title()}: {value}")


def save_results_to_file(results, filename=None):
    """Save results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prescription_results_{timestamp}.json"

    # Convert results to serializable format
    serializable_results = []
    for result in results:
        serializable_result = {
            "original_drug_name": result.original_drug_name,
            "matched_drug_name": result.matched_drug_name,
            "medication_type": result.medication_type.value,
            "corrected_quantity": result.corrected_quantity,
            "calculated_day_supply": result.calculated_day_supply,
            "standardized_sig": result.standardized_sig,
            "confidence_score": result.confidence_score,
            "warnings": result.warnings,
            "additional_info": result.additional_info,
            "timestamp": datetime.now().isoformat(),
        }
        serializable_results.append(serializable_result)

    with open(filename, "w") as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\nResults saved to: {filename}")


def main():
    """Main interface with argument parsing"""
    parser = argparse.ArgumentParser(
        description="PAAS National Prescription Data Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  paas-extractor                    # Interactive mode
  paas-extractor --help            # Show this help
  paas-extractor --version         # Show version
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="PAAS National Prescription Extractor v2.0.8",
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Exit immediately (for CI/CD environments)",
    )

    args = parser.parse_args()

    # Handle non-interactive mode (for CI/CD)
    if args.non_interactive:
        print("PAAS National Prescription Extractor v2.0.8")
        print("Non-interactive mode - exiting successfully")
        return

    # Check if running in non-interactive environment
    if not sys.stdin.isatty():
        print("PAAS National Prescription Extractor v2.0.8")
        print("Detected non-interactive environment - use --help for options")
        return

    print("=" * 60)
    print("PAAS NATIONAL - PRESCRIPTION DATA EXTRACTOR")
    print("Interactive Processing Interface")
    print("=" * 60)
    print("\nInitializing system...")

    extractor = PrescriptionDataExtractor()
    results = []

    print("System ready!")
    print("\nInstructions:")
    print("- Enter prescription details when prompted")
    print("- Type 'quit' or 'exit' to finish")
    print("- Type 'batch' to run predefined test cases")
    print("- Type 'help' for more options")

    while True:
        print("\n" + "-" * 60)
        choice = input(
            "\nChoose an option:\n1. Enter single prescription\n2. Run batch test\n3. View saved results\n4. Help\n5. Quit\n\nChoice (1-5): "
        ).strip()

        if choice in ["5", "quit", "exit", "q"]:
            break
        elif choice == "1":
            # Single prescription input
            print("\n📝 ENTER PRESCRIPTION DETAILS:")
            drug_name = input("Drug Name: ").strip()
            if not drug_name:
                print("❌ Drug name cannot be empty!")
                continue

            quantity = input("Quantity: ").strip()
            if not quantity:
                print("❌ Quantity cannot be empty!")
                continue

            sig = input("Sig/Directions: ").strip()
            if not sig:
                print("❌ Sig/Directions cannot be empty!")
                continue

            # Process prescription
            prescription = PrescriptionInput(drug_name, quantity, sig)
            result = extractor.extract_prescription_data(prescription)
            results.append(result)

            format_result(result)

        elif choice == "2":
            # Batch test
            print("\n🧪 RUNNING BATCH TEST CASES...")
            test_cases = [
                PrescriptionInput("Flonase", "1", "2 sprays each nostril twice daily"),
                PrescriptionInput(
                    "Albuterol HFA", "2", "2 puffs every 4-6 hours as needed"
                ),
                PrescriptionInput(
                    "Humalog KwikPen",
                    "5",
                    "take 15 units before meals three times daily",
                ),
                PrescriptionInput(
                    "Timolol 0.5% drops", "5", "1 drop in each eye twice daily"
                ),
                PrescriptionInput(
                    "Hydrocortisone 1% cream",
                    "30",
                    "apply to affected area twice daily",
                ),
                PrescriptionInput(
                    "Humira", "2", "inject 40mg subcutaneously every other week"
                ),
                PrescriptionInput(
                    "Ozempic", "1", "inject 0.5mg subcutaneously once weekly"
                ),
                PrescriptionInput("Lantus SoloStar", "3", "inject 25 units at bedtime"),
                PrescriptionInput(
                    "Ventolin HFA", "1", "2 puffs every 4 hours as needed"
                ),
                PrescriptionInput("Restasis", "2", "1 drop in each eye twice daily"),
            ]

            batch_results = extractor.batch_process(test_cases)
            results.extend(batch_results)

            for i, result in enumerate(batch_results, 1):
                print(f"\n{'='*20} TEST CASE {i} {'='*20}")
                format_result(result)

            print(f"\n✅ Completed {len(batch_results)} test cases!")

        elif choice == "3":
            # View results summary
            if not results:
                print("\n📊 No results to display yet.")
                continue

            print(f"\n📊 RESULTS SUMMARY ({len(results)} prescriptions processed)")
            print("-" * 80)
            print(
                f"{'#':<3} {'Drug Name':<25} {'Type':<15} {'Qty':<8} {'Days':<6} {'Confidence':<10}"
            )
            print("-" * 80)

            for i, result in enumerate(results, 1):
                drug_name = result.original_drug_name[:24]
                med_type = result.medication_type.value.replace("_", " ")[:14]
                qty = f"{result.corrected_quantity:.1f}"
                days = str(result.calculated_day_supply)
                conf = f"{result.confidence_score:.1%}"

                print(
                    f"{i:<3} {drug_name:<25} {med_type:<15} {qty:<8} {days:<6} {conf:<10}"
                )

            save_choice = input(f"\nSave results to file? (y/n): ").strip().lower()
            if save_choice in ["y", "yes"]:
                save_results_to_file(results)

        elif choice == "4":
            # Help
            print("\nHELP INFORMATION")
            print("-" * 40)
            print("This system processes prescription data and provides:")
            print("- Accurate quantity calculations")
            print("- Precise day supply estimates")
            print("- Standardized sig/directions")
            print("- Medication type identification")
            print("\nSupported medication types:")
            print("- Nasal inhalers (sprays)")
            print("- Oral inhalers (HFA, Diskus, etc.)")
            print("- Insulin products (vials, pens)")
            print("- Injectable medications")
            print("- Eye drops")
            print("- Topical medications")
            print("\nTips for best results:")
            print("- Use complete drug names when possible")
            print("- Include strength information")
            print("- Provide clear dosing instructions")

        else:
            print("Invalid choice. Please select 1-5.")

    if results:
        print(f"\nSESSION COMPLETE")
        print(f"Processed {len(results)} prescriptions total.")
        final_save = input("Save all results before exiting? (y/n): ").strip().lower()
        if final_save in ["y", "yes"]:
            save_results_to_file(results)

    print("\n👋 Thank you for using PAAS National!")


if __name__ == "__main__":
    main()
